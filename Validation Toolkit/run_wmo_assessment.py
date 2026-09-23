"""
test_wmo_assessment.py

Tests multi-station WMO performance assessment.

Discovers all comparison datasets and applies the
PerformanceAssessment class to every validation parameter.

Author:
3DPAWS Validation Toolkit
"""

from pathlib import Path

import numpy as np
import pandas as pd

from modules.performance_assessment import PerformanceAssessment
from modules.statistics_result import StatisticsResult


# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = Path(
    r"C:\Users\AK\OneDrive\KMD\WMO-TECO 2026 ON 3DPAWS"
    r"\DATA Analysis\3DPAWS_Validation_Toolkit"
)

STATIONS_DIR = (
    BASE_DIR
    / "output"
    / "Stations"
)


# ==========================================================
# PARAMETER MAPPING
# ==========================================================

PARAMETERS = {

    "Tmax": {
        "label": "Maximum Temperature",
        "units": "°C",
        "paws": "Tmax_3DPAWS",
        "kmd": "Tmax_KMD",
        "group": "Temperature",
    },

    "Tmin": {
        "label": "Minimum Temperature",
        "units": "°C",
        "paws": "Tmin_3DPAWS",
        "kmd": "Tmin_KMD",
        "group": "Temperature",
    },

    "RH_Max": {
        "label": "Maximum Relative Humidity",
        "units": "%",
        "paws": "RH_Max_3DPAWS",
        "kmd": "RH_Max_KMD",
        "group": "Humidity",
    },

    "RH_Min": {
        "label": "Minimum Relative Humidity",
        "units": "%",
        "paws": "RH_Min_3DPAWS",
        "kmd": "RH_Min_KMD",
        "group": "Humidity",
    },

    "RH_Mean": {
        "label": "Mean Relative Humidity",
        "units": "%",
        "paws": "RH_Mean_3DPAWS",
        "kmd": "RH_Mean_KMD",
        "group": "Humidity",
    },

    "Pressure_Max": {
        "label": "Maximum Pressure",
        "units": "hPa",
        "paws": "Pressure_Max_3DPAWS",
        "kmd": "Pressure_Max_KMD",
        "group": "Pressure",
    },

    "Pressure_Min": {
        "label": "Minimum Pressure",
        "units": "hPa",
        "paws": "Pressure_Min_3DPAWS",
        "kmd": "Pressure_Min_KMD",
        "group": "Pressure",
    },

    "Pressure_Mean": {
        "label": "Mean Pressure",
        "units": "hPa",
        "paws": "Pressure_Mean_3DPAWS",
        "kmd": "Pressure_Mean_KMD",
        "group": "Pressure",
    },

    "Rainfall_RG1": {
        "label": "Daily Rainfall (Rain Gauge 1)",
        "units": "mm",
        "paws": "Rain_RG1_3DPAWS",
        "kmd": "Rain_RG1_KMD",
        "group": "Rainfall",
    },

    "Rainfall_RG2": {
        "label": "Daily Rainfall (Rain Gauge 2)",
        "units": "mm",
        "paws": "Rain_RG2_3DPAWS",
        "kmd": "Rain_RG2_KMD",
        "group": "Rainfall",
    },
}


# ==========================================================
# VALIDATION METRICS
# ==========================================================

def calculate_validation_statistics(
    paws,
    kmd
):
    """
    Calculate paired validation statistics.

    Zero values are retained.
    Only missing/non-numeric pairs are excluded.
    """

    df = pd.DataFrame({

        "paws": pd.to_numeric(
            paws,
            errors="coerce"
        ),

        "kmd": pd.to_numeric(
            kmd,
            errors="coerce"
        )

    }).dropna()

    if df.empty:

        return {

            "Bias": None,
            "MAE": None,
            "RMSE": None,
            "Correlation": None,
            "R²": None

        }

    paws_values = df["paws"].to_numpy(
        dtype=float
    )

    kmd_values = df["kmd"].to_numpy(
        dtype=float
    )

    errors = (
        paws_values -
        kmd_values
    )

    bias = float(
        np.mean(errors)
    )

    mae = float(
        np.mean(
            np.abs(errors)
        )
    )

    rmse = float(
        np.sqrt(
            np.mean(
                errors ** 2
            )
        )
    )

    # ------------------------------------------------------
    # Correlation
    # ------------------------------------------------------

    if (

        len(df) < 2

        or

        np.std(paws_values) == 0

        or

        np.std(kmd_values) == 0

    ):

        correlation = None

        r_squared = None

    else:

        correlation = float(
            np.corrcoef(
                kmd_values,
                paws_values
            )[0, 1]
        )

        r_squared = float(
            correlation ** 2
        )

    return {

        "Bias": bias,

        "MAE": mae,

        "RMSE": rmse,

        "Correlation": correlation,

        "R²": r_squared

    }


