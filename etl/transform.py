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


def marcar_estornos_impostos(df: pd.DataFrame, coluna: str = "descricao") -> pd.DataFrame:
    """
    Renomeia a 2ª ocorrência em diante de ICMS, PIS e COFINS, ipi, iss como '... ESTORNO'.
    """
    impostos = {"ICMS", "PIS", "COFINS", "IPI", "ISS"}
    contadores = {}

    def renomear(valor):
        valor = str(valor).strip()
        if valor in impostos:
            contadores[valor] = contadores.get(valor, 0) + 1
            if contadores[valor] > 1:
                return "Estorno de " + valor
        return valor

    df[coluna] = df[coluna].apply(renomear)
    return df
