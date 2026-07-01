from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Relationship:
    left_table: str
    right_table: str
    key_column: str
    match_ratio: float


def _role_for_table(name: str, df: pd.DataFrame) -> str:
    lower_name = name.lower()
    if any(token in lower_name for token in ["fact", "event", "transaction", "log"]):
        return "Fact / Events"
    if len(df) < 10_000 and any(col.lower().endswith("id") for col in df.columns):
        return "Dimension / Lookup"
    return "Data Table"


def _candidate_keys(df: pd.DataFrame) -> set[str]:
    keys = set()
    for col in df.columns:
        name = col.lower()
        if name == "id" or name.endswith("_id") or name.endswith("id"):
            keys.add(col)
    return keys


def build_relationship_summary(table_map: dict[str, pd.DataFrame]) -> tuple[list[Relationship], dict[str, str]]:
    roles = {name: _role_for_table(name, df) for name, df in table_map.items()}
    relationships: list[Relationship] = []
    names = list(table_map)

    for i, left_name in enumerate(names):
        for right_name in names[i + 1 :]:
            left_df = table_map[left_name]
            right_df = table_map[right_name]
            for col in sorted(_candidate_keys(left_df) & _candidate_keys(right_df)):
                left_values = set(left_df[col].dropna().astype(str).unique())
                right_values = set(right_df[col].dropna().astype(str).unique())
                if not left_values or not right_values:
                    continue
                match_ratio = len(left_values & right_values) / min(len(left_values), len(right_values))
                if match_ratio >= 0.25:
                    relationships.append(
                        Relationship(
                            left_table=left_name,
                            right_table=right_name,
                            key_column=col,
                            match_ratio=round(match_ratio, 3),
                        )
                    )

    return relationships, roles
