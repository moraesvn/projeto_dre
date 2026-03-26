import pandas as pd
from dataclasses import dataclass

RB = "RECEITA BRUTA"
RL = "RECEITA LIQUIDA"
DESP_OP = "DESPESAS OPERACIONAIS"
_MESES_ABREV = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

@dataclass
class PeriodFrames:
    curr_period: pd.DataFrame  # mes_ini..mes_fim do ano ref
    prev_period: pd.DataFrame  # mes_ini..mes_fim do ano ref-1
    curr_ytd: pd.DataFrame     # 1..mes_fim do ano ref
    prev_ytd: pd.DataFrame     # 1..mes_fim do ano ref-1
    ref_year: int
    mes_ini: int
    mes_fim: int


def split_periods(df_base: pd.DataFrame) -> PeriodFrames:
    ref_year = int(df_base.attrs.get("ref_year"))
    mes_ini = int(df_base.attrs.get("mes_ini"))
    mes_fim = int(df_base.attrs.get("mes_fim"))
    anos_sel = df_base.attrs.get("anos_sel")
    if anos_sel is None:
        anos_sel = [ref_year]
    else:
        anos_sel = sorted({int(x) for x in anos_sel})

    if len(anos_sel) == 1:
        y = anos_sel[0]
        curr_all = df_base[df_base["ano"] == y]
        prev_all = df_base[df_base["ano"] == y - 1]
        curr_period = curr_all[(curr_all["mes_num"] >= mes_ini) & (curr_all["mes_num"] <= mes_fim)]
        prev_period = prev_all[(prev_all["mes_num"] >= mes_ini) & (prev_all["mes_num"] <= mes_fim)]
        curr_ytd = curr_all[curr_all["mes_num"] <= mes_fim]
        prev_ytd = prev_all[prev_all["mes_num"] <= mes_fim]
    else:
        sel = df_base["ano"].isin(anos_sel)
        curr_all = df_base[sel]
        curr_period = curr_all[(curr_all["mes_num"] >= mes_ini) & (curr_all["mes_num"] <= mes_fim)]
        curr_ytd = curr_all[curr_all["mes_num"] <= mes_fim]
        prev_period = df_base.iloc[0:0].copy()
        prev_ytd = df_base.iloc[0:0].copy()

    return PeriodFrames(curr_period, prev_period, curr_ytd, prev_ytd, ref_year, mes_ini, mes_fim)


def _sum(df: pd.DataFrame, desc: str) -> float:
    if df.empty:
        return 0.0
    m = df["descricao"] == desc
    return float(df.loc[m, "valor"].sum())


def kpi_receita_bruta(frames: PeriodFrames) -> dict:
    valor_periodo = _sum(frames.curr_period, RB)
    valor_ytd = _sum(frames.curr_ytd, RB)
    valor_periodo_prev = _sum(frames.prev_period, RB)

    crescimento_yoy = None
    if valor_periodo_prev and abs(valor_periodo_prev) > 1e-9:
        crescimento_yoy = (valor_periodo - valor_periodo_prev) / abs(valor_periodo_prev) * 100

    return {
        "valor": valor_periodo,
        "ytd": valor_ytd,
        "crescimento_yoy": crescimento_yoy,
    }


def kpi_receita_liquida(frames: PeriodFrames) -> dict:
    valor_periodo = _sum(frames.curr_period, RL)
    valor_ytd = _sum(frames.curr_ytd, RL)
    valor_periodo_prev = _sum(frames.prev_period, RL)

    crescimento_yoy = None
    if valor_periodo_prev and abs(valor_periodo_prev) > 1e-9:
        crescimento_yoy = (valor_periodo - valor_periodo_prev) / abs(valor_periodo_prev) * 100

    return {
        "valor": valor_periodo,
        "ytd": valor_ytd,
        "crescimento_yoy": crescimento_yoy,
    }


