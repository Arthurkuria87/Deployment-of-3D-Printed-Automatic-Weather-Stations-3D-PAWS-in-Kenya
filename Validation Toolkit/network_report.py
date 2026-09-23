"""
network_report_refined.py

Consolidated Chapter 7 generator for the 3D-PAWS multi-station validation study.

Purpose:
- Preserve station-level validation results.
- Present network-level synthesis without pooling raw observations.
- Keep 7.10 as the final, station/network-specific Key Findings section.
- Clearly distinguish temporal agreement, error magnitude, coverage and
  implemented WMO assessment classifications.
"""

from pathlib import Path
import math
import pandas as pd
import matplotlib.pyplot as plt

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


BASE_DIR = Path(__file__).resolve().parent

# ----------------------------------------------------------
# Network output structure
# ----------------------------------------------------------

NETWORK_DIR = (
    BASE_DIR
    / "output"
    / "Network_Validation"
)

RESULTS_DIR = (
    NETWORK_DIR
    / "Results"
)

REPORTS_DIR = (
    NETWORK_DIR
    / "Reports"
)

REPORT_FILE = (
    REPORTS_DIR
    / "3DPAWS_Chapter_7_Results.docx"
)

GRAPHS_DIR = (
    NETWORK_DIR
    / "Graphs"
)


GROUP_ORDER = [
    "Temperature",
    "Humidity",
    "Pressure",
    "Rainfall",
]

PARAMETER_ORDER = {
    "Temperature": ["Tmax", "Tmin", "Tmean"],
    "Humidity": ["RH_Max", "RH_Min", "RH_Mean"],
    "Pressure": ["Pressure_Max", "Pressure_Min", "Pressure_Mean"],
    "Rainfall": ["Rainfall_RG1", "Rainfall_RG2"],
}


