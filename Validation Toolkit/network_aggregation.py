"""
network_aggregation.py

Aggregates station-level 3D-PAWS validation statistics
into a single network-level dataset.

This module does NOT modify any existing station outputs.
"""

from pathlib import Path
import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

STATIONS_DIR = (
    BASE_DIR
    / "output"
    / "Stations"
)

NETWORK_DIR = (
    BASE_DIR
    / "output"
    / "Network_Validation"
)

RESULTS_DIR = (
    NETWORK_DIR
    / "Results"
)

MASTER_FILE = (
    RESULTS_DIR
    / "all_station_statistics.csv"
)


# ==========================================================
# EXPECTED CSV STRUCTURE
# ==========================================================

REQUIRED_COLUMNS = [

    "Station",
    "Period",
    "Group",
    "Parameter",
    "Label",
    "Units",
    "PAWS Column",
    "KMD Column",
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
    "WMO Criterion",
    "WMO Requirement",
    "WMO Goal",
    "WMO Breakthrough",
    "WMO Threshold",

]


# ==========================================================
# FIND STATION CSV FILES
# ==========================================================

def find_station_csvs():

    files = sorted(
        STATIONS_DIR.rglob(
            "*_statistics.csv"
        )
    )

    return files


# ==========================================================
# LOAD ONE STATION FILE
# ==========================================================

def load_station_csv(
    csv_path
):

    try:

        df = pd.read_csv(
            csv_path
        )

    except Exception as exc:

        print(
            f"ERROR loading: "
            f"{csv_path}"
        )

        print(
            f"Reason: {exc}"
        )

        return None

    # ------------------------------------------------------
    # Check required columns
    # ------------------------------------------------------

    missing_columns = [

        column

        for column in REQUIRED_COLUMNS

        if column not in df.columns

    ]

    if missing_columns:

        print()
        print(
            "WARNING: Missing columns"
        )

        print(
            f"File: {csv_path}"
        )

        for column in missing_columns:

            print(
                f"  - {column}"
            )

        return None

    # ------------------------------------------------------
    # Add source file for traceability
    # ------------------------------------------------------

    df["Source File"] = (
        csv_path.name
    )

    return df


# ==========================================================
# MAIN AGGREGATION
# ==========================================================

def aggregate():

    print()
    print("=" * 80)
    print(
        "3D-PAWS NETWORK STATISTICS AGGREGATION"
    )
    print("=" * 80)

    # ------------------------------------------------------
    # Create output directories
    # ------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------
    # Find station files
    # ------------------------------------------------------

    csv_files = (
        find_station_csvs()
    )

    if not csv_files:

        print()
        print(
            "ERROR: No station statistics CSV files found."
        )

        print(
            f"Search location: {STATIONS_DIR}"
        )

        return None

    print()
    print(
        f"Station CSV files found: "
        f"{len(csv_files)}"
    )

    # ------------------------------------------------------
    # Load files
    # ------------------------------------------------------

    dataframes = []

    station_summary = []

    for csv_path in csv_files:

        print()
        print(
            "-" * 80
        )

        print(
            f"Loading: {csv_path.name}"
        )

        df = load_station_csv(
            csv_path
        )

        if df is None:

            print(
                "STATUS: FAILED"
            )

            continue

        # --------------------------------------------------
        # Station identification
        # --------------------------------------------------

        if "Station" in df.columns:

            station_values = (
                df["Station"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )

        else:

            station_values = []

        if len(station_values) == 1:

            station = (
                station_values[0]
            )

        elif len(station_values) > 1:

            station = (
                "MULTIPLE STATIONS"
            )

            print(
                "WARNING: Multiple station names "
                "found in this file."
            )

        else:

            station = (
                csv_path.stem
            )

            print(
                "WARNING: Station name not found."
            )

        # --------------------------------------------------
        # Period
        # --------------------------------------------------

        periods = (

            df["Period"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()

        )

        if len(periods) == 1:

            period = periods[0]

        elif len(periods) > 1:

            period = (
                "MULTIPLE PERIODS"
            )

        else:

            period = ""

        # --------------------------------------------------
        # Parameters
        # --------------------------------------------------

        parameters = (

            df["Parameter"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()

        )

        print(
            f"Station   : {station}"
        )

        print(
            f"Period    : {period}"
        )

        print(
            f"Rows      : {len(df)}"
        )

        print(
            f"Parameters: {len(parameters)}"
        )

        print(
            "STATUS    : LOADED"
        )

        # --------------------------------------------------
        # Add to aggregation
        # --------------------------------------------------

        dataframes.append(
            df
        )

        station_summary.append({

            "Station": station,

            "Period": period,

            "Rows": len(df),

            "Parameters": len(
                parameters
            ),

            "Source File": csv_path.name,

        })

    # ======================================================
    # COMBINE
    # ======================================================

    if not dataframes:

        print()
        print(
            "ERROR: No valid station files "
            "could be loaded."
        )

        return None

    master = pd.concat(
        dataframes,
        ignore_index=True,
    )

    # ======================================================
    # BASIC VALIDATION
    # ======================================================

    print()
    print("=" * 80)
    print(
        "NETWORK DATASET SUMMARY"
    )
    print("=" * 80)

    print()
    print(
        f"Stations loaded : "
        f"{len(station_summary)}"
    )

    print(
        f"Total rows      : "
        f"{len(master)}"
    )

    print()

    # ------------------------------------------------------
    # Station counts
    # ------------------------------------------------------

    print(
        "Rows by station:"
    )

    station_counts = (
        master
        .groupby("Station")
        .size()
        .sort_index()
    )

    for station, count in (
        station_counts.items()
    ):

        print(
            f"  {station:<35} "
            f"{count:>5}"
        )

    # ------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------

    duplicate_columns = [

        "Station",
        "Period",
        "Parameter",

    ]

    duplicates = (
        master
        .duplicated(
            subset=duplicate_columns,
            keep=False,
        )
    )

    duplicate_count = int(
        duplicates.sum()
    )

    print()
    print(
        f"Duplicate station-parameter records: "
        f"{duplicate_count}"
    )

    # ======================================================
    # SAVE MASTER DATASET
    # ======================================================

    master.to_csv(
        MASTER_FILE,
        index=False,
    )

    print()
    print("=" * 80)
    print(
        "NETWORK AGGREGATION COMPLETED"
    )
    print("=" * 80)

    print()
    print(
        f"Master dataset:"
    )

    print(
        MASTER_FILE
    )

    print()
    print(
        f"Stations included : "
        f"{len(station_summary)}"
    )

    print(
        f"Rows included     : "
        f"{len(master)}"
    )

    print(
        f"Output directory   : "
        f"{RESULTS_DIR}"
    )

    # ------------------------------------------------------
    # Station summary
    # ------------------------------------------------------

    summary_df = pd.DataFrame(
        station_summary
    )

    summary_file = (
        RESULTS_DIR
        / "station_summary.csv"
    )

    summary_df.to_csv(
        summary_file,
        index=False,
    )

    print()
    print(
        f"Station summary:"
    )

    print(
        summary_file
    )

    return master


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    aggregate()