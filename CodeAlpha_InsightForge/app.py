"""
app.py
Production-ready, auto-discovering analytics dashboard.

Run with:
    python -m streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from utils.data_loader import get_loadable_tables, LoadedTable
from utils.relationships import build_relationship_summary
from utils.analysis import (
    profile_dataframe,
    get_columns_by_semantic,
    data_quality_report,
    duplicate_summary,
    numeric_columns,
    categorical_columns,
    datetime_columns,
    top_bottom_analysis,
)
from utils import charts
from utils.ui import inject_theme, section_header, render_kpi_row, format_number

# --------------------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="InsightForge",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAX_ROWS_FOR_HEAVY_VIZ = 500_000  # safety cap for scatter/correlation on huge tables


# --------------------------------------------------------------------------------------
# Sidebar: project path, theme, table selection
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    default_root = os.getcwd()
    project_root = st.text_input("Project folder path", value=default_root, help="Folder to scan recursively for data files.")

    theme = st.radio("Appearance", ["Light", "Dark"], horizontal=True, index=0)
    inject_theme(theme)

    rescan = st.button("🔄 Rescan folder", use_container_width=True)
    if rescan:
        st.cache_data.clear()

    st.markdown("---")

st.markdown(
    """
    <h1 style='margin-bottom:0;'>🚀 InsightForge</h1>
    <p style='color:#888;margin-top:4px;font-size:18px;'>
        Production-Inspired Developer Analytics & Data Visualization Platform
    </p>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------------------
# Discover & load data
# --------------------------------------------------------------------------------------
with st.spinner("Scanning project folder and loading datasets..."):
    tables: list[LoadedTable] = get_loadable_tables(project_root)

if not tables:
    st.warning(
        "No supported data files (.csv, .parquet, .xlsx, .xls, .json) were found in the given path, "
        "or the path does not exist. Update the **Project folder path** in the sidebar."
    )
    st.stop()

valid_tables = [t for t in tables if t.error is None and not t.df.empty]
failed_tables = [t for t in tables if t.error is not None]

if not valid_tables:
    st.error("Files were found, but none could be loaded successfully. See details below.")
    for t in failed_tables:
        st.write(f"❌ `{t.path}` — {t.error}")
    st.stop()

table_map = {t.name: t.df for t in valid_tables}
meta_map = {t.name: t for t in valid_tables}

# --------------------------------------------------------------------------------------
# Sidebar: dataset picker + file inventory
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"**{len(valid_tables)} dataset(s) loaded** "
                f"({len(failed_tables)} skipped)")

    table_names = sorted(table_map.keys())
    selected_table_name = st.selectbox("Active dataset", table_names, index=0)

    with st.expander("📁 File inventory", expanded=False):
        for t in valid_tables:
            st.markdown(
                f"<span class='table-pill'>{t.category}</span> **{t.name}** "
                f"— {t.n_rows:,} rows × {t.n_cols} cols ({t.size_mb} MB)",
                unsafe_allow_html=True,
            )
        if failed_tables:
            st.markdown("**Skipped / failed:**")
            for t in failed_tables:
                st.caption(f"⚠️ {t.name}: {t.error}")

df_active = table_map[selected_table_name].copy()
active_meta = meta_map[selected_table_name]

# --------------------------------------------------------------------------------------
# Relationship detection (across ALL tables, computed once)
# --------------------------------------------------------------------------------------
relationships, roles = build_relationship_summary(table_map)

# --------------------------------------------------------------------------------------
# Sidebar filters (built dynamically from active dataset)
# --------------------------------------------------------------------------------------
profiles = profile_dataframe(df_active)
cat_cols = categorical_columns(df_active)
num_cols = numeric_columns(df_active)
date_cols = datetime_columns(df_active)

