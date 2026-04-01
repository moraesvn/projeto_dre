import streamlit as st
from db import get_dimensoes
from ui import mostrar_filtros, Filtros

# -------------------------------------------------
# Config geral do app (apenas no entrypoint)
# -------------------------------------------------
st.set_page_config(page_title="Executivo", page_icon="📊", layout="wide")

#st.sidebar.image("gp_logo.jpg")

#st.title("📊 DRE – Navegação e Filtros Globais")

# -------------------------------------------------
# Navegação por páginas (novo modelo Page + navigation)
# Cada arquivo .py de página fica neste mesmo diretório `app/`
# -------------------------------------------------
financeiro_page = st.Page(
    "financeiro.py",
    title="Núcleo Financeiro",
    icon="💹",
)

despesas_page = st.Page(
    "comercial_operacional.py",
    title="Comercial e Operacional",
    icon="📦",
)

personalizado_page = st.Page(
    "painel_personalizado.py",
    title="Painel Personalizado",
    icon="⚙️",
)

configuracoes_page = st.Page(
    "configuracoes.py",
    title="Configurações",
    icon="🔧",
)

# Você pode agrupar páginas em seções, se quiser (ex.: "Visões")
nav = st.navigation({
    "Visualizações": [
        financeiro_page,
        despesas_page,
        personalizado_page,
        configuracoes_page,
    ],
})

# -------------------------------------------------
# Filtros globais (sidebar) — válidos para TODAS as páginas
# -------------------------------------------------
empresas_opts, anos_opts = get_dimensoes()
if not empresas_opts or not anos_opts:
    st.warning("Base vazia ou conexão ausente. Insira dados no SQLite para começar.")
else:
    filtros: Filtros = mostrar_filtros(empresas_opts, anos_opts)

    # Salva no session_state para as páginas consumirem
    st.session_state["filtros"] = filtros


# -------------------------------------------------
# Renderiza a página selecionada
# (cada página lê st.session_state["filtros"] para aplicar os filtros)
# -------------------------------------------------
nav.run()
