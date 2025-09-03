import sqlite3
import pandas as pd
from pathlib import Path


def test_database():
    try:
        db_path = Path("data/resumo.bd")
        print(f"📁 Caminho do banco: {db_path.absolute()}")
        print(f"✅ Banco existe: {db_path.exists()}")

        if db_path.exists():
            conn = sqlite3.connect(str(db_path))

            # Verificar tabelas
            tabelas = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            print("📊 Tabelas no banco:", list(tabelas['name']))

            # Verificar dados na tabela resumo_mensal
            if 'resumo_mensal' in tabelas['name'].values:
                dados = pd.read_sql_query("SELECT * FROM resumo_mensal LIMIT 5;", conn)
                print("📋 Primeiros registros:")
                print(dados)

                total = pd.read_sql_query("SELECT COUNT(*) as total FROM resumo_mensal;", conn)
                print(f"🔢 Total de registros: {total['total'].iloc[0]}")
            else:
                print("❌ Tabela 'resumo_mensal' não encontrada!")

            conn.close()
        else:
            print("❌ Arquivo do banco não encontrado!")

    except Exception as e:
        print(f"💥 Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_database()