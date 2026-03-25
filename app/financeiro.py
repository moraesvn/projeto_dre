import streamlit as st
from dataclasses import dataclass
from db import get_kpi_base
from kpi import montar_kpis

#st.set_page_config(page_title="Núcleo Financeiro", page_icon="💹", layout="wide")

# -------------------------------------------------------------------
# Leitura dos filtros globais (definidos no main.py)
# -------------------------------------------------------------------
filtros = st.session_state.get("filtros")
if not filtros:
    st.info("Use a barra lateral no menu principal para selecionar os filtros.")
    st.stop()


df_base = get_kpi_base(filtros.empresas, filtros.anos, filtros.mes_ini, filtros.mes_fim)
if df_base.empty:
    st.info("Nenhum dado para os filtros selecionados.")
    st.stop()

st.session_state["kpis_financeiro"] = montar_kpis(df_base)
# -------------------------------------------------------------------
# KPIs em destaque: Receita Bruta e Receita Líquida (período, YTD, YoY)
# -------------------------------------------------------------------
@dataclass
class KPI:
    label: str
    valor: float | None = None
    ytd: float | None = None
    crescimento_yoy: float | None = None


def fmt_val(v: float | None) -> str:
    if v is None:
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(p: float | None, casas: int = 1) -> str:
    if p is None:
        return "—"
    return f"{p:.{casas}f}%"


kpis = {
    "receita_bruta": KPI("Receita Bruta", valor=None, ytd=None, crescimento_yoy=None),
    "receita_liquida": KPI("Receita Líquida", valor=None, ytd=None, crescimento_yoy=None),
}

# Se já existir algo calculado no session_state, usa
kpis_state = st.session_state.get("kpis_financeiro")
if isinstance(kpis_state, dict):
    for key, obj in kpis.items():
        data = kpis_state.get(key, {})
        obj.valor = data.get("valor", obj.valor)
        obj.ytd = data.get("ytd", obj.ytd)
        obj.crescimento_yoy = data.get("crescimento_yoy", obj.crescimento_yoy)

st.header("💹 Visão estratégica")

c1, c2 = st.columns(2)
with c1:
    rb = kpis["receita_bruta"]
    st.metric(rb.label, fmt_val(rb.valor), fmt_pct(rb.crescimento_yoy))
    st.caption(f"YTD: {fmt_val(rb.ytd)}")
    st.caption(f"Crescimento YoY: {fmt_pct(rb.crescimento_yoy)}")

with c2:
    rl = kpis["receita_liquida"]
    st.metric(rl.label, fmt_val(rl.valor), fmt_pct(rl.crescimento_yoy))
    st.caption(f"YTD: {fmt_val(rl.ytd)}")
    st.caption(f"Crescimento YoY: {fmt_pct(rl.crescimento_yoy)}")

st.divider()

from chat_ui import render_chat
from ai.service import ask_cfo

render_chat("financeiro", filtros, on_ask=ask_cfo)
