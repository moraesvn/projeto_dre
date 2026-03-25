import pandas as pd
from dataclasses import dataclass

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
    RB = "RECEITA BRUTA"
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
    RL = "RECEITA LIQUIDA"
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
