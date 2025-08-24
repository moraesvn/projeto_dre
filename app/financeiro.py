# financeiro.py
import streamlit as st

st.header("💹 Núcleo Financeiro")

filtros = st.session_state.get("filtros")
if not filtros:
    st.info("Use a barra lateral para selecionar filtros.")
    st.stop()

# daqui pra frente, só conteúdo da página (consultas/gráficos), sem sidebar
