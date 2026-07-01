from __future__ import annotations

import math

import streamlit as st


def inject_theme(theme: str) -> None:
    dark = theme == "Dark"
    bg = "#0f172a" if dark else "#ffffff"
    surface = "#111827" if dark else "#f8fafc"
    text = "#e5e7eb" if dark else "#111827"
    border = "#374151" if dark else "#e5e7eb"
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {bg}; color: {text}; }}
        .metric-card {{
            border: 1px solid {border};
            background: {surface};
            border-radius: 8px;
            padding: 14px 16px;
        }}
        .metric-label {{ color: #64748b; font-size: 0.82rem; }}
        .metric-value {{ font-size: 1.35rem; font-weight: 700; color: {text}; }}
        .table-pill {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 999px;
            border: 1px solid {border};
            font-size: 0.72rem;
            margin-right: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str) -> None:
    st.markdown(f"### {title}")


def render_kpi_row(kpis: list[tuple[str, str]]) -> None:
    cols = st.columns(len(kpis))
    for col, (label, value) in zip(cols, kpis):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div>"
                f"<div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )


def format_number(value) -> str:
    if value is None:
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number):
        return "-"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if abs(number) >= 1_000:
        return f"{number / 1_000:.2f}K"
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"
