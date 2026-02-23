import re

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, callback
from dotenv import load_dotenv

from services.db import get_db_connection

load_dotenv()

# ── Data (loaded once at startup) ────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    conn = get_db_connection()
    query = """
        SELECT
            j.publication_date,
            j.title,
            j.company,
            j.city,
            j.region,
            j.salary,
            j.tjm,
            j.duration,
            j.experience_level,
            j.url       AS offer_url,
            m.icon_url  AS source
        FROM fct_jobs j
        LEFT JOIN sources_metadatas m ON j.source = m.source_name
    """
    return pd.read_sql(query, conn)


df = load_data()

# ── Theme ────────────────────────────────────────────────────────────────────
# dark[4] → borders, dark[6] → Paper bg, dark[7] → body bg
THEME = {
    "fontFamily": "Inter, sans-serif",
    "headings": {"fontFamily": "Inter, sans-serif"},
    "primaryColor": "indigo",
    "defaultRadius": "md",
    "colors": {
        "dark": [
            "#e4e4e7",  # 0  text
            "#a1a1aa",  # 1  dimmed
            "#71717a",  # 2  more dimmed
            "#52525b",  # 3
            "#27272a",  # 4  borders
            "#1f1f23",  # 5
            "#111113",  # 6  Paper / component bg
            "#09090b",  # 7  body bg
            "#060608",  # 8
            "#030304",  # 9
        ]
    },
}

# Donut chart color palettes
EXP_COLORS = ["indigo.6", "indigo.4", "violet.5", "violet.3", "cyan.5", "teal.4"]
REMOTE_COLORS = {
    "Télétravail 100%": "teal.5",
    "Télétravail partiel": "indigo.5",
    "Présentiel": "violet.4",
    "Pas d'infos": "dark.3",
}

# ── App ──────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    title="Aranae – Job Analytics",
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def kpi_card(value: str, label: str) -> dmc.Paper:
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title(value, order=2, fw=600, lts="-0.04em"),
                dmc.Text(
                    label,
                    c="dimmed",
                    size="xs",
                    tt="uppercase",
                    fw=500,
                    lts="0.06em",
                ),
            ],
            gap=4,
        ),
        withBorder=True,
        p="xl",
        radius="md",
    )


def section_label(text: str) -> dmc.Text:
    return dmc.Text(
        text,
        c="dimmed",
        size="xs",
        tt="uppercase",
        fw=600,
        lts="0.08em",
        mb="md",
    )


def _duration_sort_key(d: str) -> int:
    """Numeric sort key for duration strings (e.g. '3 mois' → 3)."""
    m = re.search(r"(\d+)", str(d))
    return int(m.group(1)) if m else 9999


# ── Layout ───────────────────────────────────────────────────────────────────
city_options = sorted(df["city"].dropna().unique())

