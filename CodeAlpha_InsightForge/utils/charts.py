from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _template(theme: str) -> str:
    return "plotly_dark" if theme == "Dark" else "plotly_white"


def histogram(df: pd.DataFrame, x: str, theme: str, nbins: int = 40, title: str | None = None):
    if df.empty or x not in df:
        return None
    return px.histogram(df, x=x, nbins=nbins, title=title, template=_template(theme))


def pie_chart(df: pd.DataFrame, names: str, values: str, theme: str, title: str | None = None):
    if df.empty:
        return None
    return px.pie(df, names=names, values=values, title=title, template=_template(theme))


def line_chart(df: pd.DataFrame, x: str, y: str, theme: str, color: str | None = None, title: str | None = None):
    if df.empty:
        return None
    return px.line(df, x=x, y=y, color=color, title=title, template=_template(theme), markers=True)


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    theme: str,
    orientation: str = "v",
    title: str | None = None,
):
    if df.empty:
        return None
    if orientation == "h":
        return px.bar(df, x=y, y=x, orientation="h", title=title, template=_template(theme))
    return px.bar(df, x=x, y=y, title=title, template=_template(theme))


def time_pivot_heatmap(df: pd.DataFrame, date_col: str, category_col: str, metric_col: str, theme: str, title: str | None = None):
    if df.empty:
        return None
    tmp = df[[date_col, category_col, metric_col]].dropna()
    if tmp.empty:
        return None
    tmp["_month"] = pd.to_datetime(tmp[date_col], errors="coerce").dt.to_period("M").dt.to_timestamp()
    pivot = tmp.pivot_table(index=category_col, columns="_month", values=metric_col, aggfunc="sum").fillna(0)
    if pivot.empty:
        return None
    return heatmap(pivot, theme, title=title)


def box_plot(df: pd.DataFrame, y: str, theme: str, group: str | None = None, title: str | None = None):
    if df.empty:
        return None
    return px.box(df, x=group, y=y, title=title, template=_template(theme))


def correlation_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return df[columns].corr(numeric_only=True)


def heatmap(matrix: pd.DataFrame, theme: str, title: str | None = None):
    if matrix.empty:
        return None
    fig = go.Figure(data=go.Heatmap(z=matrix.values, x=matrix.columns, y=matrix.index, colorscale="Viridis"))
    fig.update_layout(title=title, template=_template(theme))
    return fig


def scatter_matrix(df: pd.DataFrame, dimensions: list[str], theme: str, color: str | None = None):
    if df.empty or len(dimensions) < 2:
        return None
    return px.scatter_matrix(df, dimensions=dimensions, color=color, template=_template(theme))
