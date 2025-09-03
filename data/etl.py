import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import logging
from pathlib import Path
import re

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ETLProcessor:
    def __init__(self):
        self.input_file = 'dados_cobranca_formatado.csv'
        self.output_db = 'resumo.bd'
        self.output_csv = 'resumo_mensal.csv'

    def parse_valor_brasileiro(self, valor_str):
        """Converte valor no formato brasileiro para float"""
        if pd.isna(valor_str) or str(valor_str).strip().lower() in ("", "null"):
            return 0.0

        valor_str = str(valor_str).strip()

        # Remover símbolos e espaços
        valor_str = re.sub(r'[^\d,.-]', '', valor_str)

        # Caso: "1.200,50" -> "1200.50"
        if '.' in valor_str and ',' in valor_str:
            # Verificar se o ponto é separador de milhar
            if valor_str.find('.') < valor_str.find(','):
                valor_str = valor_str.replace('.', '').replace(',', '.')
            else:
                valor_str = valor_str.replace(',', '')
        # Caso: "1.200" (milhar) -> "1200"
        elif re.match(r'^\d+\.\d{3}$', valor_str):
            valor_str = valor_str.replace('.', '')
        # Caso: "1000,50" -> "1000.50"
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')

        try:
            return float(valor_str)
        except ValueError:
            return 0.0

    def extract_data(self):
        """Extrai dados do CSV formatado"""
        try:
            logger.info("Extraindo dados do arquivo CSV...")
            df = pd.read_csv(self.input_file)

            # Converter VALOR de string brasileira para float
            df['VALOR'] = df['VALOR'].apply(self.parse_valor_brasileiro)

            logger.info(f"Dados extraídos com sucesso. Shape: {df.shape}")
            return df
        except FileNotFoundError:
            logger.error(f"Arquivo {self.input_file} não encontrado")
            raise
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {str(e)}")
            raise

    def transform_data(self, df):
        """Transforma os dados e cria resumo mensal"""
        try:
            logger.info("Iniciando transformação dos dados...")

            # Verificar se as colunas necessárias existem
            required_columns = ['CREDOR', 'STATUS_TITULO', 'VALOR', 'DATA_CADASTRO']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Colunas ausentes no DataFrame: {missing_columns}")

            # Converter coluna de data para agrupamento mensal
            df['DATA_CADASTRO'] = pd.to_datetime(df['DATA_CADASTRO'], errors='coerce')

            # Remover registros com data inválida
            df = df.dropna(subset=['DATA_CADASTRO'])

            # Criar coluna MES_ANO para agrupamento
            df['MES_ANO'] = df['DATA_CADASTRO'].dt.to_period('M')

            # Remover valores NaN nas colunas de agrupamento
            df_clean = df.dropna(subset=['CREDOR', 'STATUS_TITULO', 'VALOR'])

            # Criar resumo mensal agrupado por CREDOR e STATUS_TITULO
            logger.info("Criando resumo mensal agrupado...")
            resumo = df_clean.groupby(['MES_ANO', 'CREDOR', 'STATUS_TITULO']).agg(
                QUANTIDADE=('VALOR', 'count'),
                VALOR_TOTAL=('VALOR', 'sum'),
                VALOR_MEDIO=('VALOR', 'mean')
            ).reset_index()

            # Converter MES_ANO para string para melhor armazenamento
            resumo['MES_ANO'] = resumo['MES_ANO'].astype(str)

            # Arredondar valores
            resumo['VALOR_TOTAL'] = resumo['VALOR_TOTAL'].round(2)
            resumo['VALOR_MEDIO'] = resumo['VALOR_MEDIO'].round(2)

            logger.info(f"Resumo criado com sucesso. Shape: {resumo.shape}")
            return resumo

        except Exception as e:
            logger.error(f"Erro na transformação: {str(e)}")
            raise

    def load_to_database(self, df_resumo):
        """Carrega o resumo para SQLite"""
        try:
            logger.info("Conectando ao banco SQLite...")

            # Garantir que o diretório existe
            Path('data').mkdir(exist_ok=True)

            conn = sqlite3.connect(self.output_db)

            # Criar tabela se não existir
            create_table_query = """
            CREATE TABLE IF NOT EXISTS resumo_mensal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                MES_ANO TEXT,
                CREDOR TEXT,
                STATUS_TITULO TEXT,
                QUANTIDADE INTEGER,
                VALOR_TOTAL REAL,
                VALOR_MEDIO REAL,
                DATA_CRIACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            conn.execute(create_table_query)
            conn.commit()

            # Inserir dados
            logger.info("Inserindo dados no banco...")
            df_resumo.to_sql('resumo_mensal', conn, if_exists='replace', index=False)

            conn.commit()
            conn.close()
            logger.info("Dados carregados no banco SQLite com sucesso")

        except Exception as e:
            logger.error(f"Erro ao carregar no banco: {str(e)}")
            raise

    def load_to_csv(self, df_resumo):
        """Salva o resumo em CSV (formato brasileiro)"""
        try:
            logger.info("Salvando resumo em CSV...")

            # Garantir que o diretório existe
            Path('data').mkdir(exist_ok=True)

            # Converter valores para formato brasileiro
            df_export = df_resumo.copy()
            df_export['VALOR_TOTAL'] = df_export['VALOR_TOTAL'].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            df_export['VALOR_MEDIO'] = df_export['VALOR_MEDIO'].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            df_export.to_csv(self.output_csv, index=False, encoding='utf-8')
            logger.info(f"Resumo salvo em: {self.output_csv}")
        except Exception as e:
            logger.error(f"Erro ao salvar CSV: {str(e)}")
            raise

    def run_etl(self):
        """Executa todo o processo ETL"""
        try:
            logger.info("Iniciando processo ETL...")

            # Extract
            df = self.extract_data()

            # Transform
            df_resumo = self.transform_data(df)

            # Load
            self.load_to_database(df_resumo)
            self.load_to_csv(df_resumo)

            logger.info("Processo ETL concluído com sucesso!")
            return df_resumo

        except Exception as e:
            logger.error(f"Erro no processo ETL: {str(e)}")
            return None


def query_resumo(mes_ano=None, credor=None, status=None):
    """Consulta o resumo do banco de dados"""
    try:
        # Usar caminho absoluto para garantir que encontra o banco
        db_path = Path('resumo.bd').absolute()

        if not db_path.exists():
            logger.error(f"Banco de dados não encontrado: {db_path}")
            return pd.DataFrame()

        conn = sqlite3.connect(str(db_path))

        query = "SELECT * FROM resumo_mensal WHERE 1=1"
        params = []

        if mes_ano:
            query += " AND MES_ANO = ?"
            params.append(str(mes_ano))

        if credor:
            query += " AND CREDOR LIKE ?"
            params.append(f"%{credor}%")

        if status:
            query += " AND STATUS_TITULO LIKE ?"
            params.append(f"%{status}%")

        query += " ORDER BY MES_ANO, CREDOR, STATUS_TITULO"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        logger.info(f"Consulta retornou {len(df)} registros")
        return df

    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        return pd.DataFrame()


# Executar ETL se o script for rodado diretamente
if __name__ == "__main__":
    etl = ETLProcessor()
    resultado = etl.run_etl()

    if resultado is not None:
        print("\nResumo criado com sucesso!")
        print("Primeiras linhas do resumo:")
        print(resultado.head())

        # Exemplo de consulta
        print("\nExemplo de consulta do banco:")
        df_consulta = query_resumo()
        if not df_consulta.empty:
            print(df_consulta.head())
        else:
            print("Nenhum dado encontrado na consulta")

        # Verificar arquivos gerados
        print("\nArquivos gerados:")
        for file in ['resumo.bd', 'resumo_mensal.csv']:
            file_path = Path(file)
            if file_path.exists():
                print(f"✓ {file} ({file_path.stat().st_size} bytes)")
            else:
                print(f"✗ {file} (não encontrado)")
    else:
        print("Falha no processo ETL")