with st.sidebar:
    st.markdown("---")
    st.markdown("## 🔎 Filters")
    st.caption(f"Filtering: **{selected_table_name}**")

    filtered_df = df_active

    # Date range filter
    if date_cols:
        date_col = st.selectbox("Date column", date_cols, index=0, key="date_filter_col")
        valid_dates = filtered_df[date_col].dropna()
        if not valid_dates.empty:
            min_d, max_d = valid_dates.min(), valid_dates.max()
            date_range = st.date_input("Date range", value=(min_d.date(), max_d.date()))
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start, end = date_range
                mask = (filtered_df[date_col] >= pd.Timestamp(start)) & (filtered_df[date_col] <= pd.Timestamp(end) + pd.Timedelta(days=1))
                filtered_df = filtered_df[mask]

    # Categorical filters (limit to first 5 to keep sidebar usable)
    for c in cat_cols[:5]:
        options = sorted(filtered_df[c].dropna().astype(str).unique().tolist())
        if 1 < len(options) <= 200:
            selected_vals = st.multiselect(f"{c}", options, default=[])
            if selected_vals:
                filtered_df = filtered_df[filtered_df[c].astype(str).isin(selected_vals)]

    # Numeric range filter (first 2 numeric columns)
    for c in num_cols[:2]:
        series = filtered_df[c].dropna()
        if series.empty:
            continue
        lo, hi = float(series.min()), float(series.max())
        if lo < hi:
            sel_lo, sel_hi = st.slider(f"{c} range", lo, hi, (lo, hi))
            filtered_df = filtered_df[(filtered_df[c] >= sel_lo) & (filtered_df[c] <= sel_hi)]

    st.markdown("---")
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_table_name}_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )

is_sampled = False
viz_df = filtered_df
if len(viz_df) > MAX_ROWS_FOR_HEAVY_VIZ:
    viz_df = viz_df.sample(MAX_ROWS_FOR_HEAVY_VIZ, random_state=42)
    is_sampled = True

# --------------------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------------------
tab_overview, tab_trends, tab_breakdown, tab_corr, tab_topbottom, tab_quality, tab_explorer, tab_relations = st.tabs(
    ["🏠 Overview", "📈 Trends", "📊 Breakdown", "🧮 Correlation", "🏆 Top / Bottom",
     "🧹 Data Quality", "🔍 Table Explorer", "🔗 Relationships"]
)

# ---------------- OVERVIEW ----------------
with tab_overview:
    if is_sampled:
        st.info(f"Visuals use a {MAX_ROWS_FOR_HEAVY_VIZ:,}-row sample for performance ({len(filtered_df):,} rows match filters).")

    section_header("Key Metrics")
    kpis = [
        ("Total Rows", format_number(len(filtered_df))),
        ("Total Columns", str(df_active.shape[1])),
    ]
    if num_cols:
        primary_num = num_cols[0]
        kpis.append((f"Σ {primary_num}", format_number(filtered_df[primary_num].sum())))
        kpis.append((f"Avg {primary_num}", format_number(filtered_df[primary_num].mean())))
    if cat_cols:
        kpis.append((f"Unique {cat_cols[0]}", format_number(filtered_df[cat_cols[0]].nunique())))
    render_kpi_row(kpis[:5])

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        section_header("Distribution Overview")
        if num_cols:
            metric_col = st.selectbox("Numeric column", num_cols, key="ov_hist")
            fig = charts.histogram(viz_df, metric_col, theme, title=f"Distribution of {metric_col}")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_overview_hist")
        else:
            st.caption("No numeric columns available.")

    with col2:
        section_header("Category Composition")
        if cat_cols:
            cat_col = st.selectbox("Category column", cat_cols, key="ov_pie")
            counts = viz_df[cat_col].value_counts().reset_index()
            counts.columns = [cat_col, "count"]
            fig = charts.pie_chart(counts.head(12), cat_col, "count", theme, title=f"{cat_col} share")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_overview_pie")
        else:
            st.caption("No categorical columns available.")

