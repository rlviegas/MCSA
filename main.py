#!/usr/bin/env python3
"""
Script principal para executar o pipeline completo de ETL
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path):
    """Executa um script Python"""
    try:
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {script_path} executado com sucesso")
            return True
        else:
            print(f"✗ Erro em {script_path}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Erro ao executar {script_path}: {e}")
        return False


def main():
    print("Iniciando pipeline ETL...")

    # 1. Primeiro processar o CSV original
    print("\n1. Processando CSV original...")
    processador_path = Path("data/processador_csv.py")

    if processador_path.exists():
        success = run_script(str(processador_path))
        if not success:
            print("Erro no processamento do CSV. Abortando.")
            return
    else:
        print("✓ Arquivo formatado já existe, pulando processamento...")

    # 2. Executar ETL
    print("\n2. Executando ETL...")
    etl_path = Path("data/etl.py")
    success = run_script(str(etl_path))

    if success:
        print("\n✓ Pipeline concluído com sucesso!")
        print("Arquivos gerados:")
        print("  - data/dados_cobranca_formatado.csv")
        print("  - data/resumo_mensal.csv")
        print("  - data/resumo.bd (SQLite)")
    else:
        print("\n✗ Pipeline falhou.")


if __name__ == "__main__":
    main()