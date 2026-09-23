"""
network_summary.py

Creates cross-station summaries from the completed
station-level 3D-PAWS validation statistics.

Source:
    output/Network_Validation/Results/all_station_statistics.csv

Outputs:
    output/Network_Validation/Results/
        parameter_network_summary.csv
        group_network_summary.csv
        assessment_summary.csv
        station_parameter_summary.csv

This module does not modify station-level outputs.
"""

from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

NETWORK_RESULTS_DIR = (
    BASE_DIR
    / "output"
    / "Network_Validation"
    / "Results"
)

MASTER_FILE = (
    NETWORK_RESULTS_DIR
    / "all_station_statistics.csv"
)


# ==========================================================
# NUMERIC COLUMNS
# ==========================================================

NUMERIC_COLUMNS = [

    "Paired",
    "Missing",
    "Coverage (%)",
    "Bias",
    "MAE",
    "RMSE",
    "Correlation",
    "R²",
    "WMO Requirement",
    "WMO Goal",
    "WMO Breakthrough",
    "WMO Threshold",

]


# ==========================================================
# LOAD MASTER DATASET
# ==========================================================

def load_master_dataset():

    if not MASTER_FILE.exists():

        raise FileNotFoundError(
            f"Master statistics file not found:\n"
            f"{MASTER_FILE}"
        )

    df = pd.read_csv(
        MASTER_FILE
    )

    # ------------------------------------------------------
    # Convert numeric fields
    # ------------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return df


# ==========================================================
# PARAMETER SUMMARY
# ==========================================================

