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
# Estrutura visual dos 5 cards (sem cálculos por enquanto)
# KPIs em destaque (cards grandes no topo):
# 1) Receita Líquida (ano e YTD, % crescimento)
# 2) Margem Bruta %
# 3) Margem Operacional %
# 4) Margem Líquida %
# 5) EBITDA
# -------------------------------------------------------------------
@dataclass
class KPI:
    label: str
    valor: float | None = None          # valor principal (R$ ou %)
    ytd: float | None = None            # para RL: YTD em R$
    crescimento_yoy: float | None = None  # variação % YoY
    margem_pct: float | None = None     # para EBITDA (margem EBITDA %), se aplicável


def fmt_val(v: float | None) -> str:
    if v is None:
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(p: float | None, casas: int = 1) -> str:
    if p is None:
        return "—"
    return f"{p:.{casas}f}%"


# Placeholders dos KPIs (serão preenchidos depois via st.session_state["kpis_financeiro"])
kpis = {
    # Receita Líquida — Ano/YTD e crescimento YoY
    "receita_liquida": KPI("Receita Líquida", valor=None, ytd=None, crescimento_yoy=None),

    # Margens (%)
    "margem_bruta_pct": KPI("Margem Bruta %", valor=None, crescimento_yoy=None),
    "margem_operacional_pct": KPI("Margem Operacional %", valor=None, crescimento_yoy=None),
    "margem_liquida_pct": KPI("Margem Líquida %", valor=None, crescimento_yoy=None),

    # EBITDA — valor em R$ + margem % e crescimento YoY
    "ebitda": KPI("EBITDA", valor=None, margem_pct=None, crescimento_yoy=None),
}

# Se já existir algo calculado no session_state, usa
kpis_state = st.session_state.get("kpis_financeiro")
if isinstance(kpis_state, dict):
    for key, obj in kpis.items():
        data = kpis_state.get(key, {})
        obj.valor = data.get("valor", obj.valor)
        obj.ytd = data.get("ytd", obj.ytd)
        obj.crescimento_yoy = data.get("crescimento_yoy", obj.crescimento_yoy)
        obj.margem_pct = data.get("margem_pct", obj.margem_pct)

# -------------------------------------------------------------------
# Layout visual
# Linha 1: 2 cards grandes – Receita Líquida (esquerda) e EBITDA (direita)
# Linha 2: 3 cards – Margem Bruta %, Margem Operacional %, Margem Líquida %
# -------------------------------------------------------------------
st.header("💹 Visão estratégica")

# Linha 1: 2 cards grandes
c1, c2 = st.columns((2, 1))  # Receita Líquida ocupa mais espaço
with c1:
    rl = kpis["receita_liquida"]
    st.metric(rl.label, fmt_val(rl.valor), fmt_pct(rl.crescimento_yoy))
    st.caption(f"YTD: {fmt_val(rl.ytd)}")
    st.caption(f"Crescimento YoY: {fmt_pct(rl.crescimento_yoy)}")

with c2:
    ebt = kpis["ebitda"]
    st.metric(ebt.label, fmt_val(ebt.valor), fmt_pct(ebt.crescimento_yoy))
    st.caption(f"Margem EBITDA: {fmt_pct(ebt.margem_pct)}")
    st.caption(f"YoY: {fmt_pct(ebt.crescimento_yoy)}")

st.divider()

# Linha 2: 3 cards menores (margens)
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    mb = kpis["margem_bruta_pct"]
    st.metric(mb.label, fmt_pct(mb.valor))
    st.caption(f"YoY: {fmt_pct(mb.crescimento_yoy)}")

with r2c2:
    mo = kpis["margem_operacional_pct"]
    st.metric(mo.label, fmt_pct(mo.valor))
    st.caption(f"YoY: {fmt_pct(mo.crescimento_yoy)}")

with r2c3:
    ml = kpis["margem_liquida_pct"]
    st.metric(ml.label, fmt_pct(ml.valor))
    st.caption(f"YoY: {fmt_pct(ml.crescimento_yoy)}")

st.divider()

from chat_ui import render_chat
from ai.service import ask_cfo

render_chat("financeiro", filtros, on_ask=ask_cfo)