# ---------------- TRENDS ----------------
with tab_trends:
    section_header("Time-Series Trends")
    if date_cols:
        dcol = st.selectbox("Date column", date_cols, key="trend_date")
        ycol_options = num_cols if num_cols else None
        if ycol_options:
            ycol = st.selectbox("Metric", ycol_options, key="trend_metric")
            group_options = ["(none)"] + cat_cols
            gcol = st.selectbox("Group by (optional)", group_options, key="trend_group")
            gcol = None if gcol == "(none)" else gcol

            granularity = st.radio("Granularity", ["Day", "Week", "Month"], horizontal=True, index=2)
            freq_map = {"Day": "D", "Week": "W", "Month": "M"}

            tmp = viz_df[[dcol, ycol] + ([gcol] if gcol else [])].dropna(subset=[dcol])
            if not tmp.empty:
                tmp["_period"] = pd.to_datetime(tmp[dcol]).dt.to_period(freq_map[granularity]).dt.to_timestamp()
                if gcol:
                    agg = tmp.groupby(["_period", gcol], observed=True)[ycol].sum().reset_index()
                    fig = charts.line_chart(agg, "_period", ycol, theme, color=gcol, title=f"{ycol} over time by {gcol}")
                else:
                    agg = tmp.groupby("_period")[ycol].sum().reset_index()
                    fig = charts.line_chart(agg, "_period", ycol, theme, title=f"{ycol} over time")
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key="chart_trend_line")
                else:
                    st.caption("Not enough data to plot a trend.")
            else:
                st.caption("No data available for the selected date column.")
        else:
            st.caption("No numeric metric columns available to trend.")
    else:
        st.info("No datetime columns detected in this dataset. Trends require a date/time column.")

# ---------------- BREAKDOWN ----------------
with tab_breakdown:
    section_header("Bar & Pie Breakdown")
    c1, c2 = st.columns(2)

    with c1:
        if cat_cols and num_cols:
            bcat = st.selectbox("Category", cat_cols, key="bd_cat")
            bnum = st.selectbox("Metric", num_cols, key="bd_num")
            agg = viz_df.groupby(bcat, observed=True)[bnum].sum().reset_index().sort_values(bnum, ascending=False).head(20)
            fig = charts.bar_chart(agg, bcat, bnum, theme, title=f"{bnum} by {bcat}")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_breakdown_bar")
        else:
            st.caption("Need at least one categorical and one numeric column.")

    with c2:
        if num_cols:
            hcol = st.selectbox("Histogram column", num_cols, key="bd_hist")
            bins = st.slider("Bins", 10, 100, 40, key="bd_bins")
            fig = charts.histogram(viz_df, hcol, theme, nbins=bins, title=f"Distribution of {hcol}")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_breakdown_hist")

    section_header("Heatmap (Category × Time)")
    if date_cols and cat_cols and num_cols:
        hcat = st.selectbox("Category", cat_cols, key="hm_cat")
        hnum = st.selectbox("Metric", num_cols, key="hm_num")
        hdate = st.selectbox("Date", date_cols, key="hm_date")
        fig = charts.time_pivot_heatmap(viz_df, hdate, hcat, hnum, theme, title=f"{hnum} heatmap")
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="chart_breakdown_heatmap")
        else:
            st.caption("Not enough data to render heatmap.")
    else:
        st.caption("Heatmap requires date, categorical, and numeric columns.")

    section_header("Box Plot (Outlier View)")
    if num_cols:
        box_num = st.selectbox("Numeric column", num_cols, key="box_num")
        box_group = st.selectbox("Group by (optional)", ["(none)"] + cat_cols, key="box_group")
        box_group = None if box_group == "(none)" else box_group
        fig = charts.box_plot(viz_df, box_num, theme, group=box_group, title=f"Box plot of {box_num}")
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="chart_breakdown_box")

# ---------------- CORRELATION ----------------
with tab_corr:
    section_header("Correlation Matrix")
    if len(num_cols) >= 2:
        corr = charts.correlation_matrix(viz_df, num_cols)
        fig = charts.heatmap(corr, theme, title="Correlation between numeric columns")
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="chart_corr_matrix")

        section_header("Scatter Matrix")
        chosen = st.multiselect("Columns to compare (max 5)", num_cols, default=num_cols[:min(4, len(num_cols))])
        if 2 <= len(chosen) <= 5:
            color_opt = st.selectbox("Color by (optional)", ["(none)"] + cat_cols, key="scatter_color")
            color_opt = None if color_opt == "(none)" else color_opt
            fig2 = charts.scatter_matrix(viz_df, chosen, theme, color=color_opt)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, key="chart_corr_scatter")
        else:
            st.caption("Select 2 to 5 numeric columns.")
    else:
        st.info("Correlation analysis requires at least 2 numeric columns.")

