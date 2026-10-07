import datetime
import anthropic
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Área Técnica - SST",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Customizada
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: var(--background-secondary-color, #f0f2f6);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #d97706;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-color, #31333F) !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-color, #31333F) !important;
        opacity: 0.8;
    }
    </style>
""",
    unsafe_allow_html=True,
)


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
    st.title("🛡 Painel de Gestão Técnica & SST")
    st.caption(
        "Acompanhamento de PGR, PCMSO, Visitas Técnicas e Vencimentos por Empresa"
    )

with col_upload:
    with st.expander("📁 Carregar Planilha", expanded=False):
        uploaded_file = st.file_uploader(
            "Subir arquivo (.xlsx ou .csv)", type=["xlsx", "csv"]
        )

# -----------------------------------------------------------------------------
# CARREGAMENTO E TRATAMENTO DE DADOS
# -----------------------------------------------------------------------------
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            try:
                df_raw = pd.read_csv(
                    uploaded_file, sep=None, engine="python", encoding="utf-8"
                )
            except Exception:
                uploaded_file.seek(0)
                try:
                    df_raw = pd.read_csv(
                        uploaded_file, sep=";", encoding="latin1", on_bad_lines="skip"
                    )
                except Exception:
                    uploaded_file.seek(0)
                    df_raw = pd.read_csv(
                        uploaded_file, sep=",", encoding="latin1", on_bad_lines="skip"
                    )
        else:
            df_raw = pd.read_excel(uploaded_file)

        st.success("Planilha carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
else:
    # Dados fictícios para simulação caso nenhum arquivo seja enviado
    np.random.seed(42)
    n = 60
    tecnicos = ["João Silva", "Maria Oliveira", "Carlos Eduardo", "Ana Costa"]
    fases = [
        "Visita Agendada",
        "Elaboração PGR",
        "Revisão PCMSO",
        "Emissão Finalizada",
        "Entregue",
        "Concluído",
        "Pendência",
    ]
    status_pgr = ["Vigente", "Em Elaboração", "A Vencer (30 dias)", "Vencido"]
    status_pcmso = ["Vigente", "Aguardando Exames", "A Vencer (30 dias)", "Vencido"]
    ferramentas = [
        "Checklist Presencial",
        "Sistema Web SST",
        "Planilha Auxiliar",
        "Entrevista Técnica",
    ]
    meses = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    df_raw = pd.DataFrame({
        "ID": range(1001, 1001 + n),
        "Nome do negócio": [
            f"Atendimento Técnico - Empresa {i}" for i in range(1, n + 1)
        ],
        "Empresa": [f"Empresa {chr(65 + i%26)} LTDA" for i in range(n)],
        "Razão Social": [f"Razão Social {chr(65 + i%26)} S/A" for i in range(n)],
        "CNPJ da Empresa": [f"12.345.678/0001-{i:02d}" for i in range(n)],
        "Fase": np.random.choice(fases, n),
        "Técnico Responsável": np.random.choice(tecnicos, n),
        "Status do PGR": np.random.choice(status_pgr, n),
        "PGR Status": np.random.choice(status_pgr, n),
        "PCMSO Status": np.random.choice(status_pcmso, n),
        "GRAU DE RISCO": np.random.choice(
            ["Grau 1", "Grau 2", "Grau 3", "Grau 4"], n
        ),
        "Grau de Risco da Empresa": np.random.choice(
            ["Baixo Dificuldade", "Média Dificuldade", "Alta Dificuldade"], n
        ),
        "Ferramenta Utilizada": np.random.choice(ferramentas, n),
        "MÊS DE RENOVAÇÃO": np.random.choice(meses, n),
        "Data da Visita Tecnica": pd.date_range(
            start="2026-01-01", periods=n, freq="3D"
        ).strftime("%d/%m/%Y"),
        "Data de fechamento": [
            pd.date_range(start="2026-01-15", periods=n, freq="4D")[i].strftime(
                "%d/%m/%Y"
            )
            if i % 3 != 0
            else None
            for i in range(n)
        ],
        "Modificado em": pd.date_range(
            start="2026-02-01", periods=n, freq="2D"
        ).strftime("%d/%m/%Y"),
        "PGR Vencimento": pd.date_range(
            start="2026-03-01", periods=n, freq="5D"
        ).strftime("%d/%m/%Y"),
        "PCMSO Vencimento": pd.date_range(
            start="2026-03-01", periods=n, freq="5D"
        ).strftime("%d/%m/%Y"),
        "Observações Área Técnica": [
            "Aguardando laudo" if i % 2 == 0 else "OK" for i in range(n)
        ],
    })

# Mapeamento Flexível das Colunas
col_tecnico = get_col_name(
    df_raw, ["Técnico Responsável", "Tecnico Responsavel", "Modificado por"]
)
col_mes = get_col_name(df_raw, ["MÊS DE RENOVAÇÃO", "MES DE RENOVACAO"])
col_fase = get_col_name(df_raw, ["Fase", "Etapa"])
col_pgr_status = get_col_name(df_raw, ["PGR Status", "Status do PGR"])
col_pcmso_status = get_col_name(df_raw, ["PCMSO Status", "Status do PCMSO"])
col_data_visita = get_col_name(
    df_raw,
    [
        "Data da Visita Tecnica",
        "Data Visita Tecnica",
        "Data Visita",
        "Data da Visita",
    ],
)
col_data_conclusao = get_col_name(
    df_raw,
    [
        "Data de fechamento",
        "Data fechamento",
        "Fechamento",
        "Data de Conclusão",
        "Data Conclusão",
        "Data Concluido",
        "Concluído em",
    ],
)
col_modificado = get_col_name(
    df_raw,
    [
        "Modificado",
        "Modificado em",
        "Data Modificação",
        "Data Modificacao",
        "Última Modificação",
        "Ultima Modificacao",
        "Atualizado em",
    ],
)
col_grau_empresa = get_col_name(
    df_raw, ["Grau de Risco da Empresa", "Grau de Risco Empresa"]
)
col_grau_nr01 = get_col_name(
    df_raw, ["GRAU DE RISCO", "Grau de Risco NR01", "Grau de Risco"]
)
col_ferramenta = get_col_name(
    df_raw,
    [
        "Ferramenta Utilizada",
        "Ferramenta",
        "Ferramenta SST",
        "Método Utilizado",
    ],
)
col_empresa = get_col_name(
    df_raw, ["Empresa", "Razão Social", "Nome Fantasia", "Nome do negócio"]
)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DATAS E REGRA DE FECHAMENTO (INCLUINDO PENDÊNCIA)
# -----------------------------------------------------------------------------
if col_data_conclusao:
    df_raw["__Data_Conclusao_dt"] = pd.to_datetime(
        df_raw[col_data_conclusao], dayfirst=True, errors="coerce"
    )

if col_data_visita:
    df_raw["__Data_Visita_dt"] = pd.to_datetime(
        df_raw[col_data_visita], dayfirst=True, errors="coerce"
    )

if col_modificado:
    df_raw["__Data_Modificacao_dt"] = pd.to_datetime(
        df_raw[col_modificado], dayfirst=True, errors="coerce"
    )

# Identifica se a Fase do negócio é Pendência
if col_fase:
    is_pendencia = (
        df_raw[col_fase]
        .astype(str)
        .str.contains("Pendên|Penden", case=False, na=False)
    )
else:
    is_pendencia = pd.Series(False, index=df_raw.index)

# Definição da Data Efetiva de Fechamento
if col_data_conclusao:
    df_raw["__Data_Fechamento_Efetiva"] = df_raw["__Data_Conclusao_dt"]
    if col_data_visita:
        df_raw["__Data_Fechamento_Efetiva"] = df_raw[
            "__Data_Fechamento_Efetiva"
        ].fillna(df_raw["__Data_Visita_dt"].where(is_pendencia))
    df_raw["Mês Fechamento"] = df_raw["__Data_Fechamento_Efetiva"].dt.strftime(
        "%Y-%m"
    )
elif col_data_visita:
    df_raw["__Data_Fechamento_Efetiva"] = df_raw["__Data_Visita_dt"].where(
        is_pendencia
    )
    df_raw["Mês Fechamento"] = df_raw["__Data_Fechamento_Efetiva"].dt.strftime(
        "%Y-%m"
    )
else:
    df_raw["Mês Fechamento"] = None

# Cálculo do Tempo em Dias (Aging)
if col_data_visita:
    today = pd.Timestamp.now()
    end_date = (
        df_raw["__Data_Fechamento_Efetiva"].fillna(today)
        if "__Data_Fechamento_Efetiva" in df_raw.columns
        else today
    )
    df_raw["Tempo_Em_Dias"] = (end_date - df_raw["__Data_Visita_dt"]).dt.days
    df_raw["Tempo_Em_Dias"] = df_raw["Tempo_Em_Dias"].apply(
        lambda x: max(x, 0) if pd.notnull(x) else np.nan
    )

# -----------------------------------------------------------------------------
# BARRA LATERAL - FILTROS E CONFIGURAÇÃO DA IA CLAUDE (ANTHROPIC)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações & Filtros")

st.sidebar.subheader("🤖 Configuração do Claude (Anthropic)")
try:
    default_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    default_key = ""

claude_api_key_input = st.sidebar.text_input(
    "Chave API Claude",
    value=default_key,
    type="password",
    help="Obtenha sua chave iniciada em sk-ant-... no console da Anthropic.",
)

claude_model_option = st.sidebar.selectbox(
    "Modelo Claude",
    options=[
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
    ],
    index=0,
    help="Sonnet 3.5 é ideal para análises inteligentes e rápidas.",
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros de Dados")

df_filtered = df_raw.copy()

# Filtro por Data de Modificação
if col_modificado and "__Data_Modificacao_dt" in df_filtered.columns:
    valid_dates = df_filtered["__Data_Modificacao_dt"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.sidebar.date_input(
            "Período de Modificação",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered["__Data_Modificacao_dt"].dt.date >= start_date)
                & (df_filtered["__Data_Modificacao_dt"].dt.date <= end_date)
            ]

if col_tecnico:
    opts = ["Todos"] + sorted(
        [str(x) for x in df_raw[col_tecnico].dropna().unique()]
    )
    sel = st.sidebar.selectbox("Técnico Responsável", opts)
    if sel != "Todos":
        df_filtered = df_filtered[df_filtered[col_tecnico].astype(str) == sel]

if col_mes:
    opts = ["Todos"] + sorted([str(x) for x in df_raw[col_mes].dropna().unique()])
    sel = st.sidebar.selectbox("Mês de Renovação", opts)
    if sel != "Todos":
        df_filtered = df_filtered[df_filtered[col_mes].astype(str) == sel]

if "Mês Fechamento" in df_raw.columns:
    opts_conc = ["Todos"] + sorted([
        str(x)
        for x in df_raw["Mês Fechamento"].dropna().unique()
        if str(x) != "nan"
    ])
    sel_conc = st.sidebar.selectbox("Mês de Fechamento (AAAA-MM)", opts_conc)
    if sel_conc != "Todos":
        df_filtered = df_filtered[
            df_filtered["Mês Fechamento"].astype(str) == sel_conc
        ]

if col_grau_empresa:
    opts = ["Todos"] + sorted(
        [str(x) for x in df_raw[col_grau_empresa].dropna().unique()]
    )
    sel = st.sidebar.selectbox("Grau de Risco da Empresa", opts)
    if sel != "Todos":
        df_filtered = df_filtered[
            df_filtered[col_grau_empresa].astype(str) == sel
        ]

if col_fase:
    opts = sorted([str(x) for x in df_raw[col_fase].dropna().unique()])
    sel = st.sidebar.multiselect("Fase do Processo", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[df_filtered[col_fase].astype(str).isin(sel)]

if col_pgr_status:
    opts = sorted([str(x) for x in df_raw[col_pgr_status].dropna().unique()])
    sel = st.sidebar.multiselect("Status PGR", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[
            df_filtered[col_pgr_status].astype(str).isin(sel)
        ]

if col_pcmso_status:
    opts = sorted([str(x) for x in df_raw[col_pcmso_status].dropna().unique()])
    sel = st.sidebar.multiselect("Status PCMSO", options=opts, default=[])
    if sel:
        df_filtered = df_filtered[
            df_filtered[col_pcmso_status].astype(str).isin(sel)
        ]

# -----------------------------------------------------------------------------
# CARDS DE MÉTRICAS (KPIs)
# -----------------------------------------------------------------------------
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)

total_empresas = len(df_filtered)
pgr_vencidos = (
    len(
        df_filtered[
            df_filtered[col_pgr_status]
            .astype(str)
            .str.contains("Vencid|A Vencer", case=False, na=False)
        ]
    )
    if col_pgr_status
    else 0
)
pcmso_vencidos = (
    len(
        df_filtered[
            df_filtered[col_pcmso_status]
            .astype(str)
            .str.contains("Vencid|A Vencer", case=False, na=False)
        ]
    )
    if col_pcmso_status
    else 0
)
tecnicos_ativos = df_filtered[col_tecnico].nunique() if col_tecnico else 0
tempo_medio = (
    f"{df_filtered['Tempo_Em_Dias'].mean():.1f} dias"
    if "Tempo_Em_Dias" in df_filtered.columns
    and not df_filtered["Tempo_Em_Dias"].dropna().empty
    else "N/A"
)

m1.metric("Total de Empresas", total_empresas)
m2.metric("PGR (Críticos/Vencendo)", pgr_vencidos)
m3.metric("PCMSO (Críticos/Vencendo)", pcmso_vencidos)
m4.metric("Técnicos Envolvidos", tecnicos_ativos)
m5.metric("Tempo Médio (Aging)", tempo_medio)

st.markdown("---")

# -----------------------------------------------------------------------------
# GRÁFICOS PRINCIPAIS
# -----------------------------------------------------------------------------
st.subheader("📈 Fechamentos por Técnico de Segurança por Mês")
st.caption(
    "Inclui contratos com Data de Fechamento preenchida e negócios na fase"
    " 'Pendência'."
)

if col_tecnico and "Mês Fechamento" in df_filtered.columns and not df_filtered.empty:
    df_conc = df_filtered.dropna(subset=["Mês Fechamento", col_tecnico])
    if not df_conc.empty:
        df_conc_grouped = (
            df_conc.groupby(["Mês Fechamento", col_tecnico])
            .size()
            .reset_index(name="Total Fechados")
            .sort_values("Mês Fechamento")
        )

        fig_conc_m = px.bar(
            df_conc_grouped,
            x="Mês Fechamento",
            y="Total Fechados",
            color=col_tecnico,
            barmode="group",
            text_auto=True,
            labels={
                "Mês Fechamento": "Mês de Fechamento",
                "Total Fechados": "Qtd. Fechada",
                col_tecnico: "Técnico",
            },
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_conc_m.update_traces(textposition="outside")
        fig_conc_m.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_conc_m, use_container_width=True)
    else:
        st.info("Nenhum dado com fechamento/pendência para os filtros selecionados.")
else:
    st.info("Colunas de Fechamento/Pendência ou Técnico Responsável não disponíveis.")

st.markdown("---")

g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Empresas por Mês de Renovação")
    if col_mes and not df_filtered.empty:
        fig_mes = px.bar(
            df_filtered[col_mes].value_counts().reset_index(),
            x=col_mes,
            y="count",
            text_auto=True,
            labels={"count": "Qtd Empresas", col_mes: "Mês"},
            color="count",
            color_continuous_scale="Blues",
        )
        fig_mes.update_traces(textposition="outside")
        fig_mes.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_mes, use_container_width=True)

with g2:
    st.subheader("👷 Processos por Técnico Responsável")
    if col_tecnico and col_fase and not df_filtered.empty:
        df_tec = (
            df_filtered.groupby([col_tecnico, col_fase])
            .size()
            .reset_index(name="Quantidade")
        )
        fig_tec = px.bar(
            df_tec,
            x=col_tecnico,
            y="Quantidade",
            color=col_fase,
            barmode="stack",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_tec.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_tec, use_container_width=True)

g3, g4 = st.columns(2)

with g3:
    st.subheader("🚦 Comparativo PGR vs PCMSO")
    if col_pgr_status and col_pcmso_status and not df_filtered.empty:
        status_df = pd.DataFrame({
            "Documento": ["PGR"] * len(df_filtered) + ["PCMSO"] * len(df_filtered),
            "Status": (
                list(df_filtered[col_pgr_status])
                + list(df_filtered[col_pcmso_status])
            ),
        })
        fig_status = px.histogram(
            status_df,
            x="Status",
            color="Documento",
            barmode="group",
            text_auto=True,
            color_discrete_map={"PGR": "#1f77b4", "PCMSO": "#2ca02c"},
        )
        fig_status.update_traces(textposition="outside")
        fig_status.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_status, use_container_width=True)

with g4:
    st.subheader("🏢 Grau de Risco da Empresa")
    if col_grau_empresa and not df_filtered.empty:
        fig_risco_emp = px.pie(
            df_filtered,
            names=col_grau_empresa,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.OrRd,
        )
        fig_risco_emp.update_traces(textinfo="value+percent")
        fig_risco_emp.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_risco_emp, use_container_width=True)

# -----------------------------------------------------------------------------
# DETALHAMENTO DA TABELA
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Detalhamento dos Registros")

search_term = st.text_input("🔎 Buscar em qualquer campo da tabela:")

df_display = df_filtered.copy()

cols_to_remove = [
    "Pipeline",
    "Negocio repetido",
    "disponivel para todos",
    "consulta repetida",
    "etapa anterior",
    "observadores",
    "probalidade",
    "status do pagamento",
    "status da entrega",
    "vinculo",
    "tipo",
    "fonte",
    "informaçoes da fonte",
    "renda",
    "moeda",
    "informaçoe de sua empresa",
    "fechado",
    "__Data_Conclusao_dt",
    "__Data_Visita_dt",
    "__Data_Modificacao_dt",
    "__Data_Fechamento_Efetiva",
]

cols_clean_map = {str(col).strip().lower(): col for col in df_display.columns}
cols_actual_to_drop = [
    cols_clean_map[t.strip().lower()]
    for t in cols_to_remove
    if t.strip().lower() in cols_clean_map
]

if cols_actual_to_drop:
    df_display = df_display.drop(columns=cols_actual_to_drop)

if search_term:
    mask = df_display.apply(
        lambda row: row.astype(str).str.contains(search_term, case=False).any(),
        axis=1,
    )
    df_display = df_display[mask]

st.dataframe(df_display, use_container_width=True, height=300)

# -----------------------------------------------------------------------------
# MÓDULO DE IA CLAUDE (ANTHROPIC): DIAGNÓSTICO + PERGUNTAS LIVRES
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🤖 Assistente de Inteligência Artificial (Claude)")

tab_relatorio, tab_perguntas = st.tabs(
    ["📊 Relatório de Diagnóstico", "💬 Fazer Pergunta para a IA"]
)


def preparar_contexto_dados():
    """Monta um resumo estruturado em texto dos dados atualmente filtrados."""
    if col_tecnico and not df_filtered.empty:
        df_tst_group = df_filtered.groupby(col_tecnico)
        carga_df = df_tst_group.size().reset_index(name="Total_Atendimentos")

        if "Tempo_Em_Dias" in df_filtered.columns:
            tempo_medio_tst = (
                df_tst_group["Tempo_Em_Dias"]
                .mean()
                .round(1)
                .reset_index(name="Tempo_Medio_Dias")
            )
            carga_df = pd.merge(carga_df, tempo_medio_tst, on=col_tecnico, how="left")

        if col_grau_empresa:
            grau_distrib = (
                df_filtered.groupby([col_tecnico, col_grau_empresa])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            carga_df = pd.merge(carga_df, grau_distrib, on=col_tecnico, how="left")

        carga_tst = carga_df.to_json(orient="records")
    else:
        carga_tst = "{}"

    tempo_fase = "{}"
    if col_fase and "Tempo_Em_Dias" in df_filtered.columns:
        tempo_fase = (
            df_filtered.groupby(col_fase)["Tempo_Em_Dias"]
            .agg(["mean", "count"])
            .reset_index()
            .to_json(orient="records")
        )
    elif col_fase:
        tempo_fase = (
            df_filtered[col_fase].value_counts().reset_index().to_json(orient="records")
        )

    resumo_geral = {
        "total_empresas_filtradas": len(df_filtered),
        "pgr_vencidos_ou_a_vencer": pgr_vencidos,
        "pcmso_vencidos_ou_a_vencer": pcmso_vencidos,
        "tecnicos_ativos": tecnicos_ativos,
        "tempo_medio_dias": tempo_medio,
        "regra_fechamento": "Considera fechado se possuir data de fechamento OU se estiver na fase 'Pendência'",
    }

    cols_relevantes = [
        c
        for c in [
            col_empresa,
            col_tecnico,
            col_fase,
            col_pgr_status,
            col_pcmso_status,
        ]
        if c in df_filtered.columns
    ]
    amostra_tabela = (
        df_filtered[cols_relevantes].head(25).to_json(orient="records")
        if cols_relevantes
        else "{}"
    )

    return f"""
    ### RESUMO DOS FILTROS ATUAIS:
    {resumo_geral}

    ### CARGA POR TÉCNICO:
    {carga_tst}

    ### FASES DO PROCESSO & TEMPOS:
    {tempo_fase}

    ### AMOSTRA DOS DADOS EXIBIDOS (PRIMEIRAS 25 LINHAS):
    {amostra_tabela}
    """


# -----------------------------------------------------------------------------
# ABA 1: RELATÓRIO AUTOMÁTICO
# -----------------------------------------------------------------------------
with tab_relatorio:
    st.write(
        "Clique no botão abaixo para gerar uma análise automatizada dos gargalos e"
        " carga de trabalho via Claude."
    )
    if st.button("🚀 Gerar Análise Completa por IA"):
        if not claude_api_key_input:
            st.error(
                "⚠️ Insira uma Chave API válida do Claude na barra lateral para"
                " continuar (começa com sk-ant-...)."
            )
        else:
            with st.spinner("Analisando dados via Claude (Anthropic)..."):
                try:
                    contexto = preparar_contexto_dados()
                    prompt_user = f"""
                    Analise os dados extraídos do dashboard de SST/Engenharia de Processos e forneça um relatório estratégico e objetivo.
                    Nota: O indicador de Fechamento considera negócios concluídos e negócios na fase "Pendência".

                    DADOS:
                    {contexto}

                    ---
                    Estruture sua resposta estritamente em 3 seções Markdown:
                    1. **🚨 Análise do Gargalo do Processo (Aging)**
                    2. **⚖️ Avaliação de Carga por Técnico de Segurança**
                    3. **💡 Plano de Ação Recomendado (3 orientações práticas)**
                    """

                    client = anthropic.Anthropic(api_key=claude_api_key_input.strip())
                    response = client.messages.create(
                        model=claude_model_option,
                        max_tokens=1500,
                        temperature=0.7,
                        system=(
                            "Você é um consultor especialista em Segurança e Saúde no"
                            " Trabalho (SST) e Engenharia de Processos."
                        ),
                        messages=[{"role": "user", "content": prompt_user}],
                    )

                    st.markdown("### 📋 Diagnóstico Gerencial")
                    st.info(response.content[0].text)

                except Exception as e:
                    st.error(f"❌ **Erro na API do Claude:** {e}")


# -----------------------------------------------------------------------------
# ABA 2: CAIXA DE PERGUNTAS LIVRES (CHAT COM OS DADOS)
# -----------------------------------------------------------------------------
with tab_perguntas:
    st.write("Digite qualquer dúvida ou pergunta sobre os dados filtrados na tela.")

    with st.form(key="form_pergunta_ia"):
        user_question = st.text_area(
            "Sua Pergunta para a IA:",
            placeholder=(
                "Exemplo: Qual técnico está com o maior tempo médio? Quantas"
                " pendências temos no total? Faça um resumo para a diretoria."
            ),
            height=100,
        )
        submit_button = st.form_submit_button(label="💬 Enviar Pergunta")

    if submit_button:
        if not claude_api_key_input:
            st.error(
                "⚠️ Insira a Chave API do Claude na barra lateral antes de perguntar."
            )
        elif not user_question.strip():
            st.warning("⚠️ Escreva uma pergunta antes de enviar.")
        else:
            with st.spinner("Processando sua pergunta..."):
                try:
                    contexto = preparar_contexto_dados()
                    prompt_custom = f"""
                    Você é um analista de dados de SST altamente prestativo. Responda à pergunta do usuário com base EXCLUSIVAMENTE nos dados fornecidos abaixo.
                    Nota: Negócios na fase "Pendência" são contabilizados como fechamento.

                    ### CONTEXTO DOS DADOS FILTRADOS:
                    {contexto}

                    ---
                    PERGUNTA DO USUÁRIO:
                    {user_question}

                    ---
                    Responda de forma clara, direta e bem formatada (use negritos, tópicos ou tabelas se necessário).
                    """

                    client = anthropic.Anthropic(api_key=claude_api_key_input.strip())
                    response = client.messages.create(
                        model=claude_model_option,
                        max_tokens=1500,
                        temperature=0.5,
                        system=(
                            "Você é um assistente virtual especialista em análise de"
                            " dados de Segurança do Trabalho."
                        ),
                        messages=[{"role": "user", "content": prompt_custom}],
                    )

                    st.markdown("### 💡 Resposta da IA")
                    st.success(response.content[0].text)

                except Exception as e:
                    st.error(f"❌ **Erro ao processar pergunta:** {e}")
      