def montar_kpis(df_base: pd.DataFrame) -> dict:
    frames = split_periods(df_base)
    return {
        "receita_bruta": kpi_receita_bruta(frames),
        "receita_liquida": kpi_receita_liquida(frames),
    }


def serie_desp_op_sobre_receita_bruta_pct(df_base: pd.DataFrame) -> pd.DataFrame:
    """
    Uma linha por (ano, mês) nos anos do filtro e entre mes_ini..mes_fim.
    % = despesa operacional / receita bruta * 100.
    Colunas: ano, mes_num, periodo (rótulo eixo X), pct.
    """
    cols = ["ano", "mes_num", "periodo", "pct"]
    if df_base.empty:
        return pd.DataFrame(columns=cols)
    mes_ini = int(df_base.attrs.get("mes_ini", 1))
    mes_fim = int(df_base.attrs.get("mes_fim", 12))
    anos_sel = df_base.attrs.get("anos_sel")
    if anos_sel is None:
        anos_sel = [int(df_base.attrs.get("ref_year"))]
    else:
        anos_sel = sorted({int(x) for x in anos_sel})
    d = df_base[
        df_base["ano"].isin(anos_sel)
        & df_base["descricao"].isin([RB, DESP_OP])
        & (df_base["mes_num"] >= mes_ini)
        & (df_base["mes_num"] <= mes_fim)
    ]
    if d.empty:
        return pd.DataFrame(columns=cols)
    wide = (
        d.pivot_table(index=["ano", "mes_num"], columns="descricao", values="valor", aggfunc="sum")
        .reset_index()
    )
    for col in (RB, DESP_OP):
        if col not in wide.columns:
            wide[col] = 0.0
    rb = wide[RB].astype(float)
    desp = wide[DESP_OP].astype(float)
    ok = rb.abs() > 1e-9
    pct = pd.Series(float("nan"), index=wide.index, dtype=float)
    pct.loc[ok] = (desp[ok] / rb[ok]) * 100.0
    wide["pct"] = pct
    wide["periodo"] = [
        f"{_MESES_ABREV[int(m)]}/{int(a)}" for a, m in zip(wide["ano"], wide["mes_num"])
    ]
    out = wide.sort_values(["ano", "mes_num"])[cols].reset_index(drop=True)
    return out


def medias_mensais_periodo(df_base: pd.DataFrame) -> dict[str, float | None]:
    """
    - desp_op: média dos percentuais mensais (despesa operacional / receita bruta × 100).
    - receita_bruta / receita_liquida: média dos valores mensais em R$.
    """
    empty = {"desp_op": None, "receita_bruta": None, "receita_liquida": None}
    if df_base.empty:
        return empty
    mes_ini = int(df_base.attrs.get("mes_ini", 1))
    mes_fim = int(df_base.attrs.get("mes_fim", 12))
    anos_sel = df_base.attrs.get("anos_sel")
    if anos_sel is None:
        anos_sel = [int(df_base.attrs.get("ref_year"))]
    else:
        anos_sel = sorted({int(x) for x in anos_sel})
    d = df_base[
        df_base["ano"].isin(anos_sel)
        & df_base["descricao"].isin([DESP_OP, RB, RL])
        & (df_base["mes_num"] >= mes_ini)
        & (df_base["mes_num"] <= mes_fim)
    ]
    if d.empty:
        return empty
    out: dict[str, float | None] = {**empty}

    serie_pct = serie_desp_op_sobre_receita_bruta_pct(df_base)
    pcts = serie_pct["pct"].dropna()
    out["desp_op"] = float(pcts.mean()) if not pcts.empty else None

    for desc, key in [
        (RB, "receita_bruta"),
        (RL, "receita_liquida"),
    ]:
        vals = pd.to_numeric(d.loc[d["descricao"] == desc, "valor"], errors="coerce").dropna()
        out[key] = float(vals.mean()) if not vals.empty else None
    return out
