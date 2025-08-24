# financeiro.py
import streamlit as st

st.header("💹 Núcleo Financeiro")

filtros = st.session_state.get("filtros")
if not filtros:
    st.info("Use a barra lateral para selecionar filtros.")
    st.stop()

st.write("Empresas:", ", ".join(filtros.empresas))
st.write("Anos:", ", ".join(map(str, filtros.anos)))
st.write("Intervalo:", f"{filtros.mes_ini}–{filtros.mes_fim}")

# daqui pra frente, só conteúdo da página (consultas/gráficos), sem sidebar
