import pandas as pd
from pathlib import Path
from extract import extract_dre_xlsx
from transform import (
    padronizar_nomes_colunas,
    limpar_espacos,
    converter_meses_para_float,
    remover_coluna_total,
    marcar_estornos_impostos
)

MESES_MAP = {
    "jan": 1, "janeiro": 1,
    "fev": 2, "fevereiro": 2,
    "mar": 3, "marco": 3, "março": 3,
    "abr": 4, "abril": 4,
    "mai": 5, "maio": 5,
    "jun": 6, "junho": 6,
    "jul": 7, "julho": 7,
    "ago": 8, "agosto": 8,
    "set": 9, "setembro": 9, "sept": 9,
    "out": 10, "outubro": 10,
    "nov": 11, "novembro": 11,
    "dez": 12, "dezembro": 12,
}


def _normalizar_mes_nome(col: str) -> str:
    return str(col).strip().lower().replace("ç", "c").replace("ã", "a")

def _mes_long(df: pd.DataFrame) -> pd.DataFrame:
    cols_mes = [c for c in df.columns if c not in ["descricao"]]
    df_long = df.melt(id_vars="descricao", value_vars=cols_mes,
                      var_name="mes", value_name="valor")
    df_long["mes"] = df_long["mes"].map(_normalizar_mes_nome)
    df_long["mes_num"] = df_long["mes"].map(MESES_MAP)
    return df_long

def pipeline_dre(xlsx: str | Path, ano: int, empresa: str) -> pd.DataFrame:
    # 1) extract
    df = extract_dre_xlsx(xlsx)

    # 2) padronização de colunas
    df = padronizar_nomes_colunas(df)

    # 3) limpeza de descrição
    df = limpar_espacos(df)

    # 4) remover total
    df = remover_coluna_total(df)

    # 5) tipos (meses → float)
    df = converter_meses_para_float(df)

    #criando estornos de impostos
    df = marcar_estornos_impostos(df)
    
    # 6) reshape para longo
    df = _mes_long(df)

    # 7) metadados
    df["ano"] = int(ano)
    df["empresa"] = str(empresa).upper()

    # 8) validações e ordenação
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["mes_num"])
    df = df.sort_values(["empresa", "ano", "mes_num", "descricao"]).reset_index(drop=True)

    return df[["empresa", "ano", "mes_num", "mes", "descricao", "valor"]]
