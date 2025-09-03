import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Cobranças - Análise Mensal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL base da API
API_BASE_URL = "http://localhost:8000"


@st.cache_data(ttl=300)
def fetch_data(endpoint, params=None):
    """Busca dados da API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def create_monthly_evolution_chart(df):
    """Cria gráfico de evolução mensal dos valores totais"""
    if df.empty:
        return None

    monthly_data = df.groupby('mes_ano').agg({
        'valor_total': 'sum',
        'quantidade': 'sum'
    }).reset_index().sort_values('mes_ano')

    fig = px.line(
        monthly_data,
        x='mes_ano',
        y='valor_total',
        title='📈 Evolução Mensal dos Valores Totais',
        labels={'mes_ano': 'Mês/Ano', 'valor_total': 'Valor Total (R$)'},
        markers=True
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode='x unified'
    )

    # Adicionar barras como complemento
    fig.add_trace(
        go.Bar(
            x=monthly_data['mes_ano'],
            y=monthly_data['quantidade'],
            name='Quantidade',
            yaxis='y2',
            opacity=0.3,
            marker_color='lightgray'
        )
    )

    fig.update_layout(
        yaxis2=dict(
            title='Quantidade de Registros',
            overlaying='y',
            side='right'
        )
    )

    return fig


def create_credor_comparison_chart(df):
    """Cria gráfico comparativo de valores por CREDOR"""
    if df.empty:
        return None

    credor_data = df.groupby('credor').agg({
        'valor_total': 'sum',
        'quantidade': 'sum'
    }).reset_index().sort_values('valor_total', ascending=False)

    fig = px.bar(
        credor_data,
        x='credor',
        y='valor_total',
        color='quantidade',
        title='🏢 Comparativo de Valores por Credor',
        labels={'credor': 'Credor', 'valor_total': 'Valor Total (R$)', 'quantidade': 'Qtd Registros'},
        color_continuous_scale='Blues',
        text_auto='.2s'
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode='x unified'
    )

    return fig


def create_credor_pie_chart(df):
    """Cria gráfico de pizza com distribuição por credor"""
    if df.empty:
        return None

    credor_data = df.groupby('credor')['valor_total'].sum().reset_index()

    fig = px.pie(
        credor_data,
        values='valor_total',
        names='credor',
        title='🥧 Distribuição Percentual por Credor',
        hole=0.3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label+value',
        texttemplate='%{label}<br>%{percent}<br>R$ %{value:,.2f}'
    )

    return fig


def main():
    # Cabeçalho
    st.title("📊 Dashboard de Análise de Cobranças")
    st.markdown("Análise mensal de cobranças por credor e status")
    st.markdown("---")

    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros Interativos")

    # Buscar opções disponíveis da API
    meses_data = fetch_data("/resumo/meses") or {"meses": []}
    credores_data = fetch_data("/resumo/credores") or {"credores": []}

    # Filtros interativos
    selected_mes = st.sidebar.selectbox(
        "Filtrar por Mês:",
        options=["Todos"] + meses_data["meses"],
        index=0
    )

    selected_credor = st.sidebar.selectbox(
        "Filtrar por Credor:",
        options=["Todos"] + credores_data["credores"],
        index=0
    )

    selected_status = st.sidebar.selectbox(
        "Filtrar por Status:",
        options=["Todos", "Pago", "Pendente", "Vencido"],
        index=0
    )

    # Aplicar filtros
    params = {}
    if selected_mes != "Todos":
        params["mes_ano"] = selected_mes
    if selected_credor != "Todos":
        params["credor"] = selected_credor
    if selected_status != "Todos":
        params["status"] = selected_status

    # Buscar dados da API
    resumo_data = fetch_data("/resumo", params=params)

    if not resumo_data:
        st.error("❌ Não foi possível conectar à API. Verifique se a API está rodando em http://localhost:8000")
        st.info("💡 Execute: `python run_api.py` para iniciar a API")
        return

    df = pd.DataFrame(resumo_data["data"])

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados")
        return

    # Métricas principais
    st.header("📈 Métricas Principais")

    col1, col2, col3, col4 = st.columns(4)

    total_valor = df['valor_total'].sum()
    total_registros = df['quantidade'].sum()
    avg_valor = df['valor_total'].sum() / df['quantidade'].sum() if df['quantidade'].sum() > 0 else 0
    unique_credores = df['credor'].nunique()

    with col1:
        st.metric("Valor Total", f"R$ {total_valor:,.2f}")
    with col2:
        st.metric("Total de Registros", f"{total_registros:,}")
    with col3:
        st.metric("Valor Médio", f"R$ {avg_valor:,.2f}")
    with col4:
        st.metric("Credores Únicos", unique_credores)

    st.markdown("---")

    # GRÁFICO 1: Evolução Mensal dos Valores Totais (Linha)
    st.header("📈 Evolução Mensal dos Valores Totais")
    fig_evolution = create_monthly_evolution_chart(df)
    if fig_evolution:
        st.plotly_chart(fig_evolution, use_container_width=True)
    else:
        st.info("Não há dados suficientes para mostrar a evolução mensal")

    st.markdown("---")

    # GRÁFICO 2: Comparativo de Valores por CREDOR (Barras)
    st.header("🏢 Comparativo de Valores por Credor")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_comparison = create_credor_comparison_chart(df)
        if fig_comparison:
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("Não há dados suficientes para comparação por credor")

    with col2:
        fig_pie = create_credor_pie_chart(df)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Não há dados suficientes para gráfico de pizza")

    st.markdown("---")

    # TABELA RESUMO INTERATIVA
    st.header("📊 Tabela Resumo Interativa")

    # Filtros adicionais para a tabela
    col1, col2, col3 = st.columns(3)

    with col1:
        sort_by = st.selectbox(
            "Ordenar por:",
            options=["Mês", "Credor", "Status", "Valor Total", "Quantidade"],
            index=3
        )

    with col2:
        sort_order = st.selectbox(
            "Ordem:",
            options=["Ascendente", "Descendente"],
            index=1
        )

    with col3:
        show_rows = st.slider("Linhas por página:", 5, 50, 10)

    # Ordenar dados
    sort_columns = {
        "Mês": "mes_ano",
        "Credor": "credor",
        "Status": "status_titulo",
        "Valor Total": "valor_total",
        "Quantidade": "quantidade"
    }

    df_sorted = df.sort_values(
        sort_columns[sort_by],
        ascending=(sort_order == "Ascendente")
    )

    # Mostrar tabela
    st.dataframe(
        df_sorted.head(show_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "mes_ano": st.column_config.TextColumn("Mês/Ano", width="small"),
            "credor": st.column_config.TextColumn("Credor", width="medium"),
            "status_titulo": st.column_config.TextColumn("Status", width="small"),
            "quantidade": st.column_config.NumberColumn("Quantidade", format="%d", width="small"),
            "valor_total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f", width="medium"),
            "valor_medio": st.column_config.NumberColumn("Valor Médio", format="R$ %.2f", width="medium")
        }
    )

    # Paginação e download
    col1, col2 = st.columns(2)

    with col1:
        st.caption(f"Mostrando {min(show_rows, len(df_sorted))} de {len(df_sorted)} registros")

    with col2:
        csv = df_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Exportar para CSV",
            data=csv,
            file_name=f"resumo_cobrancas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Informações do sistema
    with st.sidebar:
        st.markdown("---")
        st.subheader("ℹ️ Informações do Sistema")

        health_data = fetch_data("/health")
        if health_data:
            status_color = "🟢" if health_data['status'] == "OK" else "🔴"
            st.write(f"{status_color} **Status API:** {health_data['status']}")
            st.write(f"📦 **Versão:** {health_data['version']}")
            st.write(f"💾 **Database:** {'Conectado' if health_data['database'] else 'Desconectado'}")

        st.markdown("---")
        st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.caption(f"Total de registros: {len(df)}")


if __name__ == "__main__":
    main()