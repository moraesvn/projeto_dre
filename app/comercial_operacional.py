# pagina2.py
import streamlit as st

st.header(" Comercial e Operacional")

filtros = st.session_state.get("filtros")
if not filtros:
    st.info("Use a barra lateral para selecionar filtros.")
    st.stop()
