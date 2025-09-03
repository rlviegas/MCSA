📊 MCSA - Rafael Viegas

📋 Pré-requisitos
Python 3.8+
pip (gerenciador de pacotes Python)
Git (controle de versão)

🚀 Instalação
1. Clone o repositório
git clone https://github.com/seu-usuario/MCSA.git
cd MCSA 

2. Instale as dependências
pip install -r requirements.txt

🏃 Execução
Pipeline Completo (ETL + API + Dashboard)
python main.py # Executa todo o processamento de dados

Execução da API FastAPI
# Terminal 1 - Inicie a API REST
python run_api.py

Execução do Dashboard Streamlit
# Terminal 2 - Inicie o dashboard visual
streamlit run viz/app.py

🌐 Acessos e Endpoints

🔌 API Documentation: http://localhost:8000/docs
📊 Dashboard Interativo: http://localhost:8501
📚 Documentação Alternativa: http://localhost:8000/redoc

Endpoints da API
Método	Endpoint	Descrição
GET	/health	Health check da API
GET	/resumo	Resumo com filtros dinâmicos
GET	/resumo/aggregations	Estatísticas agregadas
GET	/resumo/meses	Meses disponíveis
GET	/resumo/credores	Credores disponíveis

📊 Funcionalidades Implementadas

✅ Parte 1: ETL (Extract, Transform, Load)

Extração: Leitura de CSV com tratamento de encoding.
Transformação: Formatação de valores.
Limpeza: Tratamento de dados missing e inconsistentes.
Agrupamento: Consolidação por CREDOR e STATUS_TITULO.
Carga: Armazenamento em SQLite e CSV.

✅ Parte 2: API FastAPI

Endpoints RESTful: API completa com documentação automática.
Filtros Dinâmicos: Parâmetros query para credor, status e mês.
Paginação: Controle de limite e offset para grandes datasets.
Validação: Schemas Pydantic para validação de dados.
Tratamento de Erros: Sistema de exceções e logging.

✅ Parte 3: Dashboard Streamlit

Visualização Interativa: Gráficos Plotly com interatividade.
Filtros em Tempo Real: Atualização dinâmica dos dados.
Métricas em Tempo Real: KPI cards com valores atualizados.
Exportação de Dados: Download dos datasets em CSV.
Design Responsivo: Layout adaptável para diferentes dispositivos.

🧪 Testes e Validação

Testes da API:

# Health check
curl http://localhost:8000/health

# Resumo completo
curl http://localhost:8000/resumo

# Com filtros específicos
curl "http://localhost:8000/resumo?credor=Credor+A&status=Pago&mes_ano=2023-01"

Testes do Banco de Dados:

# Verificação da integridade dos dados
python -c "
import sqlite3
conn = sqlite3.connect('data/resumo.bd')
cursor = conn.execute('SELECT COUNT(*) FROM resumo_mensal')
print(f'✅ Registros no banco: {cursor.fetchone()[0]}')
conn.close()
"

Testes de Integração:

# Verifique o pipeline completo
python main.py && echo "✅ ETL executado com sucesso" && python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(f'✅ API Status: {response.json()[\"status\"]}')
"

Uso de IA no Desenvolvimento (Hangzhou DeepSeek):
Declaração de Uso de Ferramentas de IA.
Este projeto foi desenvolvido com assistência estratégica de IA para acelerar o desenvolvimento, garantir boas práticas de código e implementar soluções otimizadas.

Como a IA foi utilizada:
1. Geração de Estrutura e Boilerplate:

Contribuição: Definição da arquitetura modular e organização do projeto.

Validação: Estrutura revisada e ajustada para necessidades específicas.

2. Implementação do Pipeline ETL:

Modificações: Adaptação para o formato específico dos dados, adição de validações customizadas e logging detalhado

Validação: Testes com dados reais e verificação de edge cases

3. Leitura, Debug e Documentação de Código:

Upload dos arquivos de código fonte para análise contextual;

Solicitação de debugging específico para problemas identificados;

Análise de performance e sugestões de otimização.

Contribuição:

Identificação e correção de bugs complexos de concatenação de caminhos.

Melhoria do sistema de tratamento de erros e exceções.

Adição de comentários técnicos detalhados para manutenibilidade.

Otimização de queries SQL e estrutura de dados.

📊 Partes Desenvolvidas Manualmente:
Criaçãoe e parametrização da API FastAPI

Desenvolvimento dos gráficos na interface web.

Integração da Conexão ETL → API → Dashboard.

Sistema de Logging: Implementação de logging detalhado para monitoramento.

Tratamento de Erros: Sistema de exceções e fallbacks.

Otimizações de Performance: Melhoria de queries e cache de dados.

Configuração de Ambiente: Scripts de setup e documentação.

Validações de Negócio: Regras específicas de domínio.

✅ Métodos de Validação Implementados:
Testes Manuais: Todos os endpoints testados via Swagger UI

Validação de Dados: Verificação cruzada entre CSV, SQLite e API responses

Testes de Usabilidade: Avaliação da interface e experiência do usuário

Monitoramento de Performance: Análise de tempo de resposta e consumo de memória

Validação de Negócio: Confirmação das regras de processamento específicas

