#!/usr/bin/env python3
"""
Debug do banco de dados
"""

import sqlite3
import pandas as pd
from pathlib import Path


def debug_database():
    print("=== DEBUG DO BANCO DE DADOS ===\n")

    # 1. Verificar se o banco existe
    db_path = Path("data/resumo.bd")
    print(f"1. 📁 Caminho do banco: {db_path.absolute()}")
    print(f"   ✅ Existe: {db_path.exists()}")

    if not db_path.exists():
        print("   ❌ Banco não encontrado! Execute o ETL primeiro.")
        return False

    # 2. Verificar tamanho do banco
    print(f"   📊 Tamanho: {db_path.stat().st_size} bytes")

    # 3. Conectar e verificar tabelas
    try:
        conn = sqlite3.connect(str(db_path))
        print("2. ✅ Conexão com o banco bem-sucedida!")

        # Verificar tabelas
        tabelas = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
        print(f"3. 📊 Tabelas no banco: {list(tabelas['name'])}")

        # Verificar dados da tabela resumo_mensal
        if 'resumo_mensal' in tabelas['name'].values:
            # Estrutura da tabela
            estrutura = pd.read_sql_query("PRAGMA table_info(resumo_mensal);", conn)
            print("4. 🏗️ Estrutura da tabela resumo_mensal:")
            for _, row in estrutura.iterrows():
                print(f"   - {row['name']} ({row['type']})")

            # Contar registros
            count = pd.read_sql_query("SELECT COUNT(*) as total FROM resumo_mensal;", conn)
            print(f"5. 🔢 Total de registros: {count['total'].iloc[0]}")

            # Primeiros registros
            print("6. 📋 Primeiros 3 registros:")
            dados = pd.read_sql_query("SELECT * FROM resumo_mensal LIMIT 3;", conn)
            print(dados.to_string(index=False))

        else:
            print("❌ Tabela 'resumo_mensal' não encontrada!")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"💥 Erro ao acessar o banco: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_database()