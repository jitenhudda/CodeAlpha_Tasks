"""
Supply Chain BI Dashboard
=========================
Professional Streamlit analytics dashboard for DataCo Smart Supply Chain.

Prerequisites
-------------
    pip install streamlit plotly pandas pyarrow

Usage
-----
    1. Run ALL notebook cells (Sections 1–13) to build the processed DataFrame.
    2. Run Section 14 to export  dashboard_data.csv  into this folder.
    3. Then in a terminal:
           streamlit run app.py
    4. Dashboard opens at  http://localhost:8501
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  ── must be first Streamlit call
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Supply Chain Performance Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Supply Chain Performance Intelligence · DataCo Smart Supply Chain"
    },
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLES  — Power-BI-inspired look
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>

/* Hide Streamlit Header */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Hide Deploy button */
[data-testid="stToolbar"] {
    display: none !important;
}

/* Hide Main Menu */
#MainMenu {
    visibility: hidden;
}

/* Hide Footer */
footer {
    visibility: hidden;
}

/* Remove top spacing */
.block-container {
    padding-top: 0rem !important;
}


/* ── Background ─────────────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #ECF0F8 !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0D2550 0%, #1A5276 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E4ECF7 !important; }
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.13) !important;
    border-color: rgba(255,255,255,0.28) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #fff !important; }
[data-testid="stSidebar"] [role="radiogroup"] div {
    background: transparent !important;
}

/* ── Content padding ─────────────────────────────────────────────────────── */
.block-container { padding-top: 0.9rem; padding-bottom: 2rem; max-width: 100%; }

/* ── KPI card ────────────────────────────────────────────────────────────── */
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 18px 20px 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-top: 4px solid;
    height: 100%;
    box-sizing: border-box;
}
.kpi-label {
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .9px;
    color: #6B80A8;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 29px;
    font-weight: 800;
    color: #0D2550;
    line-height: 1.05;
    margin-bottom: 5px;
}
.kpi-sub {
    font-size: 11.5px;
    color: #8EA3C8;
    min-height: 16px;
}

/* ── White card wrapper ───────────────────────────────────────────────────── */
.card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 4px;
}

/* ── Section panel headings ──────────────────────────────────────────────── */
.panel-title {
    font-size: 12.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .7px;
    color: #0D2550;
    margin: 0 0 10px;
    padding-bottom: 8px;
    border-bottom: 2px solid #E2E9F6;
}

/* ── Summary key-value rows ──────────────────────────────────────────────── */
.kv-row {
    display: flex;
    flex-direction: column;
    margin: 7px 0;
    font-size: 12.5px;
    line-height: 1.45;
}
.kv-row strong { color: #0D2550; font-size: 11px; font-weight: 700;
                  text-transform: uppercase; letter-spacing: .4px; }
.kv-row span   { color: #2C3E5A; }

/* ── Insight chip ────────────────────────────────────────────────────────── */
.insight-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin: 7px 0;
    padding: 9px 12px;
    border-radius: 8px;
    background: #F3F7FE;
}
.insight-icon { font-size: 17px; flex-shrink: 0; line-height: 1.5; }
.insight-text { font-size: 12.5px; color: #2C3E5A; line-height: 1.5; margin: 0; }

/* ── Recommendation bullet ───────────────────────────────────────────────── */
.rec-row {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin: 6px 0;
    padding: 8px 12px;
    border-radius: 8px;
    border-left: 3px solid #1A73E8;
    background: #F5F9FF;
}
.rec-text { font-size: 12.5px; color: #2C3E5A; line-height: 1.5; margin: 0; }

/* ── Dividers & spacing ──────────────────────────────────────────────────── */
.spacer { height: 14px; }
.section-hr { border: none; border-top: 1px solid #D8E2F4; margin: 14px 0 10px; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.dash-footer {
    text-align: center;
    font-size: 11px;
    color: #9AABCA;
    padding: 14px 0 4px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE & CHART DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "navy":   "#0D2550",
    "blue":   "#1A73E8",
    "teal":   "#00A8A0",
    "orange": "#E07B18",
    "green":  "#1C8F4A",
    "red":    "#C0392B",
    "muted":  "#8B9DC3",
    "grid":   "#E8EDF8",
    "white":  "#FFFFFF",
}

_CHART_FONT  = dict(family="Segoe UI, Arial, sans-serif", size=12, color=C["navy"])
_PLOTLY_BASE = dict(
    paper_bgcolor=C["white"],
    plot_bgcolor=C["white"],
    font=_CHART_FONT,
    margin=dict(l=10, r=18, t=50, b=12),
    hoverlabel=dict(bgcolor=C["navy"], font_color="#FFFFFF", font_size=12),
)

_DATE_COL  = "order date (DateOrders)"
_DATA_FILE = "dashboard_data.csv"
_MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (cached)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading supply chain data …")
def load_data() -> pd.DataFrame:
    p = pathlib.Path(_DATA_FILE)
    if not p.exists():
        st.error(
            f"❌  '{_DATA_FILE}' not found.  "
            "Please run the Jupyter notebook Section 14 first "
            "to export the processed DataFrame."
        )
        st.stop()

    df = pd.read_csv(p, low_memory=False)

    # Parse date column
    if _DATE_COL in df.columns:
        df[_DATE_COL] = pd.to_datetime(df[_DATE_COL], errors="coerce")

    # Coerce numeric columns
    for col in ("Sales", "Order Profit Per Order"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Order Year" in df.columns:
        df["Order Year"] = pd.to_numeric(df["Order Year"], errors="coerce").astype("Int64")

    # Validate required columns
    _required = {"Market", "Order Year", "Category Name",
                 "Sales", "Order Profit Per Order", _DATE_COL}
    missing = _required - set(df.columns)
    if missing:
        st.error(f"❌  Missing columns in dashboard_data.csv: {sorted(missing)}")
        st.stop()

    return df


df_full = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS & METRIC SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🚚 Supply Chain")
    st.markdown("#### Performance Intelligence")
    st.markdown("---")
    st.markdown("### 🔍 Filters")

    all_markets = sorted(df_full["Market"].dropna().astype(str).unique().tolist())
    all_years   = sorted(df_full["Order Year"].dropna().unique().tolist(), reverse=True)
    all_years_s = [str(int(y)) for y in all_years]

    sel_markets = st.multiselect(
        "Market", all_markets, default=all_markets,
        help="Select one or more markets (default: all)",
    )
    sel_years_s = st.multiselect(
        "Year", all_years_s, default=all_years_s,
        help="Select one or more years (default: all)",
    )

    st.markdown("---")
    st.markdown("### 📊 Primary Metric")

    _METRIC_MAP: dict[str, str] = {
        "💰  Total Sales ($)":    "Sales",
        "📈  Total Profit ($)":   "Order Profit Per Order",
        "📦  Order Count":        "__count__",
    }
    sel_metric_lbl = st.radio(
        "", list(_METRIC_MAP.keys()), label_visibility="collapsed"
    )
    sel_metric_col = _METRIC_MAP[sel_metric_lbl]
    sel_metric_name = sel_metric_lbl.replace("💰  ","").replace("📈  ","").replace("📦  ","")

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:#A0B8D8;'>"
        f"📂 {len(df_full):,} total orders<br>"
        f"🗓 {int(df_full['Order Year'].min())}–{int(df_full['Order Year'].max())}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# FILTER DATA
# ══════════════════════════════════════════════════════════════════════════════
sel_years_int = [int(y) for y in sel_years_s] if sel_years_s else []
sel_markets_f = sel_markets if sel_markets else all_markets

dff = df_full[
    df_full["Market"].astype(str).isin(sel_markets_f) &
    df_full["Order Year"].isin(sel_years_int)
].copy()

if dff.empty:
    st.warning("⚠️  No data matches the selected filters. Adjust the sidebar controls.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER BAR
# ══════════════════════════════════════════════════════════════════════════════
mkt_tag = (", ".join(sel_markets) if len(sel_markets) <= 3
           else f"{len(sel_markets)} of {len(all_markets)} Markets")
yr_tag  = (", ".join(sel_years_s) if len(sel_years_s) <= 4
           else f"{min(sel_years_s)}–{max(sel_years_s)}")

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0D2550 0%, #1A73E8 100%);
    padding: 17px 28px;
    border-radius: 14px;
    margin-bottom: 16px;">
  <span style="font-size:23px;font-weight:800;color:#FFFFFF;letter-spacing:-.2px;">
    🚚 Supply Chain Performance Intelligence
  </span><br>
  <span style="font-size:12px;color:rgba(255,255,255,.72);">
    DataCo Smart Supply Chain &nbsp;·&nbsp; {mkt_tag} &nbsp;·&nbsp; {yr_tag}
    &nbsp;·&nbsp; Metric: {sel_metric_name}
  </span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI COMPUTATIONS
# ══════════════════════════════════════════════════════════════════════════════
total_sales    = dff["Sales"].sum()
total_profit   = dff["Order Profit Per Order"].sum()
total_orders   = len(dff)
avg_profit     = dff["Order Profit Per Order"].mean()
overall_avg_p  = df_full["Order Profit Per Order"].mean()
delta_profit   = avg_profit - overall_avg_p
profit_margin  = (total_profit / total_sales * 100) if total_sales != 0 else 0.0
avg_order_val  = (total_sales / total_orders) if total_orders else 0.0

delta_sign  = "▲" if delta_profit >= 0 else "▼"
delta_color = C["green"] if delta_profit >= 0 else C["red"]


# ── KPI card helper ───────────────────────────────────────────────────────────
def kpi_html(label: str, value: str, sub: str, accent: str, icon: str) -> str:
    return f"""
