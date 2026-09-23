"""
test_wmo_discovery.py

Tests whether the WMO assessment workflow can discover
all station comparison datasets.

Author:
3DPAWS Validation Toolkit
"""

from pathlib import Path


# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = Path(
    r"C:\Users\AK\OneDrive\KMD\WMO-TECO 2026 ON 3DPAWS"
    r"\\DATA Analysis\3DPAWS_Validation_Toolkit"
)

STATIONS_DIR = BASE_DIR / "output" / "Stations"


# ==========================================================
# EXPECTED PARAMETERS
# ==========================================================

EXPECTED_PARAMETERS = {

    "Tmax": (
        "Tmax_3DPAWS",
        "Tmax_KMD",
    ),

    "Tmin": (
        "Tmin_3DPAWS",
        "Tmin_KMD",
    ),

    "RH_Max": (
        "RH_Max_3DPAWS",
        "RH_Max_KMD",
    ),

    "RH_Min": (
        "RH_Min_3DPAWS",
        "RH_Min_KMD",
    ),

    "RH_Mean": (
        "RH_Mean_3DPAWS",
        "RH_Mean_KMD",
    ),

    "Pressure_Max": (
        "Pressure_Max_3DPAWS",
        "Pressure_Max_KMD",
    ),

    "Pressure_Min": (
        "Pressure_Min_3DPAWS",
        "Pressure_Min_KMD",
    ),

    "Pressure_Mean": (
        "Pressure_Mean_3DPAWS",
        "Pressure_Mean_KMD",
    ),

    "Rain_RG1": (
        "Rain_RG1_3DPAWS",
        "Rain_RG1_KMD",
    ),

    "Rain_RG2": (
        "Rain_RG2_3DPAWS",
        "Rain_RG2_KMD",
    ),
}


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\n")
    print("=" * 80)
    print("WMO ASSESSMENT DATASET DISCOVERY TEST")
    print("=" * 80)

    print(f"\nStations directory:")
    print(STATIONS_DIR)

    if not STATIONS_DIR.exists():

        print("\nERROR")
        print("-" * 80)
        print("Stations directory does not exist.")

        return

    # ------------------------------------------------------
    # Discover comparison CSV files
    # ------------------------------------------------------

    comparison_files = sorted(
        STATIONS_DIR.rglob("*_Comparison.csv")
    )

    print("\n")
    print("=" * 80)
    print("DISCOVERED COMPARISON DATASETS")
    print("=" * 80)

    print(
        f"\nTotal comparison files found : "
        f"{len(comparison_files)}"
    )

    if not comparison_files:

        print("\nNO COMPARISON FILES FOUND.")
        return

    # ------------------------------------------------------
    # Inspect each file
    # ------------------------------------------------------

    total_ok = 0
    total_failed = 0

    for index, csv_file in enumerate(
        comparison_files,
        start=1
    ):

        print("\n")
        print("-" * 80)
        print(
            f"[{index}/{len(comparison_files)}] "
            f"{csv_file.name}"
        )
        print("-" * 80)

        # Station folder
        station_folder = csv_file.parent.parent

        print(
            f"Station folder : "
            f"{station_folder.name}"
        )

        print(
            f"File           : "
            f"{csv_file}"
        )

        try:

            import pandas as pd

            data = pd.read_csv(csv_file)

        except Exception as exc:

            print(f"ERROR loading file: {exc}")
            total_failed += 1
            continue

        print(
            f"Rows           : {len(data)}"
        )

        print(
            f"Columns        : {len(data.columns)}"
        )

        # --------------------------------------------------
        # Check parameters
        # --------------------------------------------------

        file_ok = True

        print("\nParameter availability:")

        for parameter, columns in EXPECTED_PARAMETERS.items():

            aws_column, kmd_column = columns

            aws_exists = aws_column in data.columns
            kmd_exists = kmd_column in data.columns

            if aws_exists and kmd_exists:

                status = "OK"

            else:

                status = "MISSING"
                file_ok = False

            print(
                f"  {parameter:<18} : {status}"
            )

            if not aws_exists:
                print(
                    f"      Missing: {aws_column}"
                )

            if not kmd_exists:
                print(
                    f"      Missing: {kmd_column}"
                )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        if file_ok:

            print("\nRESULT : OK")
            total_ok += 1

        else:

            print("\nRESULT : FAILED")
            total_failed += 1

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print("\n")
    print("=" * 80)
    print("DISCOVERY TEST SUMMARY")
    print("=" * 80)

    print(
        f"\nComparison files found : "
        f"{len(comparison_files)}"
    )

    print(
        f"Files OK               : "
        f"{total_ok}"
    )

    print(
        f"Files with problems    : "
        f"{total_failed}"
    )

    print("\n")

    if total_failed == 0:

        print(
            "STATUS : ALL DATASETS READY FOR WMO ASSESSMENT"
        )

    else:

        print(
            "STATUS : SOME DATASETS REQUIRE ATTENTION"
        )

    print("\n")
    print("=" * 80)


if __name__ == "__main__":
    main()