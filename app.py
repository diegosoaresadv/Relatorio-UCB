import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from datetime import datetime, date

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA  (deve ser 1ª chamada Streamlit)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Unimed – Gestão de Processos Judiciais",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# AUTENTICAÇÃO POR SENHA
# ─────────────────────────────────────────────
def check_password() -> bool:
    """
    Exibe tela de login e retorna True apenas quando a senha
    bater com o valor em .streamlit/secrets.toml → password.
    """

    def _verificar():
        if st.session_state.get("_pwd_input") == st.secrets.get("password", ""):
            st.session_state["_autenticado"] = True
        else:
            st.session_state["_autenticado"] = False
            st.session_state["_pwd_errada"] = True

    if st.session_state.get("_autenticado"):
        return True

    # ── Tela de login ──
    col_c, col_form, col_d = st.columns([1, 2, 1])
    with col_form:
        st.markdown("<br><br>", unsafe_allow_html=True)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔒 Acesso Restrito")
        st.text_input(
            "Senha de acesso:",
            type="password",
            key="_pwd_input",
            on_change=_verificar,
        )
        if st.session_state.get("_pwd_errada"):
            st.error("Senha incorreta. Tente novamente.")

    return False


# ─────────────────────────────────────────────
# CSS CUSTOMIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --unimed-green: #00843D;
        --unimed-dark:  #005C2A;
        --unimed-light: #E8F5EE;
    }
    section[data-testid="stSidebar"] {
        background-color: var(--unimed-dark) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        font-size: 15px !important;
    }
    div[data-testid="metric-container"] {
        background-color: var(--unimed-light);
        border-left: 5px solid var(--unimed-green);
        padding: 12px 16px;
        border-radius: 8px;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--unimed-green) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--unimed-dark) !important;
    }
    .header-title {
        color: var(--unimed-green);
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .header-sub {
        color: #555;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    .dataframe tbody tr:nth-child(odd) { background-color: #f7fcf9; }
    hr { border-top: 2px solid var(--unimed-green); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES / LISTAS DE OPÇÕES
# ─────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "processos.csv")

ABAS = ["Passivo Tributario", "Ativo Tributario", "Arquivados"]

NATUREZA = ["Nao Tributária", "Tributária", "Cível"]

OBJETOS = sorted([
    "Ação de Execução Fiscal", "Embargos à Execução Fiscal", "Ação Anulatória",
    "Mandado de Segurança", "Ação Declaratória", "Ação Cautelar com Depósito",
    "Suspensão da Exigibilidade do Débito", "Depósito/ Garantia para Suspensão da Exigibilidade",
    "AGRAVO DE INSTRUMENTO", "Cautelar", "Execução",
    "Contribuições Previdenciárias",
    "DESCONSTITUTIVA DE AUTOS DE INFRAÇÃO E APREENSÃO C/C ANTECIPAÇÃO DE TUTELA",
    "Compensação. ICMS. Descontos Incondicionais.",
])

POSICAO = ["Executado", "Réu", "Autor", "Exequente", "IMPETRANTE"]

PEDIDOS_NOME = [
    "Obrigação de Fazer", "Obrigação de Pagar",
    "Obrigação de Pagar (Ressarcimento SUS)",
    "Declaratória", "Nulidade de Crédito Tributário",
]

CONTINGENCIA = ["Passiva", "Ativa"]

FASE = sorted([
    "Sem sentença", "Sentenciado", "Sentença Favorável",
    "Apelação - Aguardando julgamento de recurso pelo TRF1",
    "Recurso de Apelação aguardando Julgamento",
    "Transitada em Julgado", "Transitado Julgado", "Transitado Julgado/ Pagamento",
    "Transitado Julgado/ Pagamento Realizado (Baixar Contingência)",
    "Transitado Julgado/ Inclusão no REFIS",
    "Arquivado", "Arquivado Provisoriamente",
    "Cumprimento de sentença - Honorários",
    "Aguardando Citação da Parte Contrária",
    "Após Sentença - aguardando recurso",
    "Recurso Julgado - Aguardando Tribunal Superior",
    "Processo Sobrestado - Aguardando processamento do RE da UNIAO.",
    "Suspensa por Depender de Julgamento do Tema n.",
    "Processo com transito em julgado registrado em razão da perda de objeto",
    "Sentença de Desistência", "Sentença homologatoria da desistencia",
    "Transito em julgado",
])

PROBABILIDADE = ["Provável", "Possível", "Remota"]

MATERIA = sorted([
    "Multa", "Multa por Infracao Adminisrativa",
    "Multa Pecuniária por Infração Administrativa",
    "Anulação de Multa Administrativa", "Ressarcimento SUS",
    "Multa. Ressarcimento SUS. Autorizacao de Internacao Hospitalar.",
    "ICMS", "PIS E COFINS", "FGTS", "Taxas",
    "TUST E TUDS sobre ICMS", "Exclusao do ISS da Base de Claculo do PIS COFINS",
    "Inexigibildade de Tributo", "Inexigibilidade de pagamento de FGTS.",
    "Inexigiblidade de Pagamento de TSS", "Infracao a Concorrencia",
    "Excucao Fiscal  Multa em Processo Licitatorio",
    "Contribuições Previdenciárias",
])

RISCO = ["Alto", "Médio", "Baixo"]

ACOES = sorted([
    "Execução fiscal", "Embargos à Execução Fiscal",
    "Ação Anulatória de Débito Fiscal C/C Liminar",
    "Ação Anulatória de Débito Fiscal C/C Protesto",
    "Ação Anulatória de Débito Fiscal C/C Protesto. ICMS",
    "Ação Declaratória de Inexistência de Débito C/C Pedido Liminar",
    "Ação Declaratória de Inexistência de relação Jurídico - Tributária C/C Repetição de Indébito com pedido de Tutela Provisória de Evidência",
    "Mandado de segurança", "Mandado de segurança Com Pedido de Medida Liminar",
    "Anulação de ato administrativo", "Anulatória. Auto de Infração.",
    "Declaratória", "Caução", "Caução. ICMS. Inexigibilidade do Débito.",
    "Cautelar de protestos, notificações e interpelações",
    "Execução de Título Extrajudicial", "procedimento comum",
    "EMBARGOS A EXECUÇÃO",
    "AÇÃO ORDINARIA DE COMPENSAÇÃO C/C PEDIDO INCIDENTAL DE INCONSTITUCIONALIDADE .",
    "AGRAVO DE INSTRUMENTO c/c PEDIDO DE EFEITO ATIVO (ANTECIPAÇÃO DE TUTELA RECURSAL)",
    "DESCONSTITUTIVA DE AUTOS DE INFRAÇÃO E APREENSÃO C/C ANTECIPAÇÃO DE TUTELA",
])

STATUS = ["Ativo", "Suspenso", "Parcialmente Suspenso", "Arquivado", "Baixado", "Inativo"]

COLUNAS = [
    "aba", "contrario_principal_nome_razao_social", "numero_de_cnj", "natureza",
    "objetos_nome", "cliente_principal_posicao", "valor_da_causa", "pedidos_nome",
    "pedidos_contingencia", "fase", "faixa_de_probabilidade_de_perda_p_a_unimed",
    "custas", "garantias_depositos_deposito_integral", "garantias_depositos_valor",
    "valor_estimado_de_perda_provisao_p_contingencias", "andamentos_data",
    "materia", "processo_administrativo", "andamentos_descricao",
    "risco", "acao", "status",
]

LABELS = {
    "aba": "Aba / Categoria",
    "contrario_principal_nome_razao_social": "Parte Contrária",
    "numero_de_cnj": "Número CNJ",
    "natureza": "Natureza",
    "objetos_nome": "Objeto da Ação",
    "cliente_principal_posicao": "Posição do Cliente",
    "valor_da_causa": "Valor da Causa (R$)",
    "pedidos_nome": "Pedido",
    "pedidos_contingencia": "Contingência",
    "fase": "Fase Processual",
    "faixa_de_probabilidade_de_perda_p_a_unimed": "Probabilidade de Perda",
    "custas": "Custas Processuais",
    "garantias_depositos_deposito_integral": "Garantia / Depósito",
    "garantias_depositos_valor": "Valor da Garantia (R$)",
    "valor_estimado_de_perda_provisao_p_contingencias": "Provisão / Valor Estimado de Perda (R$)",
    "andamentos_data": "Data do Último Andamento",
    "materia": "Matéria",
    "processo_administrativo": "Processo Administrativo",
    "andamentos_descricao": "Descrição / Andamento",
    "risco": "Risco",
    "acao": "Tipo de Ação",
    "status": "Status",
}

# ─────────────────────────────────────────────
# CARREGAMENTO E PERSISTÊNCIA DE DADOS
# ─────────────────────────────────────────────

def normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
    mapa_prob  = {"Provavel": "Provável", "Remoto": "Remota"}
    mapa_risco = {"Medio": "Médio"}
    col_prob = "faixa_de_probabilidade_de_perda_p_a_unimed"
    if col_prob in df.columns:
        df[col_prob] = df[col_prob].replace(mapa_prob)
    if "risco" in df.columns:
        df["risco"] = df["risco"].replace(mapa_risco)
    return df


@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        # dtype=object evita ArrowDtype em pandas 2.x / Python 3.12+
        df = pd.read_csv(DATA_PATH, index_col=0, dtype=object).fillna("")
    else:
        df = pd.DataFrame(columns=COLUNAS)
    for col in COLUNAS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUNAS]
    # Garante que todas as colunas sejam strings puras (object)
    df = df.astype(str).replace("nan", "")
    df = normalizar_valores(df)
    df = df.reset_index(drop=True)
    return df


def salvar_dados(df: pd.DataFrame):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df = df.reset_index(drop=True)          # garante índice contínuo antes de salvar
    df.to_csv(DATA_PATH)
    st.cache_data.clear()


def inicializar_estado():
    if "df" not in st.session_state:
        st.session_state.df = carregar_dados()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "📊 Dashboard"


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fmt_moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def opcao_com_outro(lista, label, key, valor_atual=""):
    opcoes = lista + ["✏️ Outro (digitar)"]
    idx = 0
    if valor_atual in lista:
        idx = lista.index(valor_atual)
    elif valor_atual:
        idx = len(lista)
    escolha = st.selectbox(label, opcoes, index=idx, key=key)
    if escolha == "✏️ Outro (digitar)":
        return st.text_input(
            f"{label} (texto livre)",
            value=valor_atual if valor_atual not in lista else "",
            key=f"{key}_livre",
        )
    return escolha


# ─────────────────────────────────────────────
# SIDEBAR / NAVEGAÇÃO
# ─────────────────────────────────────────────

def renderizar_sidebar():
    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        st.markdown("---")
        st.markdown("### Navegação")

        paginas = [
            "📊 Dashboard",
            "➕ Cadastrar Processo",
            "📋 Processos Cadastrados",
            "📄 Relatório e Exportação",
        ]
        escolha = st.radio(
            "",
            paginas,
            key="nav_radio",
            index=paginas.index(st.session_state.get("pagina", paginas[0])),
        )
        st.session_state.pagina = escolha

        st.markdown("---")
        df = st.session_state.df
        st.markdown(f"**Total de processos:** {len(df)}")
        ativos = (df["status"] == "Ativo").sum()
        st.markdown(f"**Processos ativos:** {ativos}")
        st.markdown("---")
        st.markdown(
            "<small style='color:#aaa'>Unimed Cuiabá · Jurídico & Contábil</small>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# PÁGINA 1 – DASHBOARD
# ─────────────────────────────────────────────

def pagina_dashboard():
    st.markdown('<p class="header-title">📊 Dashboard – Processos Judiciais</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Visão geral consolidada dos processos acompanhados pelo Jurídico e Contábil</p>', unsafe_allow_html=True)

    df = st.session_state.df.copy()
    for col in ["valor_da_causa", "valor_estimado_de_perda_provisao_p_contingencias", "garantias_depositos_valor"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    total          = len(df)
    ativos         = (df["status"] == "Ativo").sum()
    total_causa    = df["valor_da_causa"].sum()
    total_provisao = df["valor_estimado_de_perda_provisao_p_contingencias"].sum()
    total_garantia = df["garantias_depositos_valor"].sum()
    provaveis      = (df["faixa_de_probabilidade_de_perda_p_a_unimed"] == "Provável").sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total de Processos",    total)
    c2.metric("Processos Ativos",      int(ativos))
    c3.metric("Valor Total das Causas", fmt_moeda(total_causa))
    c4.metric("Total Provisionado",    fmt_moeda(total_provisao))
    c5.metric("Total em Garantias",    fmt_moeda(total_garantia))
    c6.metric("Perda Provável",        int(provaveis))

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Distribuição por Status")
        ct = df["status"].value_counts().reset_index()
        ct.columns = ["Status", "Quantidade"]
        fig = px.pie(ct, names="Status", values="Quantidade",
                     color_discrete_sequence=px.colors.sequential.Greens_r, hole=0.4)
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Probabilidade de Perda")
        ct2 = df["faixa_de_probabilidade_de_perda_p_a_unimed"].value_counts().reset_index()
        ct2.columns = ["Probabilidade", "Quantidade"]
        cores = {"Provável": "#C0392B", "Possível": "#E67E22", "Remota": "#27AE60"}
        fig2 = px.bar(ct2, x="Probabilidade", y="Quantidade",
                      color="Probabilidade", color_discrete_map=cores, text_auto=True)
        fig2.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Processos por Aba / Categoria")
        ct3 = df["aba"].value_counts().reset_index()
        ct3.columns = ["Aba", "Quantidade"]
        fig3 = px.bar(ct3, x="Aba", y="Quantidade",
                      color="Aba",
                      color_discrete_sequence=["#00843D", "#005C2A", "#66BB6A"],
                      text_auto=True)
        fig3.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.subheader("Provisão por Probabilidade de Perda (R$)")
        prov = df.groupby("faixa_de_probabilidade_de_perda_p_a_unimed")[
            "valor_estimado_de_perda_provisao_p_contingencias"
        ].sum().reset_index()
        prov.columns = ["Probabilidade", "Provisão Total"]
        fig4 = px.bar(prov, x="Probabilidade", y="Provisão Total",
                      color="Probabilidade", color_discrete_map=cores, text_auto=True)
        fig4.update_layout(showlegend=False, margin=dict(t=20, b=20))
        fig4.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("🔝 Top 10 Maiores Provisões")
    top10 = (
        df[df["valor_estimado_de_perda_provisao_p_contingencias"] > 0]
        .nlargest(10, "valor_estimado_de_perda_provisao_p_contingencias")
        [[
            "numero_de_cnj", "contrario_principal_nome_razao_social",
            "acao", "status",
            "faixa_de_probabilidade_de_perda_p_a_unimed",
            "valor_estimado_de_perda_provisao_p_contingencias",
        ]]
        .rename(columns={
            "numero_de_cnj": "Nº CNJ",
            "contrario_principal_nome_razao_social": "Parte Contrária",
            "acao": "Ação",
            "status": "Status",
            "faixa_de_probabilidade_de_perda_p_a_unimed": "Probabilidade",
            "valor_estimado_de_perda_provisao_p_contingencias": "Provisão (R$)",
        })
    )
    top10["Provisão (R$)"] = top10["Provisão (R$)"].apply(fmt_moeda)
    st.dataframe(top10, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# FORMULÁRIO GENÉRICO DE PROCESSO
# ─────────────────────────────────────────────

def formulario_processo(dados: dict = None, prefixo: str = "new") -> dict:
    d = dados or {}

    def v(col, default=""):
        val = d.get(col, default)
        return "" if pd.isna(val) else str(val)

    def vf(col):
        try:
            return float(v(col, 0)) if v(col) else 0.0
        except Exception:
            return 0.0

    st.markdown("#### 📁 Identificação e Classificação")
    c1, c2, c3 = st.columns(3)
    with c1:
        aba = st.selectbox(LABELS["aba"], ABAS,
                           index=ABAS.index(v("aba")) if v("aba") in ABAS else 0,
                           key=f"{prefixo}_aba")
    with c2:
        natureza = st.selectbox(LABELS["natureza"], NATUREZA,
                                index=NATUREZA.index(v("natureza")) if v("natureza") in NATUREZA else 0,
                                key=f"{prefixo}_natureza")
    with c3:
        status_val = st.selectbox(LABELS["status"], STATUS,
                                  index=STATUS.index(v("status")) if v("status") in STATUS else 0,
                                  key=f"{prefixo}_status")

    c4, c5 = st.columns(2)
    with c4:
        cnj = st.text_input(LABELS["numero_de_cnj"], value=v("numero_de_cnj"),
                            placeholder="0000000-00.0000.0.00.0000",
                            key=f"{prefixo}_cnj")
    with c5:
        contrario = st.text_input(LABELS["contrario_principal_nome_razao_social"],
                                  value=v("contrario_principal_nome_razao_social"),
                                  key=f"{prefixo}_contrario")

    c6, c7 = st.columns(2)
    with c6:
        objeto = opcao_com_outro(OBJETOS, LABELS["objetos_nome"], f"{prefixo}_objeto", v("objetos_nome"))
    with c7:
        acao = opcao_com_outro(ACOES, LABELS["acao"], f"{prefixo}_acao", v("acao"))

    st.markdown("---")
    st.markdown("#### ⚖️ Partes e Pedidos")
    c8, c9, c10 = st.columns(3)
    with c8:
        posicao = st.selectbox(LABELS["cliente_principal_posicao"], POSICAO,
                               index=POSICAO.index(v("cliente_principal_posicao")) if v("cliente_principal_posicao") in POSICAO else 0,
                               key=f"{prefixo}_posicao")
    with c9:
        pedido = st.selectbox(LABELS["pedidos_nome"], PEDIDOS_NOME,
                              index=PEDIDOS_NOME.index(v("pedidos_nome")) if v("pedidos_nome") in PEDIDOS_NOME else 0,
                              key=f"{prefixo}_pedido")
    with c10:
        contingencia = st.selectbox(LABELS["pedidos_contingencia"], CONTINGENCIA,
                                    index=CONTINGENCIA.index(v("pedidos_contingencia")) if v("pedidos_contingencia") in CONTINGENCIA else 0,
                                    key=f"{prefixo}_contingencia")

    st.markdown("---")
    st.markdown("#### 💰 Valores e Provisão")
    c11, c12, c13 = st.columns(3)
    with c11:
        valor_causa = st.number_input(LABELS["valor_da_causa"], min_value=0.0, step=100.0,
                                      format="%.2f", value=vf("valor_da_causa"),
                                      key=f"{prefixo}_valor_causa")
    with c12:
        valor_garantia = st.number_input(LABELS["garantias_depositos_valor"], min_value=0.0, step=100.0,
                                         format="%.2f", value=vf("garantias_depositos_valor"),
                                         key=f"{prefixo}_valor_garantia")
    with c13:
        provisao = st.number_input(LABELS["valor_estimado_de_perda_provisao_p_contingencias"],
                                   min_value=0.0, step=100.0, format="%.2f",
                                   value=vf("valor_estimado_de_perda_provisao_p_contingencias"),
                                   key=f"{prefixo}_provisao")

    c14, c15 = st.columns(2)
    with c14:
        garantia_tipo = st.text_input(LABELS["garantias_depositos_deposito_integral"],
                                      value=v("garantias_depositos_deposito_integral"),
                                      placeholder="Ex: Depósito Judicial, Parcelamento…",
                                      key=f"{prefixo}_garantia_tipo")
    with c15:
        custas = st.text_input(LABELS["custas"], value=v("custas"),
                               placeholder="Informar custas se houver",
                               key=f"{prefixo}_custas")

    st.markdown("---")
    st.markdown("#### 📌 Risco, Fase e Probabilidade")
    c16, c17, c18 = st.columns(3)
    with c16:
        risco = st.selectbox(LABELS["risco"], RISCO,
                             index=RISCO.index(v("risco")) if v("risco") in RISCO else 1,
                             key=f"{prefixo}_risco")
    with c17:
        prob = st.selectbox(LABELS["faixa_de_probabilidade_de_perda_p_a_unimed"], PROBABILIDADE,
                            index=PROBABILIDADE.index(v("faixa_de_probabilidade_de_perda_p_a_unimed"))
                            if v("faixa_de_probabilidade_de_perda_p_a_unimed") in PROBABILIDADE else 1,
                            key=f"{prefixo}_prob")
    with c18:
        fase = opcao_com_outro(FASE, LABELS["fase"], f"{prefixo}_fase", v("fase"))

    st.markdown("---")
    st.markdown("#### 📚 Matéria e Processo Administrativo")
    c19, c20 = st.columns(2)
    with c19:
        materia = opcao_com_outro(MATERIA, LABELS["materia"], f"{prefixo}_materia", v("materia"))
    with c20:
        proc_adm = st.text_input(LABELS["processo_administrativo"],
                                 value=v("processo_administrativo"),
                                 key=f"{prefixo}_proc_adm")

    st.markdown("---")
    st.markdown("#### 📝 Andamento Processual")
    c21, _ = st.columns([1, 2])
    with c21:
        data_str  = v("andamentos_data")
        data_val  = date.today()
        if data_str:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    data_val = datetime.strptime(data_str.split(" ")[0], fmt.split(" ")[0]).date()
                    break
                except Exception:
                    pass
        and_data = st.date_input(LABELS["andamentos_data"], value=data_val,
                                 key=f"{prefixo}_and_data", format="DD/MM/YYYY")

    descricao = st.text_area(LABELS["andamentos_descricao"], value=v("andamentos_descricao"),
                             height=140, key=f"{prefixo}_descricao")

    return {
        "aba": aba,
        "contrario_principal_nome_razao_social": contrario,
        "numero_de_cnj": cnj,
        "natureza": natureza,
        "objetos_nome": objeto,
        "cliente_principal_posicao": posicao,
        "valor_da_causa": valor_causa,
        "pedidos_nome": pedido,
        "pedidos_contingencia": contingencia,
        "fase": fase,
        "faixa_de_probabilidade_de_perda_p_a_unimed": prob,
        "custas": custas,
        "garantias_depositos_deposito_integral": garantia_tipo,
        "garantias_depositos_valor": valor_garantia,
        "valor_estimado_de_perda_provisao_p_contingencias": provisao,
        "andamentos_data": str(and_data),
        "materia": materia,
        "processo_administrativo": proc_adm,
        "andamentos_descricao": descricao,
        "risco": risco,
        "acao": acao,
        "status": status_val,
    }


# ─────────────────────────────────────────────
# PÁGINA 2 – CADASTRAR PROCESSO
# ─────────────────────────────────────────────

def pagina_cadastro():
    st.markdown('<p class="header-title">➕ Cadastrar Novo Processo</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Preencha todos os campos para registrar um novo processo judicial.</p>', unsafe_allow_html=True)

    with st.form("form_cadastro", clear_on_submit=True):
        dados     = formulario_processo(prefixo="cad")
        submitted = st.form_submit_button("💾 Salvar Processo", type="primary", use_container_width=True)

    if submitted:
        if not dados["numero_de_cnj"].strip():
            st.error("⚠️ O Número CNJ é obrigatório.")
        elif dados["numero_de_cnj"] in st.session_state.df["numero_de_cnj"].values:
            st.error(f"⚠️ Já existe um processo com o CNJ **{dados['numero_de_cnj']}**.")
        else:
            # Converte todos os valores para str antes de concatenar
            dados_str = {k: ("" if v is None else str(v)) for k, v in dados.items()}
            novo = pd.DataFrame([dados_str])
            st.session_state.df = pd.concat(
                [st.session_state.df, novo], ignore_index=True
            )
            salvar_dados(st.session_state.df)
            st.success(f"✅ Processo **{dados['numero_de_cnj']}** cadastrado com sucesso!")
            st.balloons()


# ─────────────────────────────────────────────
# PÁGINA 3 – PROCESSOS CADASTRADOS
# ─────────────────────────────────────────────

def pagina_processos():
    st.markdown('<p class="header-title">📋 Processos Cadastrados</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Consulte, edite ou exclua processos existentes.</p>', unsafe_allow_html=True)

    df = st.session_state.df.copy()

    with st.expander("🔍 Filtros de Busca", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            f_status = st.multiselect("Status", STATUS, default=[])
        with fc2:
            f_prob   = st.multiselect("Probabilidade de Perda", PROBABILIDADE, default=[])
        with fc3:
            f_aba    = st.multiselect("Aba", ABAS, default=[])
        with fc4:
            f_texto  = st.text_input("Busca por CNJ ou Parte Contrária", "")

    # ── Máscara com index alinhado (evita IndexingError) ──
    mask = pd.Series([True] * len(df), index=df.index)
    if f_status:
        mask &= df["status"].isin(f_status)
    if f_prob:
        mask &= df["faixa_de_probabilidade_de_perda_p_a_unimed"].isin(f_prob)
    if f_aba:
        mask &= df["aba"].isin(f_aba)
    if f_texto:
        t = f_texto.lower()
        mask &= (
            df["numero_de_cnj"].str.lower().str.contains(t, na=False) |
            df["contrario_principal_nome_razao_social"].str.lower().str.contains(t, na=False)
        )

    df_filtrado = df[mask].copy()
    st.info(f"Exibindo **{len(df_filtrado)}** processo(s) de **{len(df)}** no total.")

    if df_filtrado.empty:
        st.warning("Nenhum processo encontrado com os filtros aplicados.")
        return

    colunas_tabela = [
        "numero_de_cnj", "contrario_principal_nome_razao_social",
        "acao", "fase", "status",
        "faixa_de_probabilidade_de_perda_p_a_unimed",
        "valor_da_causa", "valor_estimado_de_perda_provisao_p_contingencias",
    ]
    df_view = df_filtrado[colunas_tabela].rename(columns={
        "numero_de_cnj": "Nº CNJ",
        "contrario_principal_nome_razao_social": "Parte Contrária",
        "acao": "Tipo de Ação",
        "fase": "Fase",
        "status": "Status",
        "faixa_de_probabilidade_de_perda_p_a_unimed": "Probabilidade",
        "valor_da_causa": "Valor da Causa",
        "valor_estimado_de_perda_provisao_p_contingencias": "Provisão",
    })
    for col in ["Valor da Causa", "Provisão"]:
        df_view[col] = pd.to_numeric(df_view[col], errors="coerce").apply(
            lambda x: fmt_moeda(x) if pd.notna(x) and x > 0 else "—"
        )
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Editar ou Excluir Processo")

    opcoes_cnj = df_filtrado["numero_de_cnj"].tolist()
    if not opcoes_cnj:
        return

    cnj_sel  = st.selectbox("Selecione o processo pelo Nº CNJ:", opcoes_cnj, key="sel_edicao")
    idx_real = df[df["numero_de_cnj"] == cnj_sel].index[0]

    tab_ed, tab_del = st.tabs(["✏️ Editar", "🗑️ Excluir"])

    with tab_ed:
        with st.form(f"form_edicao_{idx_real}"):
            dados_edit = formulario_processo(dados=df.loc[idx_real].to_dict(), prefixo=f"ed_{idx_real}")
            salvar_ed  = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        if salvar_ed:
            for col, val in dados_edit.items():
                # Converte para str para compatibilidade com ArrowDtype (pandas 2.x+)
                st.session_state.df.at[idx_real, col] = "" if val is None else str(val)
            salvar_dados(st.session_state.df)
            st.success("✅ Processo atualizado com sucesso!")
            st.rerun()

    with tab_del:
        st.warning(f"**Atenção:** Você está prestes a excluir o processo **{cnj_sel}**. Esta ação não pode ser desfeita.")
        confirmar = st.checkbox("Confirmo que desejo excluir este processo permanentemente.")
        if st.button("🗑️ Excluir Processo", type="primary", disabled=not confirmar):
            st.session_state.df = (
                st.session_state.df.drop(index=idx_real).reset_index(drop=True)
            )
            salvar_dados(st.session_state.df)
            st.success("✅ Processo excluído.")
            st.rerun()


# ─────────────────────────────────────────────
# PÁGINA 4 – RELATÓRIO E EXPORTAÇÃO
# ─────────────────────────────────────────────

def pagina_relatorio():
    st.markdown('<p class="header-title">📄 Relatório e Exportação</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Filtre os processos e exporte o relatório em CSV ou Excel.</p>', unsafe_allow_html=True)

    df = st.session_state.df.copy()

    st.subheader("🔧 Filtros Avançados")
    col1, col2, col3 = st.columns(3)
    with col1:
        r_aba    = st.multiselect("Aba / Categoria", ABAS,        key="r_aba")
        r_status = st.multiselect("Status",          STATUS,      key="r_status")
    with col2:
        r_prob   = st.multiselect("Probabilidade de Perda", PROBABILIDADE, key="r_prob")
        r_risco  = st.multiselect("Risco",                  RISCO,         key="r_risco")
    with col3:
        r_nat    = st.multiselect("Natureza",     NATUREZA,    key="r_nat")
        r_cont   = st.multiselect("Contingência", CONTINGENCIA, key="r_cont")

    col4, col5 = st.columns(2)
    with col4:
        r_val_min = st.number_input("Valor da Causa – Mínimo (R$)", min_value=0.0, value=0.0, step=1000.0, key="r_val_min")
    with col5:
        r_val_max = st.number_input("Valor da Causa – Máximo (R$, 0 = sem limite)", min_value=0.0, value=0.0, step=1000.0, key="r_val_max")

    df["valor_da_causa_num"] = pd.to_numeric(df["valor_da_causa"], errors="coerce").fillna(0)

    # ── Máscara com index alinhado (evita IndexingError) ──
    mask = pd.Series([True] * len(df), index=df.index)
    if r_aba:    mask &= df["aba"].isin(r_aba)
    if r_status: mask &= df["status"].isin(r_status)
    if r_prob:   mask &= df["faixa_de_probabilidade_de_perda_p_a_unimed"].isin(r_prob)
    if r_risco:  mask &= df["risco"].isin(r_risco)
    if r_nat:    mask &= df["natureza"].isin(r_nat)
    if r_cont:   mask &= df["pedidos_contingencia"].isin(r_cont)
    if r_val_min > 0: mask &= df["valor_da_causa_num"] >= r_val_min
    if r_val_max > 0: mask &= df["valor_da_causa_num"] <= r_val_max

    df_rel = df[mask][COLUNAS].copy()
    st.info(f"**{len(df_rel)}** processo(s) no relatório atual.")

    st.markdown("---")
    st.subheader("📊 Resumo Financeiro do Relatório")
    for col in ["valor_da_causa", "valor_estimado_de_perda_provisao_p_contingencias", "garantias_depositos_valor"]:
        df_rel[col] = pd.to_numeric(df_rel[col], errors="coerce").fillna(0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Processos",               len(df_rel))
    m2.metric("Valor Total das Causas",  fmt_moeda(df_rel["valor_da_causa"].sum()))
    m3.metric("Total Provisionado",      fmt_moeda(df_rel["valor_estimado_de_perda_provisao_p_contingencias"].sum()))
    m4.metric("Total em Garantias",      fmt_moeda(df_rel["garantias_depositos_valor"].sum()))

    st.markdown("---")
    st.subheader("📋 Processos no Relatório")
    st.dataframe(df_rel.rename(columns=LABELS), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("⬇️ Exportar Relatório")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.markdown("**Exportar como CSV**")
        csv_bytes = df_rel.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_bytes,
            file_name=f"relatorio_processos_{datetime.today().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_exp2:
        st.markdown("**Exportar como Excel (.xlsx)**")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_rel.rename(columns=LABELS).to_excel(writer, index=False, sheet_name="Processos")
            resumo = pd.DataFrame({
                "Indicador": [
                    "Total de Processos", "Valor Total das Causas",
                    "Total Provisionado", "Total em Garantias",
                    "Perda Provável", "Perda Possível", "Perda Remota",
                ],
                "Valor": [
                    len(df_rel),
                    df_rel["valor_da_causa"].sum(),
                    df_rel["valor_estimado_de_perda_provisao_p_contingencias"].sum(),
                    df_rel["garantias_depositos_valor"].sum(),
                    (df_rel["faixa_de_probabilidade_de_perda_p_a_unimed"] == "Provável").sum(),
                    (df_rel["faixa_de_probabilidade_de_perda_p_a_unimed"] == "Possível").sum(),
                    (df_rel["faixa_de_probabilidade_de_perda_p_a_unimed"] == "Remota").sum(),
                ],
            })
            resumo.to_excel(writer, index=False, sheet_name="Resumo")
        buf.seek(0)
        st.download_button(
            label="⬇️ Baixar Excel",
            data=buf.read(),
            file_name=f"relatorio_processos_{datetime.today().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown("---")
    st.subheader("📂 Importar CSV (Restaurar / Atualizar Base)")
    st.caption("Faça upload de um CSV previamente exportado para substituir a base de dados atual.")
    uploaded = st.file_uploader("Selecionar arquivo CSV", type=["csv"], key="upload_csv")
    if uploaded is not None:
        try:
            df_import = pd.read_csv(uploaded, dtype=str).fillna("")
            faltando  = [c for c in COLUNAS if c not in df_import.columns]
            if faltando:
                st.error(f"⚠️ Colunas ausentes no arquivo: {', '.join(faltando)}")
            else:
                df_import = normalizar_valores(df_import[COLUNAS])
                if st.button("✅ Confirmar Importação", type="primary"):
                    st.session_state.df = df_import
                    salvar_dados(df_import)
                    st.success(f"✅ Base atualizada com {len(df_import)} processo(s).")
                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao importar: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    # Bloqueia acesso até senha correta
    if not check_password():
        st.stop()

    inicializar_estado()
    renderizar_sidebar()

    pagina = st.session_state.pagina
    if pagina == "📊 Dashboard":
        pagina_dashboard()
    elif pagina == "➕ Cadastrar Processo":
        pagina_cadastro()
    elif pagina == "📋 Processos Cadastrados":
        pagina_processos()
    elif pagina == "📄 Relatório e Exportação":
        pagina_relatorio()


# ─────────────────────────────────────────────
# PONTO DE ENTRADA  ← estava faltando!
# ─────────────────────────────────────────────
main()
