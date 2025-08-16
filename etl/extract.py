import pandas as pd
from pathlib import Path

def extract_dre_xlsx(xlsx) -> pd.DataFrame:
    """
    Lê o arquivo DRE em formato XLSX. Aceita caminho como string ou Path.
    """
   
    return pd.read_excel(xlsx, engine="openpyxl")
