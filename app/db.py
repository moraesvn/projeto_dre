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
    Retorna um DataFrame agregado por (ano, mes_num, descricao) para os anos
    de referência (ano mais recente dos filtros) e o anterior, de 1..mes_fim.
    Essa base permite calcular valores do período (mes_ini..mes_fim) e o YTD
    (1..mes_fim), além de YoY.
    """
    if not empresas or not anos:
        return pd.DataFrame(columns=["ano","mes_num","descricao","valor"])  # vazio

    ref_year = max(anos)
    anos_consider = [ref_year, ref_year - 1]

    placeholders_emp = ",".join(["?"] * len(empresas))
    placeholders_ano = ",".join(["?"] * len(anos_consider))
    params = [*empresas, *anos_consider, mes_fim]

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
    # Anexa metadados úteis para o kpi.py
    df.attrs["ref_year"] = ref_year
    df.attrs["mes_ini"] = mes_ini
    df.attrs["mes_fim"] = mes_fim
    return df