<div class="kpi-card" style="border-top-color:{accent};">
  <div class="kpi-label">{icon}&nbsp; {label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-sub">{sub}</div>
</div>"""


k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(kpi_html(
        "Total Sales", f"${total_sales/1e6:.2f}M",
        f"{total_orders:,} orders · Avg ${avg_order_val:,.0f}/order",
        C["blue"], "💰",
    ), unsafe_allow_html=True)

with k2:
    st.markdown(kpi_html(
        "Total Profit", f"${total_profit/1e6:.2f}M",
        f"Net margin: {profit_margin:.1f}%",
        C["teal"], "📈",
    ), unsafe_allow_html=True)

with k3:
    yr_min = int(dff["Order Year"].min())
    yr_max = int(dff["Order Year"].max())
    st.markdown(kpi_html(
        "Total Orders", f"{total_orders:,}",
        f"Period: {yr_min}–{yr_max}" if yr_min != yr_max else f"Year: {yr_min}",
        C["orange"], "📦",
    ), unsafe_allow_html=True)

with k4:
    sub_delta = (
        f"<span style='color:{delta_color};font-weight:700;'>"
        f"{delta_sign} ${abs(delta_profit):.2f} vs overall avg</span>"
    )
    st.markdown(kpi_html(
        "Avg Profit / Order", f"${avg_profit:.2f}",
        sub_delta, delta_color, "💵",
    ), unsafe_allow_html=True)

st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHART ROW
# ══════════════════════════════════════════════════════════════════════════════
ch_left, ch_right = st.columns(2)

# ─── Left: Top 10 Categories ─────────────────────────────────────────────────
with ch_left:
    if sel_metric_col == "__count__":
        cat_df = (
            dff.groupby("Category Name")
               .size()
               .nlargest(10)
               .reset_index(name="Value")
               .sort_values("Value")
        )
        x_axis_title = "Order Count"
        txt_fn = lambda v: f"{v:,.0f}"
    else:
        cat_df = (
            dff.groupby("Category Name")[sel_metric_col]
               .sum()
               .nlargest(10)
               .reset_index()
               .rename(columns={sel_metric_col: "Value"})
               .sort_values("Value")
        )
        x_axis_title = sel_metric_name
        txt_fn = lambda v: f"${v/1e3:,.0f}K"

    n_bars     = max(len(cat_df), 1)
    bar_shades = np.linspace(0.3, 1.0, n_bars)

    fig_cat = go.Figure(go.Bar(
        x=cat_df["Value"],
        y=cat_df["Category Name"],
        orientation="h",
        marker=dict(
            color=bar_shades,
            colorscale=[[0, "#A5C4F2"], [1, C["navy"]]],
            showscale=False,
        ),
        text=[txt_fn(v) for v in cat_df["Value"]],
        textposition="outside",
        textfont=dict(size=11, color=C["navy"]),
        hovertemplate=(
            "<b>%{y}</b><br>" + x_axis_title + ": %{x:,.0f}<extra></extra>"
        ),
    ))
    fig_cat.update_layout(
        **_PLOTLY_BASE,
        title=dict(
            text=f"🏆 Top 10 Categories — {x_axis_title}",
            font=dict(size=14, color=C["navy"]),
            x=0,
        ),
        xaxis=dict(
            title=x_axis_title,
            showgrid=True,
            gridcolor=C["grid"],
            zeroline=False,
            tickfont=dict(size=11),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        height=400,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ─── Right: Monthly Trend ─────────────────────────────────────────────────────
with ch_right:
    # Pandas ≥2.2 renamed 'M' → 'ME' (month-end)
    try:
        _grp = dff.groupby(pd.Grouper(key=_DATE_COL, freq="ME"))
    except ValueError:
        _grp = dff.groupby(pd.Grouper(key=_DATE_COL, freq="M"))

    if sel_metric_col == "__count__":
        monthly = (
            _grp.size()
                .reset_index(name="Value")
                .rename(columns={_DATE_COL: "Month"})
        )
        y_axis_title = "Order Count"
    else:
        monthly = (
            _grp[sel_metric_col]
                .sum()
                .reset_index()
                .rename(columns={_DATE_COL: "Month", sel_metric_col: "Value"})
        )
        y_axis_title = sel_metric_name

    monthly = monthly.dropna(subset=["Month"])

    fig_trend = go.Figure()

    # Fill area (aesthetic only)
    fig_trend.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Value"],
        mode="none",
        fill="tozeroy",
        fillcolor="rgba(26,115,232,0.07)",
        showlegend=False,
        hoverinfo="skip",
    ))

    # Main line + markers
    fig_trend.add_trace(go.Scatter(
        x=monthly["Month"],
        y=monthly["Value"],
        mode="lines+markers",
        name=y_axis_title,
        line=dict(color=C["blue"], width=2.6),
        marker=dict(
            color=C["blue"],
            size=5,
            line=dict(color=C["white"], width=1.8),
        ),
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>" + y_axis_title + ": %{y:,.0f}<extra></extra>"
        ),
    ))

    # 3-month rolling average overlay
    if len(monthly) >= 3:
        roll_avg = monthly["Value"].rolling(3, min_periods=1).mean()
        fig_trend.add_trace(go.Scatter(
            x=monthly["Month"],
            y=roll_avg,
            mode="lines",
            name="3-Month Avg",
            line=dict(color=C["orange"], width=2.0, dash="dot"),
            hovertemplate="<b>%{x|%b %Y}</b><br>3M Avg: %{y:,.0f}<extra></extra>",
        ))

    fig_trend.update_layout(
        **_PLOTLY_BASE,
        title=dict(
            text=f"📅 Monthly Trend — {y_axis_title}",
            font=dict(size=14, color=C["navy"]),
            x=0,
        ),
        xaxis=dict(
            showgrid=False,
            tickformat="%b %Y",
            tickangle=-30,
            tickfont=dict(size=10.5),
        ),
        yaxis=dict(
            title=y_axis_title,
            showgrid=True,
            gridcolor=C["grid"],
            zeroline=True,
            zerolinecolor=C["grid"],
            tickfont=dict(size=11),
        ),
        legend=dict(orientation="h", x=0, y=-0.22, font=dict(size=11)),
        height=400,
    )
    st.plotly_chart(fig_trend, use_container_width=True)


st.markdown("<hr class='section-hr'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM ROW — Three analytical panels
# ══════════════════════════════════════════════════════════════════════════════
p1, p2, p3 = st.columns(3)


# ─── Panel 1: Executive Summary ───────────────────────────────────────────────
with p1:
    # Late delivery rate
    late_html = "—"
    if "Is Late" in dff.columns:
        late_rate = dff["Is Late"].mean() * 100
        color_late = C["red"] if late_rate > 50 else (C["orange"] if late_rate > 30 else C["green"])
        late_html = (
            f"<span style='color:{color_late};font-weight:700;'>{late_rate:.1f}%</span>"
        )

    # Loss-making orders
    neg_pct   = (dff["Order Profit Per Order"] < 0).mean() * 100
    color_neg = C["red"] if neg_pct > 10 else C["muted"]
    neg_html  = (
        f"<span style='color:{color_neg};font-weight:700;'>{neg_pct:.1f}%</span>"
    )

    # Top market
    top_mkt_s   = dff.groupby("Market")["Sales"].sum()
    top_mkt     = top_mkt_s.idxmax() if not top_mkt_s.empty else "—"
    top_mkt_pct = (top_mkt_s.max() / top_mkt_s.sum() * 100) if len(top_mkt_s) > 0 else 0

    def kv(label: str, value_html: str) -> str:
        return (
            f'<div class="kv-row">'
            f'<strong>{label}</strong>'
            f'<span>{value_html}</span>'
            f'</div>'
        )

    summary_rows = "".join([
        kv("Revenue",            f"${total_sales/1e6:.2f}M across {total_orders:,} orders"),
        kv("Profitability",      f"${total_profit/1e6:.2f}M &nbsp;·&nbsp; margin {profit_margin:.1f}%"),
        kv("Avg Profit / Order", f"${avg_profit:.2f}"),
        kv("Top Market",         f"{top_mkt} ({top_mkt_pct:.1f}% of revenue)"),
        kv("Late Deliveries",    late_html),
        kv("Loss-Making Orders", neg_html),
    ])

    st.markdown(f"""
<div class="card">
  <div class="panel-title">📋 Executive Summary</div>
  {summary_rows}
</div>""", unsafe_allow_html=True)


# ─── Panel 2: Business Insights ───────────────────────────────────────────────
with p2:
    def insight(icon: str, text: str) -> str:
        return (
            f'<div class="insight-row">'
            f'<span class="insight-icon">{icon}</span>'
            f'<p class="insight-text">{text}</p>'
            f'</div>'
        )

    # Best-profit category
    try:
        _cat_profit = dff.groupby("Category Name")["Order Profit Per Order"].sum()
        best_cat    = _cat_profit.idxmax()
        best_val    = _cat_profit.max() / 1e3
        cat_text    = f"<strong>{best_cat}</strong> leads with ${best_val:.0f}K total profit"
    except Exception:
        cat_text = "Category data unavailable"

    # Worst shipping mode
    try:
        if "Shipping Mode" in dff.columns and "Is Late" in dff.columns:
            mode_late   = dff.groupby("Shipping Mode")["Is Late"].mean()
            worst_mode  = mode_late.idxmax()
            worst_rt    = mode_late.max() * 100
            mode_text   = f"<strong>{worst_mode}</strong> has the highest late-delivery rate at {worst_rt:.1f}%"
        else:
            mode_text = "Shipping mode data unavailable"
    except Exception:
        mode_text = "Shipping mode data unavailable"

    # Discount impact
    try:
        if "Discount Category" in dff.columns and "Profit Margin" in dff.columns:
            dc       = dff["Discount Category"].astype(str)
            hi_med   = dff.loc[dc == "High (>15%)",   "Profit Margin"].median()
            no_med   = dff.loc[dc == "No Discount",   "Profit Margin"].median()
            disc_text = (
                f"High-discount margin <strong>{hi_med:.2f}</strong> "
                f"vs no-discount <strong>{no_med:.2f}</strong>"
                if not (pd.isna(hi_med) or pd.isna(no_med))
                else "Insufficient discount data for selection"
            )
        else:
            disc_text = "Discount data unavailable"
    except Exception:
        disc_text = "Discount data unavailable"

    # Peak month
    try:
        peak_month = _MONTHS[int(dff["Order Month"].mode()[0]) - 1] if "Order Month" in dff.columns else "—"
    except Exception:
        peak_month = "—"

    insights_html = "".join([
        insight("🏆", cat_text),
        insight("🚚", mode_text),
        insight("🏷️", disc_text),
        insight("📅", f"<strong>{peak_month}</strong> records the highest order volume"),
    ])

    st.markdown(f"""
<div class="card">
  <div class="panel-title">💡 Business Insights</div>
  {insights_html}
</div>""", unsafe_allow_html=True)


# ─── Panel 3: Key Recommendations ────────────────────────────────────────────
with p3:
    RECS = [
        ("🎯", "Prioritise logistics investment in top markets to cut revenue concentration risk."),
        ("🚛", "Review SLAs with underperforming carriers; target a 30-day on-time delivery improvement."),
        ("💸", "Replace blanket discounts with behaviour-triggered offers to protect profit margin."),
        ("📦", "Allocate greater inventory budget to the highest-profit categories and replicate their margin drivers."),
        ("📅", "Build inventory buffers 6–8 weeks before seasonal peaks to prevent stockout-driven delays."),
    ]

    def rec_row(icon: str, text: str) -> str:
        return (
            f'<div class="rec-row">'
            f'<span style="font-size:15px;flex-shrink:0;">{icon}</span>'
            f'<p class="rec-text">{text}</p>'
            f'</div>'
        )

    recs_html = "".join(rec_row(i, t) for i, t in RECS)

    st.markdown(f"""
<div class="card">
  <div class="panel-title">🎯 Key Recommendations</div>
  {recs_html}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='dash-footer'>"
    "Supply Chain Performance Intelligence &nbsp;·&nbsp; "
    "DataCo Smart Supply Chain Dataset &nbsp;·&nbsp; "
    "Built with Streamlit &amp; Plotly"
    "</div>",
    unsafe_allow_html=True,
)