app.layout = dmc.MantineProvider(
    theme=THEME,
    forceColorScheme="dark",
    children=dmc.AppShell(
        [
            # ── Header ───────────────────────────────────────────────────
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Text("🕸️", size="xl"),
                                dmc.Title("Aranae", order=5, fw=600, lts="-0.02em"),
                            ],
                            gap="xs",
                        ),
                        dmc.Text("Job Analytics", c="dimmed", size="sm"),
                    ],
                    justify="space-between",
                    px="xl",
                    h="100%",
                ),
                withBorder=True,
            ),
            # ── Main ─────────────────────────────────────────────────────
            dmc.AppShellMain(
                dmc.Container(
                    dmc.Stack(
                        [
                            # Filters
                            dmc.MultiSelect(
                                id="city-filter",
                                data=city_options,
                                placeholder="Filter by city…",
                                searchable=True,
                                clearable=True,
                                w=380,
                                size="sm",
                            ),
                            # KPI cards
                            dmc.Grid(id="kpi-grid", gutter="md"),
                            # ── Time series ─────────────────────────────
                            dmc.Paper(
                                [
                                    section_label("Dynamique du marché"),
                                    dmc.AreaChart(
                                        id="time-chart",
                                        data=[],
                                        dataKey="month",
                                        series=[
                                            {"name": "Offres", "color": "indigo.5"},
                                            {
                                                "name": "TJM moyen (€)",
                                                "color": "violet.4",
                                                "yAxisId": "right",
                                            },
                                        ],
                                        h=260,
                                        withRightYAxis=True,
                                        rightYAxisLabel="TJM (€)",
                                        yAxisLabel="Offres",
                                        withGradient=True,
                                        fillOpacity=0.12,
                                        strokeWidth=2,
                                        withDots=False,
                                        curveType="monotone",
                                        gridAxis="y",
                                        tickLine="none",
                                        withTooltip=True,
                                        tooltipAnimationDuration=150,
                                        withLegend=True,
                                        connectNulls=True,
                                    ),
                                ],
                                withBorder=True,
                                p="xl",
                                radius="md",
                            ),
                            # ── Charts row ──────────────────────────────
                            dmc.Grid(
                                [
                                    # Top cities
                                    dmc.GridCol(
                                        dmc.Paper(
                                            [
                                                section_label("Top Villes"),
                                                dmc.BarChart(
                                                    id="city-chart",
                                                    data=[],
                                                    dataKey="city",
                                                    series=[
                                                        {
                                                            "name": "count",
                                                            "color": "indigo.5",
                                                        }
                                                    ],
                                                    h=280,
                                                    barProps={"radius": 4},
                                                    gridAxis="y",
                                                    tickLine="none",
                                                    withTooltip=True,
                                                    tooltipAnimationDuration=150,
                                                    withLegend=False,
                                                ),
                                            ],
                                            withBorder=True,
                                            p="xl",
                                            radius="md",
                                        ),
                                        span=5,
                                    ),
                                    # Experience + Remote donuts stacked
                                    dmc.GridCol(
                                        dmc.Stack(
                                            [
                                                # Experience level
                                                dmc.Paper(
                                                    [
                                                        section_label("Expérience"),
                                                        dmc.Center(
                                                            dmc.DonutChart(
                                                                id="experience-chart",
                                                                data=[],
                                                                h=170,
                                                                size="110",
                                                                thickness=22,
                                                                paddingAngle=2,
                                                                strokeWidth=0,
                                                                withTooltip=True,
                                                                tooltipAnimationDuration=150,
                                                                withLabels=False,
                                                            ),
                                                            mt="xs",
                                                        ),
                                                        dmc.Stack(
                                                            id="experience-legend",
                                                            gap=4,
                                                            mt="sm",
                                                        ),
                                                    ],
                                                    withBorder=True,
                                                    p="lg",
                                                    radius="md",
                                                ),
                                                # Remote distribution
                                                dmc.Paper(
                                                    [
                                                        section_label("Télétravail"),
                                                        dmc.Center(
                                                            dmc.DonutChart(
                                                                id="remote-chart",
                                                                data=[],
                                                                h=170,
                                                                size="110",
                                                                thickness=22,
                                                                paddingAngle=2,
                                                                strokeWidth=0,
                                                                withTooltip=True,
                                                                tooltipAnimationDuration=150,
                                                                withLabels=False,
                                                            ),
                                                            mt="xs",
                                                        ),
                                                        dmc.Stack(
                                                            id="remote-legend",
                                                            gap=4,
                                                            mt="sm",
                                                        ),
                                                    ],
                                                    withBorder=True,
                                                    p="lg",
                                                    radius="md",
                                                ),
                                            ],
                                            gap="md",
                                        ),
                                        span=3,
                                    ),
                                    # Duration histogram
                                    dmc.GridCol(
                                        dmc.Paper(
                                            [
                                                section_label("Durée de mission"),
                                                dmc.BarChart(
                                                    id="duration-chart",
                                                    data=[],
                                                    dataKey="duration",
                                                    series=[
                                                        {
                                                            "name": "count",
                                                            "color": "violet.5",
                                                        }
                                                    ],
                                                    h=280,
                                                    orientation="horizontal",
                                                    barProps={"radius": [0, 4, 4, 0]},
                                                    gridAxis="x",
                                                    tickLine="none",
                                                    withTooltip=True,
                                                    tooltipAnimationDuration=150,
                                                    withLegend=False,
                                                ),
                                            ],
                                            withBorder=True,
                                            p="xl",
                                            radius="md",
                                        ),
                                        span=4,
                                    ),
                                ],
                                gutter="md",
                            ),
                            # ── Table ───────────────────────────────────
                            dmc.Paper(
                                [
                                    section_label("Latest Offers"),
                                    dag.AgGrid(
                                        id="jobs-table",
                                        columnDefs=[
                                            {
                                                "field": "source",
                                                "headerName": "",
                                                "width": 60,
                                                "cellRenderer": "markdown",
                                                "sortable": False,
                                                "filter": False,
                                            },
                                            {
                                                "field": "publication_date",
                                                "headerName": "Date",
                                                "width": 120,
                                            },
                                            {
                                                "field": "title",
                                                "headerName": "Title",
                                                "flex": 2,
                                                "minWidth": 200,
                                            },
                                            {
                                                "field": "company",
                                                "headerName": "Company",
                                                "flex": 1,
                                                "minWidth": 120,
                                            },
                                            {"field": "city", "headerName": "City", "width": 120},
                                            {"field": "region", "headerName": "Region", "width": 130},
                                            {"field": "salary", "headerName": "Salary", "width": 120},
                                            {"field": "tjm", "headerName": "TJM", "width": 90},
                                            {"field": "duration", "headerName": "Duration", "width": 120},
                                            {
                                                "field": "experience_level",
                                                "headerName": "Level",
                                                "width": 110,
                                            },
                                            {
                                                "field": "offer_url",
                                                "headerName": "Link",
                                                "width": 90,
                                                "cellRenderer": "markdown",
                                                "sortable": False,
                                                "filter": False,
                                            },
                                        ],
                                        rowData=[],
                                        className="ag-theme-quartz-dark",
                                        style={"height": "480px"},
                                        dashGridOptions={
                                            "pagination": True,
                                            "paginationPageSize": 20,
                                            "rowHeight": 44,
                                        },
                                    ),
                                ],
                                withBorder=True,
                                p="xl",
                                radius="md",
                            ),
                        ],
                        gap="lg",
                        py="xl",
                    ),
                    size="xl",
                    px="xl",
                ),
            ),
        ],
        header={"height": 56},
        padding=0,
    ),
)


