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
