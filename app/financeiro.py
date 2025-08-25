import streamlit as st
from dataclasses import dataclass

#st.set_page_config(page_title="Núcleo Financeiro", page_icon="💹", layout="wide")

# -------------------------------------------------------------------
# Leitura dos filtros globais (definidos no main.py)
# -------------------------------------------------------------------
filtros = st.session_state.get("filtros")
if not filtros:
    st.info("Use a barra lateral no menu principal para selecionar os filtros.")
    st.stop()

# -------------------------------------------------------------------
# Estrutura visual dos 6 cards (sem cálculos por enquanto)
# - Mostra placeholders até conectarmos os cálculos/queries
# - Quando os KPIs estiverem prontos, basta preencher o dicionário 'kpis'
# -------------------------------------------------------------------
@dataclass
class KPI:
    label: str
    valor: float | None = None
    delta_mom: float | None = None  # variação mês contra mês (%)
    delta_yoy: float | None = None  # variação ano contra ano (%)
    sublabel: str | None = None     # ex.: Margem %, % da RL


def fmt_val(v: float | None) -> str:
    if v is None:
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(p: float | None) -> str:
    if p is None:
        return "—"
    return f"{p:.1f}%"


# Placeholder de KPIs (valores serão conectados depois)
kpis = {
    "rl": KPI("Receita Líquida", valor=None, delta_mom=None, delta_yoy=None),
    "lb": KPI("Lucro Bruto", valor=None, delta_mom=None, delta_yoy=None, sublabel="Margem Bruta: —"),
    "ebitda": KPI("EBITDA", valor=None, delta_mom=None, delta_yoy=None, sublabel="Margem EBITDA: —"),
    "desp_op": KPI("Despesas Operacionais", valor=None, delta_mom=None, delta_yoy=None, sublabel="% da RL: —"),
    "cmv": KPI("CMV", valor=None, delta_mom=None, delta_yoy=None, sublabel="% da RL: —"),
    "resultado": KPI("Resultado", valor=None, delta_mom=None, delta_yoy=None, sublabel="Margem Líquida: —"),
}

# Caso já exista algo calculado no session_state, usa no lugar dos placeholders
kpis_state = st.session_state.get("kpis_financeiro")
if isinstance(kpis_state, dict):
    for key, obj in kpis.items():
        if key in kpis_state:
            # Espera dict com chaves: valor, delta_mom, delta_yoy, sublabel (opcional)
            data = kpis_state[key]
            obj.valor = data.get("valor", obj.valor)
            obj.delta_mom = data.get("delta_mom", obj.delta_mom)
            obj.delta_yoy = data.get("delta_yoy", obj.delta_yoy)
            obj.sublabel = data.get("sublabel", obj.sublabel)

# -------------------------------------------------------------------
# Layout: 2 linhas x 3 colunas (cards)
# -------------------------------------------------------------------
st.header("💹 Núcleo Financeiro")

row1 = st.columns(3)
with row1[0]:
    st.metric(kpis["rl"].label, fmt_val(kpis["rl"].valor), fmt_pct(kpis["rl"].delta_mom))
    st.caption(f"YoY: {fmt_pct(kpis["rl"].delta_yoy)}")

with row1[1]:
    st.metric(kpis["lb"].label, fmt_val(kpis["lb"].valor), fmt_pct(kpis["lb"].delta_mom))
    st.caption((kpis["lb"].sublabel or "").replace("%", "%"))
    st.caption(f"YoY: {fmt_pct(kpis["lb"].delta_yoy)}")

with row1[2]:
    st.metric(kpis["ebitda"].label, fmt_val(kpis["ebitda"].valor), fmt_pct(kpis["ebitda"].delta_mom))
    st.caption((kpis["ebitda"].sublabel or "").replace("%", "%"))
    st.caption(f"YoY: {fmt_pct(kpis["ebitda"].delta_yoy)}")

row2 = st.columns(3)
with row2[0]:
    st.metric(kpis["desp_op"].label, fmt_val(kpis["desp_op"].valor), fmt_pct(kpis["desp_op"].delta_mom))
    st.caption((kpis["desp_op"].sublabel or "").replace("%", "%"))
    st.caption(f"YoY: {fmt_pct(kpis["desp_op"].delta_yoy)}")

with row2[1]:
    st.metric(kpis["cmv"].label, fmt_val(kpis["cmv"].valor), fmt_pct(kpis["cmv"].delta_mom))
    st.caption((kpis["cmv"].sublabel or "").replace("%", "%"))
    st.caption(f"YoY: {fmt_pct(kpis["cmv"].delta_yoy)}")

with row2[2]:
    st.metric(kpis["resultado"].label, fmt_val(kpis["resultado"].valor), fmt_pct(kpis["resultado"].delta_mom))
    st.caption((kpis["resultado"].sublabel or "").replace("%", "%"))
    st.caption(f"YoY: {fmt_pct(kpis["resultado"].delta_yoy)}")

st.divider()

st.info(
    "Estrutura visual pronta. Quando os cálculos estiverem disponíveis, "
    "preencha st.session_state['kpis_financeiro'] com os valores/deltas e os cards serão atualizados."
)
