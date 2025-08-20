import pandas as pd

def padronizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.normalize('NFKD')        # remove acentos
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.lower()
    )
    return df


def limpar_espacos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa a coluna 'Descrição': remove espaços e prefixos como '(=)', '(-)' etc.
    """
    df["descricao"] = (
        df["descricao"]
        .astype(str)
        .str.strip()
        .str.replace(r"^[\(\)=\-\+]+\s*", "", regex=True)
    )
    return df


def converter_meses_para_float(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte todas as colunas, exceto 'Descrição', para float.
    """
    colunas_meses = df.columns.drop("descricao")
    df[colunas_meses] = df[colunas_meses].apply(pd.to_numeric, errors="coerce")
    return df

def remover_coluna_total(df: pd.DataFrame) -> pd.DataFrame:
    if "total" in df.columns:
        df = df.drop(columns=["total"])
    return df
