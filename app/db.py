# app/db.py
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "dre.sqlite"

@st.cache_data(show_spinner=False)
def get_dimensoes():
    """
    Lê do BD as listas de empresas e anos para popular os filtros.
    Retorna (empresas: list[str], anos: list[int]).
    """
    with sqlite3.connect(DB_PATH) as conn:
        df_emp = pd.read_sql("SELECT DISTINCT empresa FROM dre_linhas ORDER BY empresa;", conn)
        df_ano = pd.read_sql("SELECT DISTINCT ano FROM dre_linhas ORDER BY ano;", conn)

    empresas = df_emp["empresa"].astype(str).tolist()
    anos = df_ano["ano"].astype(int).tolist()
    return empresas, anos


@st.cache_data(show_spinner=False)
def get_kpi_base(empresas: list[str], anos: list[int], mes_ini: int, mes_fim: int) -> pd.DataFrame:
    """
    Retorna um DataFrame agregado por (ano, mes_num, descricao).
    - Carrega todos os anos selecionados no filtro, mais (para cada um) o ano
      anterior, para permitir YoY quando só um ano está selecionado.
    - Metadado `anos_sel`: anos efetivamente escolhidos no filtro (o kpi.py soma
      entre eles quando há mais de um).
    """
    if not empresas or not anos:
        return pd.DataFrame(columns=["ano","mes_num","descricao","valor"])  # vazio

    anos_sel = sorted({int(a) for a in anos})
    ref_year = max(anos_sel)
    anos_fetch = sorted({y for y in anos_sel} | {y - 1 for y in anos_sel})

    placeholders_emp = ",".join(["?"] * len(empresas))
    placeholders_ano = ",".join(["?"] * len(anos_fetch))
    params = [*empresas, *anos_fetch, mes_fim]

    sql = f"""
        SELECT ano, mes_num, descricao, SUM(valor) AS valor
        FROM dre_linhas
        WHERE empresa IN ({placeholders_emp})
          AND ano IN ({placeholders_ano})
          AND mes_num BETWEEN 1 AND ?
        GROUP BY ano, mes_num, descricao
        ORDER BY ano, mes_num, descricao;
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(sql, conn, params=params)
    # Normaliza tipos
    if not df.empty:
        df["ano"] = df["ano"].astype(int)
        df["mes_num"] = df["mes_num"].astype(int)
        df["descricao"] = df["descricao"].astype(str).str.upper().str.strip()
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df.attrs["ref_year"] = ref_year
    df.attrs["anos_sel"] = anos_sel
    df.attrs["mes_ini"] = mes_ini
    df.attrs["mes_fim"] = mes_fim
    return df
