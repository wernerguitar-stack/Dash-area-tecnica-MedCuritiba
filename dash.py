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
  df_raw["Tempo_Em_Dias"] = (end
