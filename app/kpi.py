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

    curr_all = df_base[df_base["ano"] == ref_year]
    prev_all = df_base[df_base["ano"] == ref_year - 1]

    curr_period = curr_all[(curr_all["mes_num"] >= mes_ini) & (curr_all["mes_num"] <= mes_fim)]
    prev_period = prev_all[(prev_all["mes_num"] >= mes_ini) & (prev_all["mes_num"] <= mes_fim)]

    curr_ytd = curr_all[curr_all["mes_num"] <= mes_fim]
    prev_ytd = prev_all[prev_all["mes_num"] <= mes_fim]

    return PeriodFrames(curr_period, prev_period, curr_ytd, prev_ytd, ref_year, mes_ini, mes_fim)


def _sum(df: pd.DataFrame, desc: str) -> float:
    if df.empty:
        return 0.0
    m = df["descricao"] == desc
    return float(df.loc[m, "valor"].sum())


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


def kpi_margem_bruta(frames: PeriodFrames) -> dict:
    RL = "RECEITA LIQUIDA"; LB = "LUCRO BRUTO"
    rl = _sum(frames.curr_period, RL)
    lb = _sum(frames.curr_period, LB)
    mb_pct = (lb / rl * 100) if rl else None

    rl_prev = _sum(frames.prev_period, RL)
    lb_prev = _sum(frames.prev_period, LB)
    mb_prev_pct = (lb_prev / rl_prev * 100) if rl_prev else None

    delta_yoy = (mb_pct - mb_prev_pct) if (mb_pct is not None and mb_prev_pct is not None) else None
    return {"valor": mb_pct, "crescimento_yoy": delta_yoy}


def kpi_margem_operacional(frames: PeriodFrames) -> dict:
    RL = "RECEITA LIQUIDA"; LB = "LUCRO BRUTO"; DESP = "DESPESAS OPERACIONAIS"
    rl = _sum(frames.curr_period, RL)
    op = _sum(frames.curr_period, LB) - _sum(frames.curr_period, DESP)
    op_pct = (op / rl * 100) if rl else None

    rl_prev = _sum(frames.prev_period, RL)
    op_prev = _sum(frames.prev_period, LB) - _sum(frames.prev_period, DESP)
    op_prev_pct = (op_prev / rl_prev * 100) if rl_prev else None

    delta_yoy = (op_pct - op_prev_pct) if (op_pct is not None and op_prev_pct is not None) else None
    return {"valor": op_pct, "crescimento_yoy": delta_yoy}


def kpi_margem_liquida(frames: PeriodFrames) -> dict:
    RL = "RECEITA LIQUIDA"; RES = "RESULTADO LIQUIDO"
    rl = _sum(frames.curr_period, RL)
    res = _sum(frames.curr_period, RES)
    ml_pct = (res / rl * 100) if rl and res != 0 else (0.0 if rl and res == 0 else None)

    rl_prev = _sum(frames.prev_period, RL)
    res_prev = _sum(frames.prev_period, RES)
    ml_prev_pct = (res_prev / rl_prev * 100) if rl_prev and res_prev != 0 else (0.0 if rl_prev and res_prev == 0 else None)

    delta_yoy = (ml_pct - ml_prev_pct) if (ml_pct is not None and ml_prev_pct is not None) else None
    return {"valor": ml_pct, "crescimento_yoy": delta_yoy}


def kpi_ebitda(frames: PeriodFrames) -> dict:
    RL = "RECEITA LIQUIDA"; LB = "LUCRO BRUTO"; DESP = "DESPESAS OPERACIONAIS"
    rl = _sum(frames.curr_period, RL)
    ebitda_val = _sum(frames.curr_period, LB) - _sum(frames.curr_period, DESP)
    margem_pct = (ebitda_val / rl * 100) if rl else None

    ebitda_prev = _sum(frames.prev_period, LB) - _sum(frames.prev_period, DESP)
    crescimento_yoy = None
    if abs(ebitda_prev) > 1e-9:
        crescimento_yoy = (ebitda_val - ebitda_prev) / abs(ebitda_prev) * 100

    return {"valor": ebitda_val, "margem_pct": margem_pct, "crescimento_yoy": crescimento_yoy}


def montar_kpis(df_base: pd.DataFrame) -> dict:
    frames = split_periods(df_base)
    return {
        "receita_liquida": kpi_receita_liquida(frames),
        "margem_bruta_pct": kpi_margem_bruta(frames),
        "margem_operacional_pct": kpi_margem_operacional(frames),
        "margem_liquida_pct": kpi_margem_liquida(frames),
        "ebitda": kpi_ebitda(frames),
    }
