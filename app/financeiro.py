import math
import streamlit as st
import altair as alt
from dataclasses import dataclass
from db import get_kpi_base
from kpi import montar_kpis, serie_desp_op_sobre_receita_bruta_pct, medias_mensais_periodo

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

st.divider()

c1, c2 = st.columns(2)
with c1:
    rb = kpis["receita_bruta"]
    st.metric(rb.label, fmt_val(rb.valor))
    

with c2:
    rl = kpis["receita_liquida"]
    st.metric(rl.label, fmt_val(rl.valor))

st.divider()

st.subheader("% Custo fixo / Faturamento", text_alignment="center")
df_desp_rb = serie_desp_op_sobre_receita_bruta_pct(df_base)
if df_desp_rb.empty or df_desp_rb["pct"].notna().sum() == 0:
    st.caption("Sem pontos válidos para o indicador no intervalo e anos selecionados.")
else:
    df_plot = df_desp_rb.dropna(subset=["pct"]).copy()
    ordem = df_desp_rb["periodo"].tolist()
    pct_max = float(df_plot["pct"].max())
    y_max = max(math.ceil(pct_max), 1)
    if y_max == pct_max:
        y_max += 1
    df_plot["pct_lbl"] = df_plot["pct"].map(lambda v: f"{v:.1f}%")

    enc_x = alt.X("periodo:N", sort=ordem, title="Período")
    enc_y = alt.Y(
        "pct:Q",
        title="% Custo fixo",
        scale=alt.Scale(domain=[0, y_max], nice=False),
        axis=alt.Axis(
            tickMinStep=1,
            labelExpr="datum.value + '%'",
        ),
    )

    base = alt.Chart(df_plot).encode(enc_x, enc_y, tooltip=["periodo", alt.Tooltip("pct:Q", title="%", format=".2f")])
    line = base.mark_line(interpolate="monotone")
    pts = base.mark_point(size=60, filled=True)
    labels = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-8,
        fontSize=11,
        fontWeight=500,
    ).encode(text=alt.Text("pct_lbl:N"))

    chart = (line + pts + labels).properties(height=320).interactive()
    st.altair_chart(chart, use_container_width=True)

medias = medias_mensais_periodo(df_base)
st.subheader("Médias mensais no período", text_alignment="center")
mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.metric(
        "Média % Custo fixo",
        fmt_pct(medias["desp_op"]),
        help="Média dos percentuais mensais (despesa operacional ÷ receita bruta) no período filtrado.",
    )
with mc2:
    st.metric(
        "Receita bruta",
        fmt_val(medias["receita_bruta"]),
        help="Média dos valores mensais de receita bruta no intervalo e anos filtrados.",
    )
with mc3:
    st.metric(
        "Receita líquida",
        fmt_val(medias["receita_liquida"]),
        help="Média dos valores mensais de receita líquida no intervalo e anos filtrados.",
    )

st.divider()

from chat_ui import render_chat
from ai.service import ask_cfo

render_chat("financeiro", filtros, on_ask=ask_cfo)
