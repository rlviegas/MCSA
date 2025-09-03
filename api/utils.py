import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    try:
        # ✅ CORREÇÃO DEFINITIVA DO CAMINHO
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        db_path = os.path.join(project_root, "data", "resumo.bd")

        print(f"🔍 Tentando conectar em: {db_path}")
        print(f"📁 Arquivo existe: {os.path.exists(db_path)}")

        if not os.path.exists(db_path):
            # Listar arquivos na pasta data para debug
            data_dir = os.path.join(project_root, "data")
            if os.path.exists(data_dir):
                files = os.listdir(data_dir)
                print(f"📂 Arquivos em data/: {files}")
            raise FileNotFoundError(f"Banco de dados não encontrado: {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print("✅ Conexão bem-sucedida!")
        return conn

    except Exception as e:
        print(f"💥 Erro na conexão: {e}")
        import traceback
        traceback.print_exc()
        raise


def query_resumo(
        credor: Optional[str] = None,
        status: Optional[str] = None,
        mes_ano: Optional[str] = None,
        page: int = 1,
        limit: int = 10
) -> Dict[str, Any]:
    """
    Consulta o resumo do banco de dados com filtros e paginação
    """
    try:
        print(f"🔍 Iniciando query_resumo com filtros: credor={credor}, status={status}, mes_ano={mes_ano}")

        conn = get_db_connection()

        # ✅ CORREÇÃO: Usar as colunas exatas do banco
        query = "SELECT MES_ANO, CREDOR, STATUS_TITULO, QUANTIDADE, VALOR_TOTAL, VALOR_MEDIO FROM resumo_mensal WHERE 1=1"
        count_query = "SELECT COUNT(*) as total FROM resumo_mensal WHERE 1=1"
        params = []

        # Aplicar filtros
        if credor:
            query += " AND CREDOR LIKE ?"
            count_query += " AND CREDOR LIKE ?"
            params.append(f"%{credor}%")

        if status:
            query += " AND STATUS_TITULO LIKE ?"
            count_query += " AND STATUS_TITULO LIKE ?"
            params.append(f"%{status}%")

        if mes_ano:
            query += " AND MES_ANO = ?"
            count_query += " AND MES_ANO = ?"
            params.append(mes_ano)

        # Ordenação
        query += " ORDER BY MES_ANO, CREDOR, STATUS_TITULO"

        # Paginação
        offset = (page - 1) * limit
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        print(f"📝 Query: {query}")
        print(f"📋 Parâmetros: {params}")

        # Executar queries
        cursor = conn.execute(query, params)

        # ✅ Converter para dicionário com nomes de campos corretos
        resultados = []
        for row in cursor.fetchall():
            resultados.append({
                "mes_ano": row["MES_ANO"],
                "credor": row["CREDOR"],
                "status_titulo": row["STATUS_TITULO"],
                "quantidade": row["QUANTIDADE"],
                "valor_total": row["VALOR_TOTAL"],
                "valor_medio": row["VALOR_MEDIO"]
            })

        print(f"📊 Resultados encontrados: {len(resultados)}")

        # Contar total de registros (sem paginação)
        cursor_count = conn.execute(count_query, params[:-2])  # Remove LIMIT e OFFSET
        total = cursor_count.fetchone()['total']

        conn.close()

        return {
            "data": resultados,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        print(f"💥 Erro fatal em query_resumo: {e}")
        import traceback
        traceback.print_exc()
        raise


def get_resumo_aggregations() -> Dict[str, Any]:
    """Retorna agregações totais do resumo"""
    try:
        conn = get_db_connection()

        # Total por status
        status_query = """
        SELECT STATUS_TITULO, SUM(QUANTIDADE) as total_registros, SUM(VALOR_TOTAL) as total_valor
        FROM resumo_mensal 
        GROUP BY STATUS_TITULO
        """
        status_data = pd.read_sql_query(status_query, conn)

        # Total por credor
        credor_query = """
        SELECT CREDOR, SUM(QUANTIDADE) as total_registros, SUM(VALOR_TOTAL) as total_valor
        FROM resumo_mensal 
        GROUP BY CREDOR
        """
        credor_data = pd.read_sql_query(credor_query, conn)

        # Totais gerais
        total_query = """
        SELECT 
            SUM(QUANTIDADE) as total_registros,
            SUM(VALOR_TOTAL) as total_valor,
            COUNT(DISTINCT MES_ANO) as total_meses,
            COUNT(DISTINCT CREDOR) as total_credores
        FROM resumo_mensal
        """
        totais = pd.read_sql_query(total_query, conn).iloc[0].to_dict()

        conn.close()

        return {
            "por_status": status_data.to_dict('records'),
            "por_credor": credor_data.to_dict('records'),
            "totais_gerais": totais
        }

    except Exception as e:
        logger.error(f"Erro ao obter agregações: {str(e)}")
        raise


def check_database_health() -> bool:
    """Verifica se o banco de dados está acessível"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1 FROM resumo_mensal LIMIT 1")
        conn.close()
        return True
    except:
        return False