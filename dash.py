import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Dashboard Área Técnica - SST",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Customizada para Suporte a Modo Claro e Escuro (Dark Mode)
st.markdown("""
    <style>
    /* Estilização dos cards de métrica adaptável ao tema claro/escuro */
    [data-testid="stMetric"] {
        background-color: var(--background-secondary-color, #f0f2f6);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #0066cc;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-color, #31333F) !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-color, #31333F) !important;
        opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÃO PARA LOCALIZAR NOMES DE COLUNAS DE FORMA FLEXÍVEL
# -----------------------------------------------------------------------------
def get_col_name(df, possible_names):
    """Encontra a coluna na planilha ignorando maiúsculas/minúsculas e espaços extras."""
    cols_clean = {str(col).strip().lower(): col for col in df.columns}
    for name in possible_names:
        name_clean = name.strip().lower()
        if name_clean in cols_clean:
            return cols_clean[name_clean]
    return None

# -----------------------------------------------------------------------------
# TOPO DA PÁGINA & UPLOAD DISCRETO
# -----------------------------------------------------------------------------
col_title, col_upload = st.columns([3, 1])

with col_title:
    st.title("🛡️ Painel de Gestão Técnica & SST")
    st.caption("Acompanhamento de PGR, PCMSO, Visitas Técnicas e Vencimentos por Empresa")

with col_upload:
    with st.expander("📁 Carregar Planilha", expanded=False):
        uploaded_file = st.file_uploader("Subir arquivo (.xlsx ou .csv)", type=["xlsx", "csv"])

# -----------------------------------------------------------------------------
# CARREGAMENTO E TRATAMENTO DE DADOS
# -----------------------------------------------------------------------------
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            try:
                df_raw = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except Exception:
                uploaded_file.seek(0)
                try:
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='latin1', on_bad_lines='skip')
                except Exception:
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(uploaded_file, sep=',', encoding='latin1', on_bad_lines='skip')
        else:
            df_raw = pd.read_excel(uploaded_file)
            
        st.success("Planilha carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
else:
    # Dados fictícios para simulação
    n = 60
    tecnicos = ['João Silva', 'Maria Oliveira', 'Carlos Eduardo', 'Ana Costa']
    fases = ['Visita Agendada', 'Elaboração PGR', 'Revisão PCMSO', 'Emissão Finalizada', 'Entregue']
    status_pgr = ['Vigente', 'Em Elaboração', 'A Vencer (30 dias)', 'Vencido']
    status_pcmso = ['Vigente', 'Aguardando Exames', 'A Vencer (30 dias)', 'Vencido']
    ferramentas = ['Checklist Presencial', 'Sistema Web SST', 'Planilha Auxiliar', 'Entrevista Técnica']
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    df_raw = pd.DataFrame({
        'ID': range(1001, 1001 + n),
        'Nome do negócio': [f'Atendimento Técnico - Empresa {i}' for i in range(1, n+1)],
        'Empresa': [f'Empresa {chr(65 + i%26)} LTDA' for i in range(n)],
        'Razão Social': [f'Razão Social {chr(65 + i%26)} S/A' for i in range(n)],
        'CNPJ da Empresa': [f'12.345.678/0001-{i:02d}' for i in range(n)],
        'Fase': np.random.choice(fases, n),
        'Técnico Responsável': np.random.choice(tecnicos, n),
        'Status do PGR': np.random.choice(status_pgr, n),
        'PGR Status': np.random.choice(status_pgr, n),
        'PCMSO Status': np.random.choice(status_pcmso, n),
        'GRAU DE RISCO': np.random.choice(['Grau 1', 'Grau 2', 'Grau 3', 'Grau 4'], n),
        'Grau de Risco da Empresa': np.random.choice(['Baixo Dificuldade', 'Média Dificuldade', 'Alta Dificuldade'], n),
        'Ferramenta Utilizada': np.random.choice(ferramentas, n),
        'MÊS DE RENOVAÇÃO': np.random.choice(meses, n),
        'Data da Visita Tecnica': pd.date_range(start='2026-01-01', periods=n, freq='3D').strftime('%Y-%m-%d'),
        'PGR Vencimento': pd.date_range(start='2026-03-01', periods=n, freq='5D').strftime('%Y-%m-%d'),
        'PCMSO Vencimento': pd.date_range(start='2026-03-01', periods=n, freq='5D').strftime('%Y-%m-%d'),
        'Observações Área Técnica': ['Aguardando laudo' if i%2==0 else 'OK' for i in range(n)],
        # Colunas extras para demonstrar a filtragem na tabela
        'Pipeline': ['P1']*n,
        'Negocio repetido': ['Não']*n,
        'disponivel para todos': ['Sim']*n,
        'consulta repetida': ['Não']*n,
        'etapa anterior': ['Inicial']*n,
        'observadores': ['Nenhum']*n,
        'probalidade': ['100%']*n,
        'status do pagamento': ['Pago']*n,
        'status da entrega': ['Entregue']*n,
        'vinculo': ['Direto']*n,
        'tipo': ['Padrão']*n,
        'fonte': ['Site']*n,
        'informaçoes da fonte': ['Internet']*n,
        'renda': [0]*n,
        'moeda': ['BRL']*n,
        'informaçoe de sua empresa': ['SST']*n,
        'fechado': ['Sim']*n
    })

# Identificação Mapeada das Colunas
col_tecnico = get_col_name(df_raw, ['Técnico Responsável', 'Tecnico Responsavel', 'Modificado por'])
col_mes = get_col_name(df_raw, ['MÊS DE RENOVAÇÃO', 'MES DE RENOVACAO'])
col_fase = get_col_name(df_raw, ['Fase', 'Etapa'])
col_pgr_status = get_col_name(df_raw, ['PGR Status', 'Status do PGR'])
col_pcmso_status = get_col_name(df_raw, ['PCMSO Status', 'Status do PCMSO'])
col_data_visita = get_col_name(df_raw, ['Data da Visita Tecnica', 'Data Visita Tecnica', 'Data Visita', 'Data da Visita'])

# Mapeamento dos Graus de Risco e Ferramenta
col_grau_empresa = get_col_name(df_raw, ['Grau de Risco da Empresa', 'Grau de Risco Empresa'])
col_grau_nr01 = get_col_name(df_raw, ['GRAU DE RISCO', 'Grau de Risco NR01', 'Grau de Risco'])
col_ferramenta = get_col_name(df_raw, ['Ferramenta Utilizada', 'Ferramenta', 'Ferramenta SST', 'Método Utilizado'])

col_empresa = get_col_name(df_raw, ['Empresa', 'Razão Social', 'Nome Fantasia', 'Nome do negócio'])

# -----------------------------------------------------------------------------
# BARRA LATERAL RECOLHÍVEL - FILTROS DINÂMICOS
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Filtros do Dashboard")
st.sidebar.caption("Clique na seta no canto superior esquerdo para expandir ou recolher.")

df_filtered = df_raw.copy()

# Filtro 1: Técnico Responsável
if col_tecnico:
    opts = ['Todos'] + sorted([str(x) for x in df_raw[col_tecnico].dropna().unique()])
    sel = st.sidebar.selectbox("Técnico Responsável", opts)
    if sel != 'Todos':
        df_filtered = df_filtered[df_filtered[col_tecnico].astype(str) == sel]

# Filtro 2: Mês de Renovação
if col_mes:
    opts = ['Todos'] + sorted([str(x) for x in df_raw[col_mes].dropna().unique()])
    sel = st.sidebar.selectbox("Mês de Renovação", opts)
    if sel != 'Todos':
        df_filtered = df_filtered[df_filtered[col_mes].astype(str) == sel]

# Filtro 3: Grau de Risco da Empresa
if col_grau_empresa:
    opts = ['Todos'] + sorted([str(x) for x in df_raw[col_grau_empresa].dropna().unique()])
    sel = st.sidebar.selectbox("Grau de Risco da Empresa", opts)
    if sel != 'Todos':
        df_filtered = df_filtered[df_filtered[col_grau_empresa].astype(str) == sel]

# Filtro 4: Fase
if col_fase:
    opts = sorted([str(x) for x in df_raw[col_fase].dropna().unique()])
    sel = st.sidebar.multiselect("Fase do Processo", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[df_filtered[col_fase].astype(str).isin(sel)]

# Filtro 5: Status PGR
if col_pgr_status:
    opts = sorted([str(x) for x in df_raw[col_pgr_status].dropna().unique()])
    sel = st.sidebar.multiselect("Status PGR", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[df_filtered[col_pgr_status].astype(str).isin(sel)]

# Filtro 6: Status PCMSO
if col_pcmso_status:
    opts = sorted([str(x) for x in df_raw[col_pcmso_status].dropna().unique()])
    sel = st.sidebar.multiselect("Status PCMSO", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[df_filtered[col_pcmso_status].astype(str).isin(sel)]

# -----------------------------------------------------------------------------
# CARDS DE MÉTRICAS (KPIs)
# -----------------------------------------------------------------------------
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)

total_empresas = len(df_filtered)
pgr_vencidos = len(df_filtered[df_filtered[col_pgr_status].astype(str).str.contains('Vencid|A Vencer', case=False, na=False)]) if col_pgr_status else 0
pcmso_vencidos = len(df_filtered[df_filtered[col_pcmso_status].astype(str).str.contains('Vencid|A Vencer', case=False, na=False)]) if col_pcmso_status else 0
tecnicos_ativos = df_filtered[col_tecnico].nunique() if col_tecnico else 0

m1.metric("Total de Empresas", total_empresas)
m2.metric("PGR (Críticos/Vencendo)", pgr_vencidos)
m3.metric("PCMSO (Críticos/Vencendo)", pcmso_vencidos)
m4.metric("Técnicos Envolvidos", tecnicos_ativos)

st.markdown("---")

# -----------------------------------------------------------------------------
# GRÁFICOS INTERATIVOS (PLOTLY)
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Empresas por Mês de Renovação")
    if col_mes and not df_filtered.empty:
        fig_mes = px.bar(
            df_filtered[col_mes].value_counts().reset_index(),
            x=col_mes, y='count',
            labels={'count': 'Qtd Empresas', col_mes: 'Mês'},
            color='count', color_continuous_scale='Blues'
        )
        fig_mes.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_mes, use_container_width=True)

with g2:
    st.subheader("👷 Processos por Técnico Responsável")
    if col_tecnico and col_fase and not df_filtered.empty:
        df_tec = df_filtered.groupby([col_tecnico, col_fase]).size().reset_index(name='Quantidade')
        fig_tec = px.bar(
            df_tec, x=col_tecnico, y='Quantidade', color=col_fase, barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_tec.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_tec, use_container_width=True)

g3, g4 = st.columns(2)

with g3:
    st.subheader("🚦 Comparativo PGR vs PCMSO")
    if col_pgr_status and col_pcmso_status and not df_filtered.empty:
        status_df = pd.DataFrame({
            'Documento': ['PGR']*len(df_filtered) + ['PCMSO']*len(df_filtered),
            'Status': list(df_filtered[col_pgr_status]) + list(df_filtered[col_pcmso_status])
        })
        fig_status = px.histogram(
            status_df, x='Status', color='Documento', barmode='group',
            color_discrete_map={'PGR': '#1f77b4', 'PCMSO': '#2ca02c'}
        )
        fig_status.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_status, use_container_width=True)

with g4:
    st.subheader("🏢 Grau de Risco da Empresa (Dificuldade)")
    if col_grau_empresa and not df_filtered.empty:
        fig_risco_emp = px.pie(
            df_filtered, names=col_grau_empresa, hole=0.4,
            color_discrete_sequence=px.colors.sequential.OrRd
        )
        fig_risco_emp.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_risco_emp, use_container_width=True)

# SEÇÃO NOVOS GRÁFICOS: FASE E DATA DA VISITA TÉCNICA
g5, g6 = st.columns(2)

with g5:
    st.subheader("📌 Distribuição por Fase do Processo")
    if col_fase and not df_filtered.empty:
        fig_fase_pie = px.pie(
            df_filtered, names=col_fase, hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_fase_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_fase_pie, use_container_width=True)
    else:
        st.info("Coluna 'Fase' não localizada no arquivo.")

with g6:
    st.subheader("📅 Visitas Técnicas por Data")
    if col_data_visita and not df_filtered.empty:
        df_visita = df_filtered[col_data_visita].dropna().astype(str).value_counts().reset_index()
        df_visita.columns = ['Data', 'Quantidade']
        df_visita = df_visita.sort_values('Data')
        
        fig_visita = px.bar(
            df_visita, x='Data', y='Quantidade',
            labels={'Data': 'Data da Visita', 'Quantidade': 'Nº de Visitas'},
            color_discrete_sequence=['#2b5c8f']
        )
        fig_visita.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_visita, use_container_width=True)
    else:
        st.info("Coluna 'Data da Visita Tecnica' não localizada no arquivo.")

# -----------------------------------------------------------------------------
# TABELA DETALHADA COM BUSCA E EXCLUSÃO DE COLUNAS DESNECESSÁRIAS
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Detalhamento dos Registros")

col_search, _ = st.columns([3, 1])
with col_search:
    search_term = st.text_input("🔎 Buscar em qualquer campo da tabela:")

df_display = df_filtered.copy()

# Lista de colunas a serem removidas conforme solicitado
cols_to_remove = [
    'Pipeline', 'Negocio repetido', 'disponivel para todos', 'consulta repetida',
    'etapa anterior', 'observadores', 'probalidade', 'status do pagamento',
    'status da entrega', 'vinculo', 'tipo', 'fonte', 'informaçoes da fonte',
    'renda', 'moeda', 'informaçoe de sua empresa', 'fechado'
]

# Função para remover colunas ignorando diferenças de maiúsculas/minúsculas e acentos
cols_clean_map = {str(col).strip().lower(): col for col in df_display.columns}
cols_actual_to_drop = []

for target in cols_to_remove:
    target_clean = target.strip().lower()
    if target_clean in cols_clean_map:
        cols_actual_to_drop.append(cols_clean_map[target_clean])

if cols_actual_to_drop:
    df_display = df_display.drop(columns=cols_actual_to_drop)

if search_term:
    mask = df_display.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    df_display = df_display[mask]

st.dataframe(df_display, use_container_width=True, height=350)

# -----------------------------------------------------------------------------
# QUADROS INFERIORES: NR01 PSICOSSOCIAL & FERRAMENTA UTILIZADA
# -----------------------------------------------------------------------------
st.markdown("---")
col_nr01, col_ferr = st.columns(2)

with col_nr01:
    st.markdown("##### 🧠 Grau de Risco - NR01 Psicossocial")
    if col_grau_nr01 and not df_filtered.empty:
        fig_nr01 = px.pie(
            df_filtered, names=col_grau_nr01, hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_nr01.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_nr01, use_container_width=True)
    else:
        st.info("Coluna 'GRAU DE RISCO' (NR01) não localizada no arquivo.")

with col_ferr:
    st.markdown("##### 🛠️ Ferramenta Utilizada")
    if col_ferramenta and not df_filtered.empty:
        fig_ferr = px.bar(
            df_filtered[col_ferramenta].value_counts().reset_index(),
            x=col_ferramenta, y='count',
            labels={'count': 'Qtd', col_ferramenta: 'Ferramenta'},
            color=col_ferramenta, color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_ferr.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_ferr, use_container_width=True)
    else:
        st.info("Coluna 'Ferramenta Utilizada' não localizada no arquivo.")