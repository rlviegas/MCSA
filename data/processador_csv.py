import pandas as pd
from pathlib import Path
import re

def processar_csv():
    # ------------------------
    # 1. LER E RECONSTRUIR O CSV
    # ------------------------
    # ✅ CORRIGIDO: Adicionar "data/" no caminho
    csv_path = Path("dados_cobranca.csv")

    # Verificar se o arquivo existe
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path.absolute()}")

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    reconstructed_data = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Corrigir header
        if i == 0:
            if 'C#EDOR' in line:
                line = line.replace('C#EDOR', 'CREDOR')
            reconstructed_data.append(
                ['CREDOR', 'CAMPANHA', 'CLIENTE', 'DATA_CADASTRO', 'DATA_PAGAMENTO', 'STATUS_TITULO', 'VALOR']
            )
            continue

        # Corrigir casos tipo "2,500.50" → "2500.50"
        line = re.sub(r'(\d),(\d{3}\.\d+)', r'\1\2', line)

        # Substituir delimitadores inconsistentes
        line = line.replace(',', ';')
        parts = line.split(';')

        if len(parts) >= 6:
            credor = parts[0].strip().lower()
            campanha = parts[1].strip().lower()
            cliente = parts[2].strip()
            data_cadastro = parts[3].strip()
            data_pagamento = parts[4].strip() if len(parts) > 4 else ''
            status_titulo = parts[5].strip().lower() if len(parts) > 5 else ''
            valor = parts[6].strip() if len(parts) > 6 else ''

            reconstructed_data.append(
                [credor, campanha, cliente, data_cadastro, data_pagamento, status_titulo, valor]
            )

    # Criar DataFrame
    df = pd.DataFrame(reconstructed_data[1:], columns=reconstructed_data[0])

    # ------------------------
    # 2. FUNÇÕES DE FORMATAÇÃO
    # ------------------------
    def formatar_credor(credor):
        if pd.isna(credor) or str(credor).strip() == '':
            return 'Credor Desconhecido'
        return str(credor).strip().title()

    def formatar_campanha(campanha):
        if pd.isna(campanha) or str(campanha).strip() == '':
            return 'Campanha 1'
        campanha = str(campanha).strip().lower()
        numeros = re.findall(r'\d+', campanha)
        if numeros:
            return f'Campanha {numeros[0]}'
        return campanha.title()

    def formatar_cliente(cliente):
        if pd.isna(cliente) or str(cliente).strip() == '':
            return 'Cliente X'
        original = str(cliente).strip()
        sem_prefixo = re.sub(r'(?i)^cliente\s*', '', original).strip()
        if sem_prefixo == '':
            return 'Cliente X'
        m = re.search(r'([A-Za-z0-9]+)$', sem_prefixo)
        if not m:
            return 'Cliente X'
        sufixo = m.group(1)
        if sufixo.isdigit():
            sufixo_formatado = sufixo
        else:
            sufixo_formatado = sufixo[-1].upper()
        return f"Cliente {sufixo_formatado}"

    def formatar_data(data_str):
        if pd.isna(data_str) or str(data_str).strip() == '':
            return ''
        data_str = str(data_str).strip()
        try:
            dt = pd.to_datetime(data_str, errors='coerce', dayfirst=True)
            return dt.strftime('%Y-%m-%d') if not pd.isna(dt) else ''
        except:
            return ''

    def formatar_status(status):
        if pd.isna(status) or str(status).strip() == '':
            return 'Pendente'
        status = str(status).strip().lower()
        if any(p in status for p in ['pago', 'paid', 'liquidado']):
            return 'Pago'
        if any(p in status for p in ['vencido', 'overdue']):
            return 'Vencido'
        if any(p in status for p in ['pendente', 'pending']):
            return 'Pendente'
        return 'Pendente'

    def parse_valor(valor):
        if pd.isna(valor) or str(valor).strip().lower() in ("", "null"):
            return 0.0
        valor_str = str(valor).strip()
        valor_str = re.sub(r'[^\d,.-]', '', valor_str)
        if '.' in valor_str and ',' in valor_str:
            valor_str = valor_str.replace('.', '').replace(',', '.')
        elif re.match(r'^\d+\.\d{3}$', valor_str):
            valor_str = valor_str.replace('.', '')
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')
        try:
            return float(valor_str)
        except:
            return 0.0

    # ------------------------
    # 3. APLICAR FORMATAÇÕES
    # ------------------------
    df["CREDOR"] = df["CREDOR"].apply(formatar_credor)
    df["CAMPANHA"] = df["CAMPANHA"].apply(formatar_campanha)
    df["CLIENTE"] = df["CLIENTE"].apply(formatar_cliente)
    df["DATA_CADASTRO"] = df["DATA_CADASTRO"].apply(formatar_data)
    df["DATA_PAGAMENTO"] = df["DATA_PAGAMENTO"].apply(formatar_data)
    df["STATUS_TITULO"] = df["STATUS_TITULO"].apply(formatar_status)
    df["VALOR"] = df["VALOR"].apply(parse_valor)

    # ------------------------
    # 4. FORMATAR PARA CSV (estilo brasileiro)
    # ------------------------
    df["VALOR"] = df["VALOR"].apply(
        lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    # Salvar CSV final - ✅ CORRIGIDO: Salvar na pasta data/
    out_path = Path("dados_cobranca_formatado.csv")
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False, sep=',', encoding='utf-8')

    return df

if __name__ == "__main__":
    try:
        df_final = processar_csv()
        print("✅ CSV formatado criado com sucesso!")
        print(df_final.head())
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        print("📁 Verifique se o arquivo 'dados_cobranca.csv' existe")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")