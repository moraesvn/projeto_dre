"""Integração do ETL `etl/` com o app Streamlit (importação de DRE via upload)."""
from __future__ import annotations

import io
import sys
from pathlib import Path
import pandas as pd

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent
_ETL_DIR = _PROJECT_ROOT / "etl"

# Coloca a pasta `etl/` no path para `load`, `pipeline`, `extract`, `transform` importarem entre si.
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from load import substituir_dre_periodo  # noqa: E402
from pipeline import pipeline_dre  # noqa: E402


def preparar_dados_upload(
    file_bytes: bytes,
    ano: int,
    empresa: str,
) -> tuple[bool, str, pd.DataFrame | None]:
    """
    Executa o pipeline sobre o XLSX em memória.
    Retorna (sucesso, mensagem de erro ou vazia, DataFrame ou None).
    """
    try:
        buf = io.BytesIO(file_bytes)
        df = pipeline_dre(buf, ano, empresa)
        return True, "", df
    except Exception as e:  # noqa: BLE001
        return False, str(e), None


def executar_importacao(df: pd.DataFrame, ano: int, empresa: str) -> tuple[bool, str]:
    """Substitui o período (empresa, ano) no SQLite pelo DataFrame já processado."""
    try:
        removidas, inseridas = substituir_dre_periodo(df, ano, empresa)
        return (
            True,
            f"Importação concluída. Linhas antigas removidas: {removidas}. Linhas inseridas: {inseridas}.",
        )
    except Exception as e:  # noqa: BLE001
        return False, str(e)