# ── Callback ─────────────────────────────────────────────────────────────────
@callback(
    Output("kpi-grid", "children"),
    Output("time-chart", "data"),
    Output("city-chart", "data"),
    Output("experience-chart", "data"),
    Output("experience-chart", "chartLabel"),
    Output("experience-legend", "children"),
    Output("duration-chart", "data"),
    Output("remote-chart", "data"),
    Output("remote-legend", "children"),
    Output("jobs-table", "rowData"),
    Input("city-filter", "value"),
)
def update(selected_cities: list | None):
    flt = df.copy()
    if selected_cities:
        flt = flt[flt["city"].isin(selected_cities)]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    tjm_nums = (
        flt["tjm"].dropna().astype(str).str.extract(r"(\d+)")[0].dropna().astype(float)
    )
    avg_tjm = f"{int(tjm_nums.mean())} €" if not tjm_nums.empty else "N/A"

    kpis = [
        dmc.GridCol(kpi_card(val, lbl), span=3)
        for val, lbl in [
            (f"{len(flt):,}", "Total Offers"),
            (f"{flt['company'].nunique():,}", "Companies"),
            (avg_tjm, "Avg TJM"),
            (f"{flt['city'].nunique():,}", "Cities"),
        ]
    ]

    # ── Time series ──────────────────────────────────────────────────────────
    ts = flt.copy()
    ts["date"] = pd.to_datetime(ts["publication_date"], errors="coerce")
    ts = ts.dropna(subset=["date"])
    ts["month_ts"] = ts["date"].dt.to_period("M").dt.to_timestamp()
    ts["tjm_num"] = ts["tjm"].astype(str).str.extract(r"(\d+)")[0].astype(float)

    if not ts.empty:
        monthly = (
            ts.groupby("month_ts")
            .agg(Offres=("title", "count"), tjm_num=("tjm_num", "mean"))
            .reset_index()
            .sort_values("month_ts")
        )
        monthly["month"] = monthly["month_ts"].dt.strftime("%b %Y")
        monthly["TJM moyen (€)"] = monthly["tjm_num"].round(0).fillna(0).astype(int)
        time_data = monthly[["month", "Offres", "TJM moyen (€)"]].to_dict("records")
    else:
        time_data = []

    # ── Top cities ───────────────────────────────────────────────────────────
    city_counts = flt["city"].value_counts().head(10).reset_index()
    city_counts.columns = ["city", "count"]

    # ── Experience level donut ────────────────────────────────────────────────
    exp_counts = (
        flt["experience_level"].dropna().value_counts().reset_index()
    )
    exp_counts.columns = ["name", "value"]
    total_exp = int(exp_counts["value"].sum())

    exp_data = [
        {
            "name": row["name"],
            "value": int(row["value"]),
            "color": EXP_COLORS[i % len(EXP_COLORS)],
        }
        for i, row in exp_counts.iterrows()
    ]

    # Custom legend: colored dot + name + percentage
    exp_legend = [
        dmc.Group(
            [
                dmc.Box(
                    style={
                        "width": 8,
                        "height": 8,
                        "borderRadius": "50%",
                        "backgroundColor": f"var(--mantine-color-{item['color'].replace('.', '-')})",
                        "flexShrink": 0,
                    }
                ),
                dmc.Text(item["name"], size="xs", c="dimmed", style={"flex": 1}),
                dmc.Text(
                    f"{item['value'] / total_exp:.0%}" if total_exp else "—",
                    size="xs",
                    fw=500,
                ),
            ],
            gap="xs",
            wrap="nowrap",
        )
        for item in exp_data
    ] if exp_data else []

    # DonutChart center label: dominant level
    chart_label = exp_data[0]["name"] if exp_data else ""

    # ── Duration histogram ───────────────────────────────────────────────────
    dur_counts = flt["duration"].dropna().value_counts().reset_index()
    dur_counts.columns = ["duration", "count"]
    dur_counts["sort_key"] = dur_counts["duration"].apply(_duration_sort_key)
    dur_counts = dur_counts.sort_values("sort_key").head(10)
    dur_data = dur_counts[["duration", "count"]].to_dict("records")

    # ── Remote distribution ──────────────────────────────────────────────────
    remote_counts = flt["remote"].dropna().value_counts().reset_index()
    remote_counts.columns = ["name", "value"]
    total_remote = int(remote_counts["value"].sum())

    remote_data = [
        {
            "name": row["name"],
            "value": int(row["value"]),
            "color": REMOTE_COLORS.get(row["name"], "gray.5"),
        }
        for _, row in remote_counts.iterrows()
    ]

    remote_legend = [
        dmc.Group(
            [
                dmc.Box(
                    style={
                        "width": 8,
                        "height": 8,
                        "borderRadius": "50%",
                        "backgroundColor": f"var(--mantine-color-{item['color'].replace('.', '-')})",
                        "flexShrink": 0,
                    }
                ),
                dmc.Text(item["name"], size="xs", c="dimmed", style={"flex": 1}),
                dmc.Text(
                    f"{item['value'] / total_remote:.0%}" if total_remote else "—",
                    size="xs",
                    fw=500,
                ),
            ],
            gap="xs",
            wrap="nowrap",
        )
        for item in remote_data
    ] if remote_data else []

    # ── Table ────────────────────────────────────────────────────────────────
    display = flt[
        [
            "source", "publication_date", "title", "company", "city", "region",
            "salary", "tjm", "duration", "experience_level", "offer_url",
        ]
    ].copy()
    display["source"] = display["source"].apply(
        lambda x: f"![icon]({x})" if pd.notna(x) and x else ""
    )
    display["offer_url"] = display["offer_url"].apply(
        lambda x: f"[Open →]({x})" if pd.notna(x) and x else ""
    )

    return (
        kpis,
        time_data,
        city_counts.to_dict("records"),
        exp_data,
        chart_label,
        exp_legend,
        dur_data,
        remote_data,
        remote_legend,
        display.fillna("").to_dict("records"),
    )


if __name__ == "__main__":
    app.run(debug=True)
