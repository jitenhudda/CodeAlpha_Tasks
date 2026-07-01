from __future__ import annotations

import pandas as pd


def _hashable_value(value):
    if isinstance(value, (dict, list, set, tuple)):
        return str(value)
    return value


def _safe_series(series: pd.Series) -> pd.Series:
    return series.map(_hashable_value)


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def datetime_columns(df: pd.DataFrame) -> list[str]:
    cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        sample = df[col].dropna().head(200)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", utc=False)
        if parsed.notna().mean() >= 0.8:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            cols.append(col)
    return cols


def categorical_columns(df: pd.DataFrame) -> list[str]:
    excluded = set(numeric_columns(df)) | set(datetime_columns(df))
    cols: list[str] = []
    for col in df.columns:
        if col in excluded:
            continue
        values = df[col].dropna().head(100)
        if values.map(lambda value: isinstance(value, (dict, list, set))).any():
            continue
        nunique = _safe_series(df[col]).nunique(dropna=True)
        if nunique <= max(200, int(len(df) * 0.2)):
            cols.append(col)
    return cols


def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Column": df.columns,
            "Dtype": [str(df[col].dtype) for col in df.columns],
            "Non-null": [int(df[col].notna().sum()) for col in df.columns],
            "Unique": [int(_safe_series(df[col]).nunique(dropna=True)) for col in df.columns],
        }
    )


def get_columns_by_semantic(df: pd.DataFrame) -> dict[str, list[str]]:
    lower_cols = {col: col.lower() for col in df.columns}
    return {
        "id": [col for col, name in lower_cols.items() if name == "id" or name.endswith("_id")],
        "date": datetime_columns(df),
        "numeric": numeric_columns(df),
        "categorical": categorical_columns(df),
    }


def duplicate_summary(df: pd.DataFrame) -> dict[str, int]:
    hashable_df = df.apply(_safe_series)
    duplicate_rows = int(hashable_df.duplicated().sum())
    return {
        "total_rows": int(len(df)),
        "duplicate_rows": duplicate_rows,
        "unique_rows": int(len(df) - duplicate_rows),
    }


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    total_rows = max(len(df), 1)
    dup = duplicate_summary(df)["duplicate_rows"]
    rows = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        rows.append(
            {
                "Column": col,
                "Dtype": str(df[col].dtype),
                "Missing": missing,
                "Missing %": round((missing / total_rows) * 100, 2),
                "Unique": int(_safe_series(df[col]).nunique(dropna=True)),
                "Duplicates (rows)": dup,
            }
        )
    return pd.DataFrame(rows)


def top_bottom_analysis(df: pd.DataFrame, category_col: str, metric_col: str, n: int):
    agg = (
        df.groupby(category_col, observed=True)[metric_col]
        .sum()
        .reset_index()
        .sort_values(metric_col, ascending=False)
    )
    return agg.head(n), agg.tail(n).sort_values(metric_col, ascending=True)
