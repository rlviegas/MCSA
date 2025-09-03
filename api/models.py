from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ResumoBase(BaseModel):
    mes_ano: str = Field(..., description="Período no formato YYYY-MM")
    credor: str = Field(..., description="Nome do credor")
    status_titulo: str = Field(..., description="Status do título")
    quantidade: int = Field(..., description="Quantidade de registros")
    valor_total: float = Field(..., description="Valor total")
    valor_medio: float = Field(..., description="Valor médio")


class ResumoResponse(BaseModel):
    # ✅ REMOVER o campo 'id' que não existe no banco
    mes_ano: str = Field(..., description="Período no formato YYYY-MM")
    credor: str = Field(..., description="Nome do credor")
    status_titulo: str = Field(..., description="Status do título")
    quantidade: int = Field(..., description="Quantidade de registros")
    valor_total: float = Field(..., description="Valor total")
    valor_medio: float = Field(..., description="Valor médio")

    class Config:
        from_attributes = True


class FiltrosResumo(BaseModel):
    credor: Optional[str] = Field(None, description="Filtrar por credor")
    status: Optional[str] = Field(None, description="Filtrar por status")
    mes_ano: Optional[str] = Field(None, description="Filtrar por mês-ano (YYYY-MM)")
    page: int = Field(1, ge=1, description="Número da página")
    limit: int = Field(10, ge=1, le=100, description="Limite de registros por página")


class ResumoPaginado(BaseModel):
    data: List[ResumoResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class HealthCheck(BaseModel):
    status: str = "OK"
    version: str = "1.0.0"
    database: bool = False