def create_parameter_summary(
    df
):

    records = []

    for parameter, group in (
        df.groupby(
            "Parameter",
            sort=False,
        )
    ):

        correlations = (
            group["Correlation"]
            .dropna()
        )

        rmse = (
            group["RMSE"]
            .dropna()
        )

        mae = (
            group["MAE"]
            .dropna()
        )

        bias = (
            group["Bias"]
            .dropna()
        )

        coverage = (
            group["Coverage (%)"]
            .dropna()
        )

        assessment = (
            group["Assessment"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        records.append({

            "Parameter":
                parameter,

            "Label":
                group["Label"]
                .dropna()
                .iloc[0]
                if not group["Label"]
                .dropna()
                .empty
                else "",

            "Group":
                group["Group"]
                .dropna()
                .iloc[0]
                if not group["Group"]
                .dropna()
                .empty
                else "",

            "Units":
                group["Units"]
                .dropna()
                .iloc[0]
                if not group["Units"]
                .dropna()
                .empty
                else "",

            "Stations Evaluated":
                group["Station"]
                .nunique(),

            "Mean Coverage (%)":
                coverage.mean()
                if not coverage.empty
                else None,

            "Median Coverage (%)":
                coverage.median()
                if not coverage.empty
                else None,

            "Minimum Coverage (%)":
                coverage.min()
                if not coverage.empty
                else None,

            "Maximum Coverage (%)":
                coverage.max()
                if not coverage.empty
                else None,

            "Mean Bias":
                bias.mean()
                if not bias.empty
                else None,

            "Median Bias":
                bias.median()
                if not bias.empty
                else None,

            "Minimum Bias":
                bias.min()
                if not bias.empty
                else None,

            "Maximum Bias":
                bias.max()
                if not bias.empty
                else None,

            "Mean MAE":
                mae.mean()
                if not mae.empty
                else None,

            "Median MAE":
                mae.median()
                if not mae.empty
                else None,

            "Minimum MAE":
                mae.min()
                if not mae.empty
                else None,

            "Maximum MAE":
                mae.max()
                if not mae.empty
                else None,

            "Mean RMSE":
                rmse.mean()
                if not rmse.empty
                else None,

            "Median RMSE":
                rmse.median()
                if not rmse.empty
                else None,

            "Minimum RMSE":
                rmse.min()
                if not rmse.empty
                else None,

            "Maximum RMSE":
                rmse.max()
                if not rmse.empty
                else None,

            "Mean Correlation":
                correlations.mean()
                if not correlations.empty
                else None,

            "Median Correlation":
                correlations.median()
                if not correlations.empty
                else None,

            "Minimum Correlation":
                correlations.min()
                if not correlations.empty
                else None,

            "Maximum Correlation":
                correlations.max()
                if not correlations.empty
                else None,

            "Breakthrough":
                int(
                    (
                        assessment
                        == "Breakthrough"
                    ).sum()
                ),

            "Threshold":
                int(
                    (
                        assessment
                        == "Threshold"
                    ).sum()
                ),

            "Below Threshold":
                int(
                    (
                        assessment
                        == "Below Threshold"
                    ).sum()
                ),

            "Total Assessments":
                int(
                    assessment
                    .isin(
                        [
                            "Breakthrough",
                            "Threshold",
                            "Below Threshold",
                        ]
                    )
                    .sum()
                ),

        })

    result = pd.DataFrame(
        records
    )

    # ------------------------------------------------------
    # Round numeric values
    # ------------------------------------------------------

    numeric_output = [

        "Mean Coverage (%)",
        "Median Coverage (%)",
        "Minimum Coverage (%)",
        "Maximum Coverage (%)",

        "Mean Bias",
        "Median Bias",
        "Minimum Bias",
        "Maximum Bias",

        "Mean MAE",
        "Median MAE",
        "Minimum MAE",
        "Maximum MAE",

        "Mean RMSE",
        "Median RMSE",
        "Minimum RMSE",
        "Maximum RMSE",

        "Mean Correlation",
        "Median Correlation",
        "Minimum Correlation",
        "Maximum Correlation",

    ]

    for column in numeric_output:

        if column in result.columns:

            result[column] = result[
                column
            ].round(4)

    return result


# ==========================================================
# GROUP SUMMARY
# ==========================================================

def create_group_summary(
    df
):

    records = []

    for group_name, group in (
        df.groupby(
            "Group",
            sort=False,
        )
    ):

        correlations = (
            group["Correlation"]
            .dropna()
        )

        rmse = (
            group["RMSE"]
            .dropna()
        )

        mae = (
            group["MAE"]
            .dropna()
        )

        bias = (
            group["Bias"]
            .dropna()
        )

        coverage = (
            group["Coverage (%)"]
            .dropna()
        )

        assessment = (
            group["Assessment"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        records.append({

            "Group":
                group_name,

            "Stations Evaluated":
                group["Station"]
                .nunique(),

            "Parameters Evaluated":
                group["Parameter"]
                .nunique(),

            "Station-Parameter Results":
                len(group),

            "Mean Coverage (%)":
                coverage.mean()
                if not coverage.empty
                else None,

            "Median Coverage (%)":
                coverage.median()
                if not coverage.empty
                else None,

            "Mean Bias":
                bias.mean()
                if not bias.empty
                else None,

            "Median Bias":
                bias.median()
                if not bias.empty
                else None,

            "Mean MAE":
                mae.mean()
                if not mae.empty
                else None,

            "Median MAE":
                mae.median()
                if not mae.empty
                else None,

            "Mean RMSE":
                rmse.mean()
                if not rmse.empty
                else None,

            "Median RMSE":
                rmse.median()
                if not rmse.empty
                else None,

            "Mean Correlation":
                correlations.mean()
                if not correlations.empty
                else None,

            "Median Correlation":
                correlations.median()
                if not correlations.empty
                else None,

            "Breakthrough":
                int(
                    (
                        assessment
                        == "Breakthrough"
                    ).sum()
                ),

            "Threshold":
                int(
                    (
                        assessment
                        == "Threshold"
                    ).sum()
                ),

            "Below Threshold":
                int(
                    (
                        assessment
                        == "Below Threshold"
                    ).sum()
                ),

        })

    result = pd.DataFrame(
        records
    )

    numeric_columns = [
        column
        for column in result.columns
        if column not in [
            "Group"
        ]
    ]

    for column in numeric_columns:

        if result[column].dtype.kind in "fc":

            result[column] = result[
                column
            ].round(4)

    return result


# ==========================================================
# ASSESSMENT SUMMARY
# ==========================================================

def create_assessment_summary(
    df
):

    assessment = (
        df["Assessment"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    total = len(df)

    counts = (
        assessment
        .value_counts()
    )

    records = []

    categories = [

        "Breakthrough",
        "Threshold",
        "Below Threshold",

    ]

    for category in categories:

        count = int(
            counts.get(
                category,
                0,
            )
        )

        percentage = (

            count
            /
            total
            *
            100

            if total > 0

            else 0

        )

        records.append({

            "Assessment":
                category,

            "Records":
                count,

            "Percentage (%)":
                round(
                    percentage,
                    2,
                ),

        })

    return pd.DataFrame(
        records
    )


# ==========================================================
# STATION-PARAMETER SUMMARY
# ==========================================================

def create_station_parameter_summary(
    df
):

    columns = [

        "Station",
        "Period",
        "Group",
        "Parameter",
        "Label",
        "Units",
        "Paired",
        "Missing",
        "Coverage (%)",
        "Bias",
        "MAE",
        "RMSE",
        "Correlation",
        "R²",
        "Assessment",
        "Quality Level",
        "QC Status",

    ]

    available_columns = [

        column

        for column in columns

        if column in df.columns

    ]

    result = (
        df[
            available_columns
        ]
        .copy()
        .sort_values(
            [
                "Station",
                "Group",
                "Parameter",
            ]
        )
    )

    return result


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print("=" * 80)
    print(
        "3D-PAWS NETWORK SUMMARY ANALYSIS"
    )
    print("=" * 80)

    # ------------------------------------------------------
    # Load
    # ------------------------------------------------------

    df = load_master_dataset()

    print()
    print(
        f"Master records loaded: "
        f"{len(df)}"
    )

    print(
        f"Stations: "
        f"{df['Station'].nunique()}"
    )

    # ------------------------------------------------------
    # Parameter summary
    # ------------------------------------------------------

    parameter_summary = (
        create_parameter_summary(
            df
        )
    )

    parameter_file = (
        NETWORK_RESULTS_DIR
        / "parameter_network_summary.csv"
    )

    parameter_summary.to_csv(
        parameter_file,
        index=False,
    )

    # ------------------------------------------------------
    # Group summary
    # ------------------------------------------------------

    group_summary = (
        create_group_summary(
            df
        )
    )

    group_file = (
        NETWORK_RESULTS_DIR
        / "group_network_summary.csv"
    )

    group_summary.to_csv(
        group_file,
        index=False,
    )

    # ------------------------------------------------------
    # Assessment summary
    # ------------------------------------------------------

    assessment_summary = (
        create_assessment_summary(
            df
        )
    )

    assessment_file = (
        NETWORK_RESULTS_DIR
        / "assessment_summary.csv"
    )

    assessment_summary.to_csv(
        assessment_file,
        index=False,
    )

    # ------------------------------------------------------
    # Station parameter summary
    # ------------------------------------------------------

    station_parameter_summary = (
        create_station_parameter_summary(
            df
        )
    )

    station_parameter_file = (
        NETWORK_RESULTS_DIR
        / "station_parameter_summary.csv"
    )

    station_parameter_summary.to_csv(
        station_parameter_file,
        index=False,
    )

    # ======================================================
    # CONSOLE SUMMARY
    # ======================================================

    print()
    print("=" * 80)
    print(
        "NETWORK SUMMARY COMPLETED"
    )
    print("=" * 80)

    print()
    print(
        "Parameter summary:"
    )

    print(
        parameter_summary.to_string(
            index=False
        )
    )

    print()
    print(
        "Assessment summary:"
    )

    print(
        assessment_summary.to_string(
            index=False
        )
    )

    print()
    print(
        "Files generated:"
    )

    print(
        parameter_file
    )

    print(
        group_file
    )

    print(
        assessment_file
    )

    print(
        station_parameter_file
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()