"""Página de configurações do aplicativo (preferências e importação de dados)."""
from __future__ import annotations

import streamlit as st

from db import get_dimensoes, get_kpi_base
from dre_import import executar_importacao, preparar_dados_upload

_STAGING_KEY = "_dre_import_staging"


@st.dialog("Confirmar importação", width="medium")
def dialog_confirmar_importacao() -> None:
    st.markdown("Os dados existentes desta **empresa** e **ano** serão **substituídos** pelos novos dados.")
    s = st.session_state.get(_STAGING_KEY)
    if not s:
        st.info("Nenhuma importação pendente.")
        return

    st.write(f"**Arquivo:** {s['filename']}")
    st.write(f"**Empresa:** {s['empresa']} | **Ano:** {s['ano']}")
    st.write(f"**Linhas a importar:** {len(s['df'])}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", use_container_width=True):
            del st.session_state[_STAGING_KEY]
            st.rerun()
    with c2:
        if st.button("Confirmar", type="primary", use_container_width=True):
            ok, msg = executar_importacao(s["df"], s["ano"], s["empresa"])
            if ok:
                get_dimensoes.clear()
                get_kpi_base.clear()
                del st.session_state[_STAGING_KEY]
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


st.header("Configurações")
st.caption("Preferências e opções do aplicativo.")

st.subheader("Importar DRE")
st.caption("Importe o arquivo Excel do DRE; escolha empresa (SP ou SC) e o ano de referência.")

uploaded = st.file_uploader("Arquivo (.xlsx)", type=["xlsx"], help="Formato esperado: o mesmo usado pelo pipeline ETL do projeto.")

col_a, col_b = st.columns(2)
with col_a:
    ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2024, step=1)
with col_b:
    empresa = st.selectbox("Empresa", ["SP", "SC"], index=0)

if st.button("Importar dados", type="primary"):
    if uploaded is None:
        st.warning("Selecione um arquivo Excel (.xlsx).")
    else:
        ok_prep, err_prep, df = preparar_dados_upload(uploaded.getvalue(), int(ano), empresa)
        if not ok_prep or df is None:
            st.error(f"Erro ao processar a planilha: {err_prep}")
        else:
            st.session_state[_STAGING_KEY] = {
                "filename": uploaded.name,
                "ano": int(ano),
                "empresa": empresa,
                "df": df,
            }
            dialog_confirmar_importacao()