def clean(value):
    if value is None:
        return ""

    s = str(value)

    replacements = {
        "Â°C": "°C",
        "Â²": "²",
        "RÂ²": "R²",
        "Â": "",
        "Ã—": "×",
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    return s.strip()


def number(value, decimals=3):
    try:
        x = float(value)
        if math.isnan(x):
            return "N/A"
        return f"{x:.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def percentage(value, decimals=1):
    x = number(value, decimals)
    return "N/A" if x == "N/A" else f"{x}%"


def make_table(document, headers, rows, font_size=8.5):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = clean(header)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(font_size)

    for row in rows:
        cells = table.add_row().cells

        for i, value in enumerate(row):
            cells[i].text = clean(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

            for run in cells[i].paragraphs[0].runs:
                run.font.size = Pt(font_size)

    document.add_paragraph()
    return table


def configure_document(document):
    section = document.sections[0]

    section.top_margin = Inches(0.70)
    section.bottom_margin = Inches(0.70)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    for style_name, size in [
        ("Normal", 10.5),
        ("Heading 1", 15),
        ("Heading 2", 12),
    ]:
        style = document.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def load_results():
    required = {
        "master": "all_station_statistics.csv",
        "parameter": "parameter_network_summary.csv",
        "group": "group_network_summary.csv",
        "assessment": "assessment_summary.csv",
    }

    paths = {
        key: RESULTS_DIR / filename
        for key, filename in required.items()
    }

    missing = [
        str(path)
        for path in paths.values()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Required network result files are missing:\n"
            + "\n".join(missing)
        )

    master = pd.read_csv(paths["master"])
    parameter = pd.read_csv(paths["parameter"])
    group = pd.read_csv(paths["group"])
    assessment = pd.read_csv(paths["assessment"])

    numeric_columns = [
        "Paired",
        "Missing",
        "Coverage (%)",
        "Bias",
        "MAE",
        "RMSE",
        "Correlation",
        "R²",
    ]

    for column in numeric_columns:
        if column in master.columns:
            master[column] = pd.to_numeric(
                master[column],
                errors="coerce",
            )

    for frame in [parameter, group]:
        for column in frame.columns:
            if column not in ["Parameter", "Label", "Group", "Units"]:
                converted = pd.to_numeric(
                    frame[column],
                    errors="coerce",
                )

                if converted.notna().any():
                    frame[column] = converted

    return master, parameter, group, assessment


def save_chart(fig, filename):
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    path = GRAPHS_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_network_graphs(master, parameter_summary):
    """
    Generate a small, publication-oriented set of Chapter 7 figures.

    Figures:
      7.1 Network assessment distribution
      7.2 Median station-level correlation by parameter
      7.3 Median station-level RMSE by parameter
      7.4 Median paired-observation coverage by parameter
      7.5 Mean station-level correlation by parameter group
    """
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------
    # Figure 7.1 - Assessment distribution
    # ------------------------------------------------------
    assessment = (
        master["Assessment"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    categories = [
        "Breakthrough",
        "Threshold",
        "Below Threshold",
    ]

    counts = [
        int((assessment == c).sum())
        for c in categories
    ]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(categories, counts)
    ax.set_title(
        "Distribution of Station-Parameter Performance Assessments"
    )
    ax.set_ylabel("Number of station-parameter results")
    ax.set_xlabel("Performance classification")
    ax.grid(axis="y", alpha=0.25)

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(count),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig_71 = save_chart(
        fig,
        "Figure_7_1_Assessment_Distribution.png",
    )

    # ------------------------------------------------------
    # Figure 7.2 - Median correlation by parameter
    # ------------------------------------------------------
    ps = parameter_summary.copy()

    parameter_order = [
        p
        for group in GROUP_ORDER
        for p in PARAMETER_ORDER.get(group, [])
        if p in set(ps["Parameter"].astype(str))
    ]

    ps["Parameter"] = pd.Categorical(
        ps["Parameter"],
        categories=parameter_order,
        ordered=True,
    )

    ps = ps.sort_values("Parameter")

    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    bars = ax.bar(
        ps["Parameter"].astype(str),
        ps["Median Correlation"],
    )
    ax.set_title(
        "Median Station-Level Correlation by Parameter"
    )
    ax.set_ylabel("Median correlation coefficient (r)")
    ax.set_xlabel("Parameter")
    ax.set_ylim(
        min(-1.0, float(ps["Median Correlation"].min()) - 0.05),
        min(1.0, float(ps["Median Correlation"].max()) + 0.10),
    )
    ax.axhline(0, linewidth=0.8)
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=35, ha="right")

    for bar, value in zip(
        bars,
        ps["Median Correlation"],
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=8,
        )

    fig_72 = save_chart(
        fig,
        "Figure_7_2_Median_Correlation_by_Parameter.png",
    )

    # ------------------------------------------------------
    # Figure 7.3 - Median RMSE by parameter
    # ------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    bars = ax.bar(
        ps["Parameter"].astype(str),
        ps["Median RMSE"],
    )
    ax.set_title(
        "Median Station-Level RMSE by Parameter"
    )
    ax.set_ylabel("Median RMSE")
    ax.set_xlabel("Parameter")
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=35, ha="right")

    for bar, value in zip(
        bars,
        ps["Median RMSE"],
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig_73 = save_chart(
        fig,
        "Figure_7_3_Median_RMSE_by_Parameter.png",
    )

    # ------------------------------------------------------
    # Figure 7.4 - Median coverage by parameter
    # ------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    bars = ax.bar(
        ps["Parameter"].astype(str),
        ps["Median Coverage (%)"],
    )
    ax.set_title(
        "Median Paired-Observation Coverage by Parameter"
    )
    ax.set_ylabel("Median coverage (%)")
    ax.set_xlabel("Parameter")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=35, ha="right")

    for bar, value in zip(
        bars,
        ps["Median Coverage (%)"],
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig_74 = save_chart(
        fig,
        "Figure_7_4_Median_Coverage_by_Parameter.png",
    )

    # ------------------------------------------------------
    # Figure 7.5 - Mean correlation by group
    # ------------------------------------------------------
    group_rows = []

    for group_name in GROUP_ORDER:
        group = ps[
            ps["Group"].astype(str).str.strip()
            == group_name
        ]

        if group.empty:
            continue

        group_rows.append([
            group_name,
            group["Mean Correlation"].mean(),
        ])

    group_df = pd.DataFrame(
        group_rows,
        columns=["Group", "MeanCorrelation"],
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    bars = ax.bar(
        group_df["Group"],
        group_df["MeanCorrelation"],
    )
    ax.set_title(
        "Mean Station-Level Correlation by Parameter Group"
    )
    ax.set_ylabel("Mean correlation coefficient (r)")
    ax.set_xlabel("Parameter group")
    ax.set_ylim(
        min(-1.0, float(group_df["MeanCorrelation"].min()) - 0.05),
        min(1.0, float(group_df["MeanCorrelation"].max()) + 0.10),
    )
    ax.axhline(0, linewidth=0.8)
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(
        bars,
        group_df["MeanCorrelation"],
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=9,
        )

    fig_75 = save_chart(
        fig,
        "Figure_7_5_Mean_Correlation_by_Group.png",
    )

    return {
        "assessment": fig_71,
        "correlation": fig_72,
        "rmse": fig_73,
        "coverage": fig_74,
        "group_correlation": fig_75,
    }


def add_figure(document, figure_path, caption):
    if not figure_path or not Path(figure_path).exists():
        return

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = paragraph.add_run()
    run.add_picture(
        str(figure_path),
        width=Inches(6.3),
    )

    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    caption_run = caption_paragraph.add_run(
        caption
    )
    caption_run.bold = True
    caption_run.font.size = Pt(9)


def add_title(document):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = paragraph.add_run("CHAPTER 7\nRESULTS")
    run.bold = True
    run.font.size = Pt(18)

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = paragraph.add_run(
        "Evaluation and Deployment of 3D-Printed Automatic Weather "
        "Stations (3D-PAWS) in Kenya"
    )
    run.font.size = Pt(11)


def add_71(document, df):
    document.add_heading("7.1 Results Overview", level=1)

    document.add_paragraph(
        "This chapter presents the results of the comparative validation "
        "of 3D-PAWS observations against Kenya Meteorological Department "
        "(KMD) reference observations. Validation was first undertaken "
        "independently for each station and parameter. The resulting "
        "station-level statistics were then synthesized to provide a "
        "multi-station assessment of 3D-PAWS performance."
    )

    document.add_paragraph(
        f"The consolidated assessment comprised {df['Station'].nunique()} "
        f"stations and {len(df)} station-parameter results. The number "
        "of evaluated parameters differed among stations because of "
        "differences in data availability and parameter-specific "
        "assessment eligibility."
    )

    periods = sorted(
        df["Period"].dropna().astype(str).unique()
    )

    if periods:
        document.add_paragraph(
            "The validation periods were retained separately for each "
            "station rather than forcing a common period. The periods "
            "represented in the consolidated dataset were: "
            + "; ".join(periods)
            + "."
        )

    document.add_paragraph(
        "The principal statistics reported in this chapter are paired-"
        "observation coverage, bias, mean absolute error (MAE), root "
        "mean square error (RMSE), and correlation coefficient (r). "
        "Where applicable, performance classifications are reported "
        "according to the criteria implemented in the validation toolkit."
    )


def add_72(document, df, graphs=None):
    document.add_heading(
        "7.2 Data Availability, Completeness and Quality",
        level=1,
    )

    document.add_paragraph(
        "Data availability varied considerably among stations and "
        "parameters. Consequently, station-specific coverage is retained "
        "throughout the analysis rather than assuming equivalent data "
        "availability across the network."
    )

    rows = []

    for station, group in df.groupby("Station", sort=True):
        periods = group["Period"].dropna().astype(str).unique()

        period = (
            periods[0]
            if len(periods) == 1
            else "Multiple periods"
        )

        rows.append([
            station,
            period,
            int(group["Parameter"].nunique()),
            len(group),
            percentage(group["Coverage (%)"].mean()),
            percentage(group["Coverage (%)"].min()),
            percentage(group["Coverage (%)"].max()),
        ])

    make_table(
        document,
        [
            "Station",
            "Validation Period",
            "Parameters",
            "Results",
            "Mean Coverage",
            "Minimum Coverage",
            "Maximum Coverage",
        ],
        rows,
    )

    if graphs and graphs.get("coverage"):
        add_figure(
            document,
            graphs["coverage"],
            "Figure 7.4. Median paired-observation coverage by parameter across the evaluated stations.",
        )

    document.add_paragraph(
        "The highest mean station-level coverage was observed at GARISSA "
        f"({df.groupby('Station')['Coverage (%)'].mean().idxmax()}), "
        "while lower coverage was observed at stations such as KITALE - NEW "
        "and MTWAPA AGROMET STATION. These differences are important when "
        "interpreting the reliability and representativeness of the "
        "parameter-level statistics."
    )

    document.add_paragraph(
        "Unavailable station-parameter combinations were not imputed and "
        "were not automatically interpreted as sensor failures. They "
        "remain outside the evaluated result set."
    )


def ordered_group_parameters(frame, group_name):
    order = PARAMETER_ORDER.get(group_name, [])

    existing = set(
        frame["Parameter"].astype(str)
    )

    ordered = [
        parameter
        for parameter in order
        if parameter in existing
    ]

    ordered.extend(
        parameter
        for parameter in frame["Parameter"].astype(str)
        if parameter not in ordered
    )

    return ordered


def add_parameter_group(
    document,
    master,
    parameter_summary,
    group_name,
    section_number,
):
    document.add_heading(
        f"7.{section_number} {group_name} Validation Results",
        level=1,
    )

    group_data = master[
        master["Group"].astype(str).str.strip() == group_name
    ].copy()

    summary = parameter_summary[
        parameter_summary["Group"].astype(str).str.strip()
        == group_name
    ].copy()

    if group_data.empty:
        document.add_paragraph(
            "No evaluated results were available for this parameter group."
        )
        return

    document.add_paragraph(
        f"The {group_name.lower()} results were evaluated using paired "
        "3D-PAWS and KMD observations available at each station. The "
        "network summary describes the distribution of station-level "
        "performance rather than pooling observations from different "
        "stations."
    )

    ordered_parameters = ordered_group_parameters(
        summary,
        group_name,
    )

    summary["Parameter"] = pd.Categorical(
        summary["Parameter"],
        categories=ordered_parameters,
        ordered=True,
    )

    summary = summary.sort_values("Parameter")

    rows = []

    for _, row in summary.iterrows():
        rows.append([
            row["Parameter"],
            row["Label"],
            int(row["Stations Evaluated"]),
            percentage(row["Median Coverage (%)"]),
            number(row["Median Bias"]),
            number(row["Median MAE"]),
            number(row["Median RMSE"]),
            number(row["Median Correlation"]),
            int(row["Breakthrough"]),
            int(row["Threshold"]),
            int(row["Below Threshold"]),
        ])

    make_table(
        document,
        [
            "Parameter",
            "Description",
            "Stations",
            "Median Coverage",
            "Median Bias",
            "Median MAE",
            "Median RMSE",
            "Median r",
            "Breakthrough",
            "Threshold",
            "Below Threshold",
        ],
        rows,
    )

    document.add_heading(
        f"7.{section_number}.1 Station-Level Results",
        level=2,
    )

    group_data["Parameter"] = pd.Categorical(
        group_data["Parameter"],
        categories=ordered_parameters,
        ordered=True,
    )

    group_data = group_data.sort_values(
        ["Parameter", "Station"]
    )

    rows = []

    for _, row in group_data.iterrows():
        rows.append([
            row["Station"],
            row["Parameter"],
            percentage(row["Coverage (%)"]),
            number(row["Bias"]),
            number(row["MAE"]),
            number(row["RMSE"]),
            number(row["Correlation"]),
            row["Assessment"],
        ])

    make_table(
        document,
        [
            "Station",
            "Parameter",
            "Coverage",
            "Bias",
            "MAE",
            "RMSE",
            "r",
            "Assessment",
        ],
        rows,
    )

    correlation_data = group_data.dropna(
        subset=["Correlation"]
    )

    if not correlation_data.empty:
        highest = correlation_data.loc[
            correlation_data["Correlation"].idxmax()
        ]
        lowest = correlation_data.loc[
            correlation_data["Correlation"].idxmin()
        ]

        document.add_paragraph(
            f"Within the {group_name.lower()} group, the highest "
            f"station-level correlation was observed for "
            f"{highest['Parameter']} at {highest['Station']} "
            f"(r = {float(highest['Correlation']):.3f}), while the "
            f"lowest was observed for {lowest['Parameter']} at "
            f"{lowest['Station']} "
            f"(r = {float(lowest['Correlation']):.3f})."
        )

    rmse_data = group_data.dropna(
        subset=["RMSE"]
    )

    if not rmse_data.empty:
        lowest_rmse = rmse_data.loc[
            rmse_data["RMSE"].idxmin()
        ]
        highest_rmse = rmse_data.loc[
            rmse_data["RMSE"].idxmax()
        ]

        unit_values = group_data[
            group_data["Parameter"]
            == lowest_rmse["Parameter"]
        ]["Units"]

        units = (
            clean(unit_values.iloc[0])
            if len(unit_values)
            else ""
        )

        document.add_paragraph(
            f"The lowest station-level RMSE was observed for "
            f"{lowest_rmse['Parameter']} at {lowest_rmse['Station']} "
            f"({float(lowest_rmse['RMSE']):.3f} {units}), whereas the "
            f"highest was observed for {highest_rmse['Parameter']} at "
            f"{highest_rmse['Station']} "
            f"({float(highest_rmse['RMSE']):.3f} {units})."
        )


def add_77(document, df, graphs=None):
    document.add_heading(
        "7.7 Cross-Station Performance Assessment",
        level=1,
    )

    assessment = (
        df["Assessment"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    total = len(df)

    rows = []

    for category in [
        "Breakthrough",
        "Threshold",
        "Below Threshold",
    ]:
        count = int(
            (assessment == category).sum()
        )

        share = (
            count / total * 100
            if total
            else 0
        )

        rows.append([
            category,
            count,
            f"{share:.1f}%",
        ])

    make_table(
        document,
        [
            "Assessment",
            "Station-Parameter Results",
            "Percentage",
        ],
        rows,
    )

    if graphs and graphs.get("assessment"):
        add_figure(
            document,
            graphs["assessment"],
            "Figure 7.1. Distribution of station-parameter performance assessments across the validation network.",
        )

    breakthrough = int(
        (assessment == "Breakthrough").sum()
    )
    threshold = int(
        (assessment == "Threshold").sum()
    )
    below = int(
        (assessment == "Below Threshold").sum()
    )

    document.add_paragraph(
        f"Across the {total} evaluated station-parameter results, "
        f"{breakthrough} ({breakthrough / total * 100:.1f}%) were "
        "classified as Breakthrough, "
        f"{threshold} ({threshold / total * 100:.1f}%) as Threshold, "
        f"and {below} ({below / total * 100:.1f}%) as Below Threshold "
        "under the criteria implemented in the validation toolkit."
    )

    document.add_paragraph(
        "The assessment distribution is strongly influenced by the "
        "parameter groups. Temperature produced the only Breakthrough "
        "and Threshold classifications in the consolidated dataset, "
        "whereas humidity, pressure and rainfall results were classified "
        "as Below Threshold under the implemented criteria."
    )

    document.add_paragraph(
        "These classifications should not be interpreted independently "
        "of temporal agreement, error magnitude, paired-observation "
        "coverage and station-specific environmental conditions."
    )

    document.add_heading(
        "7.7.1 Performance by Parameter Group",
        level=2,
    )

    rows = []

    for group_name in GROUP_ORDER:
        group = df[
            df["Group"].astype(str).str.strip()
            == group_name
        ]

        if group.empty:
            continue

        a = (
            group["Assessment"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        rows.append([
            group_name,
            len(group),
            int((a == "Breakthrough").sum()),
            int((a == "Threshold").sum()),
            int((a == "Below Threshold").sum()),
        ])

    make_table(
        document,
        [
            "Parameter Group",
            "Results",
            "Breakthrough",
            "Threshold",
            "Below Threshold",
        ],
        rows,
    )


def add_78(document, df, parameter_summary, graphs=None):
    document.add_heading(
        "7.8 Overall Multi-Station Results",
        level=1,
    )

    document.add_paragraph(
        "The consolidated results demonstrate substantial variation "
        "in 3D-PAWS performance among meteorological parameters and "
        "deployment sites. The network statistics presented here are "
        "summaries of station-level results and should not be interpreted "
        "as statistics calculated from a single pooled observation series."
    )

    highest_corr = parameter_summary.loc[
        parameter_summary["Mean Correlation"].idxmax()
    ]

    lowest_corr = parameter_summary.loc[
        parameter_summary["Mean Correlation"].idxmin()
    ]

    document.add_paragraph(
        f"Across the evaluated parameters, {highest_corr['Parameter']} "
        f"recorded the highest mean station-level correlation "
        f"(r = {float(highest_corr['Mean Correlation']):.3f}), while "
        f"{lowest_corr['Parameter']} recorded the lowest "
        f"(r = {float(lowest_corr['Mean Correlation']):.3f})."
    )

    highest_coverage = parameter_summary.loc[
        parameter_summary["Median Coverage (%)"].idxmax()
    ]

    lowest_coverage = parameter_summary.loc[
        parameter_summary["Median Coverage (%)"].idxmin()
    ]

    document.add_paragraph(
        f"Median station-level coverage was highest for "
        f"{highest_coverage['Parameter']} "
        f"({float(highest_coverage['Median Coverage (%)']):.1f}%) "
        f"and lowest for {lowest_coverage['Parameter']} "
        f"({float(lowest_coverage['Median Coverage (%)']):.1f}%)."
    )

    document.add_paragraph(
        "The results therefore support parameter- and station-specific "
        "interpretation of 3D-PAWS performance rather than reliance on "
        "a single network-wide performance score."
    )

    if graphs and graphs.get("group_correlation"):
        add_figure(
            document,
            graphs["group_correlation"],
            "Figure 7.5. Mean station-level correlation by meteorological parameter group.",
        )

    document.add_heading(
        "7.8.1 Notable Station-Specific Results",
        level=2,
    )

    # High-coverage / strong temporal agreement
    valid = df.dropna(
        subset=["Correlation", "Coverage (%)"]
    ).copy()

    if not valid.empty:
        strongest = valid.loc[
            valid["Correlation"].idxmax()
        ]

        document.add_paragraph(
            f"The strongest individual temporal association in the "
            f"consolidated dataset was observed for "
            f"{strongest['Parameter']} at {strongest['Station']} "
            f"(r = {float(strongest['Correlation']):.3f}, "
            f"coverage = {float(strongest['Coverage (%)']):.1f}%)."
        )

    # Explicit low-coverage observations
    low_coverage = valid[
        valid["Coverage (%)"] < 10
    ]

    if not low_coverage.empty:
        for _, row in low_coverage.iterrows():
            document.add_paragraph(
                f"{row['Station']} recorded very limited paired coverage "
                f"for {row['Parameter']} ({float(row['Coverage (%)']):.1f}%). "
                "This result should be treated cautiously because the "
                "small available comparison period limits the robustness "
                "of the associated performance statistics."
            )

    # Extreme error results
    highest_rmse = df.dropna(
        subset=["RMSE"]
    ).loc[
        df.dropna(subset=["RMSE"])["RMSE"].idxmax()
    ]

    document.add_paragraph(
        f"The largest RMSE in the consolidated results was observed for "
        f"{highest_rmse['Parameter']} at {highest_rmse['Station']} "
        f"({float(highest_rmse['RMSE']):.3f} "
        f"{clean(highest_rmse['Units'])}). This station-parameter result "
        "should be interpreted alongside its data coverage and the "
        "station-specific observation conditions rather than being used "
        "alone to characterize network performance."
    )


def add_79(document, df, parameter_summary, graphs=None):
    document.add_heading(
        "7.9 Statistical Performance and Interpretation",
        level=1,
    )

    document.add_paragraph(
        "The statistical results show that temporal agreement and "
        "absolute agreement were not necessarily equivalent. Correlation "
        "coefficients describe the degree to which 3D-PAWS and KMD "
        "observations varied together, whereas bias, MAE and RMSE "
        "describe differences in magnitude. Consequently, a parameter "
        "may demonstrate strong temporal correspondence while still "
        "showing relatively large systematic or absolute differences."
    )

    # Group-level interpretation
    for group_name in GROUP_ORDER:
        group = parameter_summary[
            parameter_summary["Group"].astype(str).str.strip()
            == group_name
        ]

        if group.empty:
            continue

        strongest = group.loc[
            group["Mean Correlation"].idxmax()
        ]

        lowest_error = group.loc[
            group["Mean RMSE"].idxmin()
        ]

        document.add_paragraph(
            f"For {group_name.lower()}, {strongest['Parameter']} had "
            f"the highest mean station-level correlation "
            f"(r = {float(strongest['Mean Correlation']):.3f}), while "
            f"{lowest_error['Parameter']} had the lowest mean station-"
            f"level RMSE ({float(lowest_error['Mean RMSE']):.3f} "
            f"{clean(lowest_error['Units'])})."
        )

    if graphs and graphs.get("correlation"):
        add_figure(
            document,
            graphs["correlation"],
            "Figure 7.2. Median station-level correlation coefficients for the evaluated parameters.",
        )

    if graphs and graphs.get("rmse"):
        add_figure(
            document,
            graphs["rmse"],
            "Figure 7.3. Median station-level RMSE values for the evaluated parameters.",
        )

    document.add_heading(
        "7.9.1 Interpretation of Low-Coverage Results",
        level=2,
    )

    document.add_paragraph(
        "Several station-parameter combinations had substantially lower "
        "paired-observation coverage than the better-performing stations. "
        "Such results are retained because they reflect the actual "
        "availability of the validation datasets; however, lower coverage "
        "reduces the strength with which the corresponding statistics can "
        "be generalized to the full validation period."
    )

    document.add_heading(
        "7.9.2 Interpretation of WMO Performance Classifications",
        level=2,
    )

    document.add_paragraph(
        "The Breakthrough, Threshold and Below Threshold classifications "
        "reported in this chapter follow the performance criteria "
        "implemented in the validation toolkit. They provide a structured "
        "assessment of statistical performance, but they do not by "
        "themselves establish operational suitability. Operational "
        "interpretation should also consider temporal agreement, data "
        "coverage, sensor behaviour, station exposure, calibration and "
        "the intended application of the observations."
    )


def add_710(document, df, parameter_summary):
    document.add_heading(
        "7.10 Key Findings",
        level=1,
    )

    # Temperature
    temperature = parameter_summary[
        parameter_summary["Group"] == "Temperature"
    ]

    if not temperature.empty:
        strongest = temperature.loc[
            temperature["Mean Correlation"].idxmax()
        ]

        document.add_paragraph(
            f"Temperature observations demonstrated meaningful temporal "
            f"agreement across several stations. Within the temperature "
            f"group, {strongest['Parameter']} recorded the highest mean "
            f"station-level correlation (r = "
            f"{float(strongest['Mean Correlation']):.3f}). The temperature "
            "results also contained all of the Breakthrough and Threshold "
            "classifications recorded in the consolidated assessment."
        )

    # Humidity
    humidity = parameter_summary[
        parameter_summary["Group"] == "Humidity"
    ]

    if not humidity.empty:
        strongest = humidity.loc[
            humidity["Mean Correlation"].idxmax()
        ]

        document.add_paragraph(
            f"Relative humidity showed stronger temporal agreement for "
            f"mean humidity than for the maximum and minimum humidity "
            f"statistics. {strongest['Parameter']} recorded the highest "
            f"mean station-level correlation in the humidity group "
            f"(r = {float(strongest['Mean Correlation']):.3f}). "
            "Nevertheless, the humidity parameters were classified as "
            "Below Threshold under the implemented accuracy criteria, "
            "indicating that temporal reproduction did not consistently "
            "translate into close agreement in absolute magnitude."
        )

    # Pressure
    pressure = parameter_summary[
        parameter_summary["Group"] == "Pressure"
    ]

    if not pressure.empty:
        strongest = pressure.loc[
            pressure["Mean Correlation"].idxmax()
        ]

        document.add_paragraph(
            f"Atmospheric pressure showed the greatest station-to-station "
            f"variability and generally weaker temporal agreement than "
            f"temperature and humidity. {strongest['Parameter']} recorded "
            f"the highest mean station-level pressure correlation "
            f"(r = {float(strongest['Mean Correlation']):.3f}). "
            "The pressure results indicate the need for continued "
            "investigation of pressure reduction, elevation correction, "
            "sensor response and station exposure."
        )

    # Rainfall
    rainfall = parameter_summary[
        parameter_summary["Group"] == "Rainfall"
    ]

    if not rainfall.empty:
        strongest = rainfall.loc[
            rainfall["Mean Correlation"].idxmax()
        ]

        document.add_paragraph(
            f"Rainfall showed useful temporal correspondence across the "
            f"network, with {strongest['Parameter']} recording the highest "
            f"mean station-level correlation in the rainfall group "
            f"(r = {float(strongest['Mean Correlation']):.3f}). "
            "Differences in rainfall magnitude should nevertheless be "
            "interpreted in relation to spatial variability of precipitation, "
            "gauge characteristics and station exposure."
        )

    assessment = (
        df["Assessment"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    total = len(df)

    document.add_paragraph(
        f"Across the {total} evaluated station-parameter results, "
        f"{int((assessment == 'Breakthrough').sum())} were classified as "
        "Breakthrough, "
        f"{int((assessment == 'Threshold').sum())} as Threshold, and "
        f"{int((assessment == 'Below Threshold').sum())} as Below "
        "Threshold under the implemented criteria."
    )

    document.add_paragraph(
        "Overall, the multi-station validation demonstrates that "
        "3D-PAWS can reproduce meaningful temporal variability in several "
        "meteorological parameters. However, performance was not uniform "
        "among stations or parameters, and strong temporal agreement did "
        "not consistently translate into compliance with the implemented "
        "accuracy thresholds. The findings support the potential of "
        "3D-PAWS as a cost-effective approach for meteorological "
        "observation network densification, while highlighting the need "
        "for continued sensor calibration, refinement of pressure "
        "reduction and elevation-correction procedures, improved quality "
        "control, and evaluation across additional stations and "
        "environmental conditions before wider operational deployment."
    )


def main():
    master, parameter_summary, group_summary, assessment_summary = (
        load_results()
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = Document()
    configure_document(document)
    add_title(document)

    graphs = generate_network_graphs(
        master,
        parameter_summary,
    )

    add_71(document, master)
    add_72(document, master, graphs)

    section_numbers = {
        "Temperature": 3,
        "Humidity": 4,
        "Pressure": 5,
        "Rainfall": 6,
    }

    for group_name in GROUP_ORDER:
        add_parameter_group(
            document,
            master,
            parameter_summary,
            group_name,
            section_numbers[group_name],
        )

    add_77(document, master, graphs)
    add_78(document, master, parameter_summary, graphs)
    add_79(document, master, parameter_summary, graphs)
    add_710(document, master, parameter_summary)

    document.save(REPORT_FILE)

    # Supporting tables for manuscript preparation.
    parameter_summary.to_csv(
        RESULTS_DIR / "chapter_7_parameter_summary.csv",
        index=False,
    )

    group_summary.to_csv(
        RESULTS_DIR / "chapter_7_group_summary.csv",
        index=False,
    )

    assessment_summary.to_csv(
        RESULTS_DIR / "chapter_7_assessment_summary.csv",
        index=False,
    )

    print()
    print("=" * 80)
    print("REFINED CONSOLIDATED CHAPTER 7 GENERATED")
    print("=" * 80)
    print(f"Stations : {master['Station'].nunique()}")
    print(f"Results  : {len(master)}")
    print(f"Report   : {REPORT_FILE}")
    print(f"Graphs   : {GRAPHS_DIR}")
    print(f"Results  : {RESULTS_DIR}")


if __name__ == "__main__":
    main()