# ---------------- TOP / BOTTOM ----------------
with tab_topbottom:
    section_header("Top / Bottom N Analysis")
    if cat_cols and num_cols:
        tb_cat = st.selectbox("Group by", cat_cols, key="tb_cat")
        tb_num = st.selectbox("Metric", num_cols, key="tb_num")
        n = st.slider("N", 5, 25, 10, key="tb_n")
        top, bottom = top_bottom_analysis(viz_df, tb_cat, tb_num, n)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Top {n} by {tb_num}**")
            fig = charts.bar_chart(top, tb_cat, tb_num, theme, orientation="h", title=f"Top {n}")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_topbottom_top")
        with c2:
            st.markdown(f"**Bottom {n} by {tb_num}**")
            fig = charts.bar_chart(bottom, tb_cat, tb_num, theme, orientation="h", title=f"Bottom {n}")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="chart_topbottom_bottom")
    else:
        st.info("Top/Bottom analysis requires a categorical and a numeric column.")

# ---------------- DATA QUALITY ----------------
with tab_quality:
    section_header("Data Quality Report")

    dup = duplicate_summary(df_active)
    render_kpi_row([
        ("Total Rows", format_number(dup["total_rows"])),
        ("Duplicate Rows", format_number(dup["duplicate_rows"])),
        ("Unique Rows", format_number(dup["unique_rows"])),
        ("Columns", str(df_active.shape[1])),
        ("Missing Cells", format_number(int(df_active.isna().sum().sum()))),
    ])

    st.markdown("")
    quality_df = data_quality_report(df_active)
    quality_df = quality_df.drop(columns=["Duplicates (rows)"])
    st.dataframe(quality_df, use_container_width=True, height=380)

    if quality_df["Missing %"].sum() > 0:
        fig = charts.bar_chart(
            quality_df[quality_df["Missing %"] > 0].sort_values("Missing %", ascending=False),
            "Column", "Missing %", theme, title="Missing % by column"
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="chart_quality_missing")
    else:
        st.success("No missing values detected in this dataset.")

# ---------------- TABLE EXPLORER ----------------
with tab_explorer:
    section_header(f"Table Explorer — {selected_table_name}")
    st.caption(f"Source file: `{active_meta.path}`")

    search = st.text_input("🔎 Search across all columns", "")
    explore_df = filtered_df
    if search:
        try:
            mask = explore_df.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False)).any(axis=1)
            explore_df = explore_df[mask]
        except Exception:
            pass

    page_size = st.slider("Rows per page", 10, 500, 50)
    total_rows = len(explore_df)
    max_page = max((total_rows - 1) // page_size, 0)
    page = st.number_input("Page", min_value=0, max_value=max_page, value=0, step=1)
    start, end = page * page_size, page * page_size + page_size

    st.dataframe(explore_df.iloc[start:end], use_container_width=True, height=500)
    st.caption(f"Showing rows {start+1:,}–{min(end, total_rows):,} of {total_rows:,}")

    st.download_button(
        "⬇️ Download current view (CSV)",
        data=explore_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_table_name}_explorer_view.csv",
        mime="text/csv",
    )

# ---------------- RELATIONSHIPS ----------------
with tab_relations:
    section_header("Detected Table Roles")
    role_df = pd.DataFrame([{"Table": k, "Role": v, "Rows": meta_map[k].n_rows, "Columns": meta_map[k].n_cols}
                             for k, v in roles.items() if k in meta_map])
    st.dataframe(role_df.sort_values("Role"), use_container_width=True, height=260)

    section_header("Detected Relationships (Key Column Overlap)")
    if relationships:
        rel_df = pd.DataFrame([{
            "Table A": r.left_table,
            "Table B": r.right_table,
            "Shared Key": r.key_column,
            "Match Ratio": r.match_ratio,
        } for r in relationships])
        st.dataframe(rel_df, use_container_width=True, height=400)
    else:
        st.info("No strong key-column relationships were detected between the loaded tables.")

st.markdown("---")
st.caption("Auto-generated analytics dashboard · Built with Streamlit & Plotly")
