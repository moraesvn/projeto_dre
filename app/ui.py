# app/ui.py
from dataclasses import dataclass
import streamlit as st

# Meses (número e label curto)
MESES = [
    (1, "Jan"), (2, "Fev"), (3, "Mar"), (4, "Abr"),
    (5, "Mai"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
    (9, "Set"), (10, "Out"), (11, "Nov"), (12, "Dez"),
]

@dataclass
class Filtros:
    empresas: list[str]
    anos: list[int]
    mes_ini: int
    mes_fim: int

def mostrar_filtros(empresas_opts: list[str], anos_opts: list[int]) -> Filtros:
    st.sidebar.header("Filtros")

    # Empresa (multi) – default: todas
    empresas_sel = st.sidebar.multiselect(
        "Empresa",
        options=empresas_opts,
        default=empresas_opts,
    )

    # Ano (multi) – default: ano mais recente
    default_anos = [max(anos_opts)] if anos_opts else []
    anos_sel = st.sidebar.multiselect(
        "Ano",
        options=anos_opts,
        default=default_anos,
    )

    # Mês (intervalo Jan–Dez) com labels legíveis e retorno em números (1..12)
    labels = [lbl for _, lbl in MESES]
    valores = [num for num, _ in MESES]
    lbl_ini, lbl_fim = st.sidebar.select_slider(
        "Mês (intervalo)",
        options=labels,
        value=(labels[0], labels[-1]),
    )
    # mapear label -> número
    label_to_num = dict(zip(labels, valores))
    mes_ini = label_to_num[lbl_ini]
    mes_fim = label_to_num[lbl_fim]

    return Filtros(
        empresas=empresas_sel,
        anos=anos_sel,
        mes_ini=mes_ini,
        mes_fim=mes_fim,
    )
