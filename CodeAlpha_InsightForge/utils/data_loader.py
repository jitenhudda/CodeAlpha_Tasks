from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st


SUPPORTED_SUFFIXES = {".csv", ".parquet", ".xlsx", ".xls", ".json"}


@dataclass
class LoadedTable:
    name: str
    path: str
    category: str
    df: pd.DataFrame
    n_rows: int
    n_cols: int
    size_mb: float
    error: str | None = None


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported file type: {suffix}")


@st.cache_data(show_spinner=False)
def get_loadable_tables(project_root: str) -> list[LoadedTable]:
    root = Path(project_root).expanduser()
    if not root.exists() or not root.is_dir():
        return []

    tables: list[LoadedTable] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        size_mb = round(path.stat().st_size / (1024 * 1024), 2)
        rel_name = str(path.relative_to(root))
        category = path.suffix.lower().lstrip(".").upper()

        try:
            df = _read_table(path)
            tables.append(
                LoadedTable(
                    name=rel_name,
                    path=str(path),
                    category=category,
                    df=df,
                    n_rows=len(df),
                    n_cols=len(df.columns),
                    size_mb=size_mb,
                )
            )
        except Exception as exc:
            tables.append(
                LoadedTable(
                    name=rel_name,
                    path=str(path),
                    category=category,
                    df=pd.DataFrame(),
                    n_rows=0,
                    n_cols=0,
                    size_mb=size_mb,
                    error=str(exc),
                )
            )

    return tables
