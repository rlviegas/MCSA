from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from .models import (
    ResumoResponse,
    FiltrosResumo,
    ResumoPaginado,
    HealthCheck
)
from .utils import query_resumo, get_resumo_aggregations, check_database_health

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Resumo de Cobranças",
    description="API para consulta de resumos mensais de cobranças",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "API de Resumo de Cobranças - Use /docs para ver a documentação"}


@app.get("/health", response_model=HealthCheck, tags=["Health Check"])
async def health_check():
    """Endpoint de health check da API"""
    db_healthy = check_database_health()
    return HealthCheck(
        status="OK" if db_healthy else "WARNING",
        database=db_healthy
    )


@app.get("/resumo", response_model=ResumoPaginado, tags=["Resumo"])
async def get_resumo(
        credor: Optional[str] = Query(None, description="Filtrar por nome do credor"),
        status: Optional[str] = Query(None, description="Filtrar por status do título"),
        mes_ano: Optional[str] = Query(None, description="Filtrar por mês-ano (formato: YYYY-MM)"),
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Limite de registros por página")
):
    """
    Retorna o resumo mensal de cobranças com opções de filtro e paginação.

    - **credor**: Filtra por nome do credor (case-insensitive)
    - **status**: Filtra por status do título (Pago, Pendente, Vencido)
    - **mes_ano**: Filtra por mês e ano (formato: YYYY-MM)
    - **page**: Número da página para paginação
    - **limit**: Quantidade de registros por página
    """
    try:
        # Validar formato do mes_ano se fornecido
        if mes_ano:
            if len(mes_ano) != 7 or mes_ano[4] != '-':
                raise HTTPException(
                    status_code=400,
                    detail="Formato de mês-ano inválido. Use YYYY-MM"
                )

        resultado = query_resumo(credor, status, mes_ano, page, limit)

        return ResumoPaginado(
            data=resultado["data"],
            total=resultado["total"],
            page=resultado["page"],
            limit=resultado["limit"],
            total_pages=resultado["total_pages"]
        )

    except FileNotFoundError as e:
        logger.error(f"Banco de dados não encontrado: {e}")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados não disponível. Execute o ETL primeiro."
        )
    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@app.get("/resumo/aggregations", tags=["Resumo"])
async def get_resumo_aggregations():
    """
    Retorna agregações e estatísticas do resumo.

    Inclui totais por status, por credor e estatísticas gerais.
    """
    try:
        aggregations = get_resumo_aggregations()
        return aggregations

    except Exception as e:
        logger.error(f"Erro ao obter agregações: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar agregações")


@app.get("/resumo/meses", tags=["Resumo"])
async def get_meses_disponiveis():
    """
    Retorna lista de meses disponíveis no resumo.
    """
    try:
        from .utils import get_db_connection
        conn = get_db_connection()

        query = "SELECT DISTINCT MES_ANO FROM resumo_mensal ORDER BY MES_ANO DESC"
        meses = [row['MES_ANO'] for row in conn.execute(query).fetchall()]

        conn.close()
        return {"meses": meses}

    except Exception as e:
        logger.error(f"Erro ao obter meses: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter meses disponíveis")


@app.get("/resumo/credores", tags=["Resumo"])
async def get_credores_disponiveis():
    """
    Retorna lista de credores disponíveis no resumo.
    """
    try:
        from .utils import get_db_connection
        conn = get_db_connection()

        query = "SELECT DISTINCT CREDOR FROM resumo_mensal ORDER BY CREDOR"
        credores = [row['CREDOR'] for row in conn.execute(query).fetchall()]

        conn.close()
        return {"credores": credores}

    except Exception as e:
        logger.error(f"Erro ao obter credores: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter credores disponíveis")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)