# ==========================================================
# STATION NAME
# ==========================================================

def station_display_name(
    station_folder
):

    name = station_folder.name

    if name.endswith("_"):

        name = name[:-1]

    return name.replace(
        "_",
        " "
    ).title()


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\n")
    print("=" * 80)
    print("MULTI-STATION WMO ASSESSMENT TEST")
    print("=" * 80)

    if not STATIONS_DIR.exists():

        print(
            "\nERROR: Stations directory not found."
        )

        print(
            STATIONS_DIR
        )

        return

    # ------------------------------------------------------
    # Discover comparison datasets
    # ------------------------------------------------------

    comparison_files = sorted(
        STATIONS_DIR.rglob(
            "*_Comparison.csv"
        )
    )

    print(
        f"\nComparison datasets discovered : "
        f"{len(comparison_files)}"
    )

    if not comparison_files:

        print(
            "\nNo comparison datasets found."
        )

        return

    assessor = PerformanceAssessment()

    all_results = []

    # ======================================================
    # PROCESS EVERY DATASET
    # ======================================================

    for index, csv_file in enumerate(
        comparison_files,
        start=1
    ):

        station_folder = (
            csv_file.parent.parent
        )

        station_name = station_display_name(
            station_folder
        )

        print("\n")
        print("=" * 80)

        print(
            f"[{index}/{len(comparison_files)}] "
            f"{station_name}"
        )

        print("=" * 80)

        print(
            f"Dataset : {csv_file.name}"
        )

        try:

            data = pd.read_csv(
                csv_file
            )

        except Exception as exc:

            print(
                f"ERROR loading dataset: {exc}"
            )

            continue

        # --------------------------------------------------
        # Process parameters
        # --------------------------------------------------

        for parameter, config in PARAMETERS.items():

            paws_column = config["paws"]

            kmd_column = config["kmd"]

            # ----------------------------------------------
            # Check columns
            # ----------------------------------------------

            if (

                paws_column not in data.columns

                or

                kmd_column not in data.columns

            ):

                print(
                    f"\n{config['label']}"
                )

                print(
                    "  STATUS : MISSING COLUMNS"
                )

                continue

            # ----------------------------------------------
            # Calculate statistics
            # ----------------------------------------------

            validation_statistics = (
                calculate_validation_statistics(
                    data[paws_column],
                    data[kmd_column]
                )
            )

            paired = int(
                pd.DataFrame({

                    "paws": data[paws_column],

                    "kmd": data[kmd_column]

                })
                .apply(
                    pd.to_numeric,
                    errors="coerce"
                )
                .dropna()
                .shape[0]
            )

            # ----------------------------------------------
            # Build StatisticsResult
            # ----------------------------------------------

            result = StatisticsResult(

                parameter=parameter,

                label=config["label"],

                group=config["group"],

                units=config["units"],

                paws_column=paws_column,

                kmd_column=kmd_column,

                paired=paired,

                missing=len(data) - paired,

                validation_statistics=
                    validation_statistics

            )
            # Add dynamic metadata if your current
            # StatisticsResult supports it.


            result.station = station_name

            result.source_file = (
                csv_file.name
            )

            # ----------------------------------------------
            # WMO assessment
            # ----------------------------------------------

            assessment = assessor.assess(
                result
            )

            result.performance_assessment = (
                assessment
            )

            all_results.append(
                result
            )

            # ----------------------------------------------
            # Display
            # ----------------------------------------------

            print(
                f"\n{config['label']}"
            )

            print(
                "-" * 60
            )

            print(
                f"  Paired       : {paired}"
            )

            print(
                f"  RMSE         : "
                f"{validation_statistics['RMSE']}"
            )

            print(
                f"  Correlation  : "
                f"{validation_statistics['Correlation']}"
            )

            print(
                f"  WMO Status   : "
                f"{assessment.get('overall')}"
            )

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\n")
    print("=" * 80)
    print("MULTI-STATION WMO ASSESSMENT SUMMARY")
    print("=" * 80)

    print(
        f"\nStations processed : "
        f"{len(comparison_files)}"
    )

    print(
        f"Results generated  : "
        f"{len(all_results)}"
    )

    # ------------------------------------------------------
    # Assessment counts
    # ------------------------------------------------------

    counts = {

        "Goal": 0,

        "Breakthrough": 0,

        "Threshold": 0,

        "Below Threshold": 0,

        "Not Available": 0

    }

    for result in all_results:

        status = (
            result.performance_assessment
            .get(
                "overall",
                "Not Available"
            )
        )

        if status not in counts:

            counts["Not Available"] += 1

        else:

            counts[status] += 1

    print("\n")
    print("OVERALL WMO RESULTS")
    print("-" * 80)

    for status, count in counts.items():

        print(
            f"{status:<20}: {count}"
        )

    print("\n")
    print("=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":

    main()