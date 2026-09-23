"""
test_statistical_analysis.py

Tests the StatisticalAnalysis module.

Author:
3DPAWS Validation Toolkit
"""

import config

from modules.dataset_manager import DatasetManager
from modules.comparison_manager import ComparisonManager
from modules.statistical_analysis import StatisticalAnalysis


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("\n")
    print("=" * 80)
    print("TEST STATISTICAL ANALYSIS")
    print("=" * 80)

    # ------------------------------------------------------
    # Build Station Catalogue
    # ------------------------------------------------------

    dataset_manager = DatasetManager(

        root_folder=config.STATIONS_OUTPUT_DIR

    )

    stations = dataset_manager.run()

    # ------------------------------------------------------
    # Display Stations
    # ------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("AVAILABLE STATIONS")
    print("=" * 80)

    print(
        f"{'No':>3} "
        f"{'Station':30}"
        f"{'3DPAWS':>10}"
        f"{'KMD':>10}"
        f"{'Status':>18}"
    )

    print("-" * 80)

    for index, station in enumerate(stations, start=1):

        if station.paws_count > 0 and station.kmd_count > 0:

            status = "✓ READY"

        elif station.paws_count == 0:

            status = "No 3DPAWS"

        else:

            status = "No KMD"

        print(

            f"{index:3d} "

            f"{station.display_name:30}"

            f"{station.paws_count:10d}"

            f"{station.kmd_count:10d}"

            f"{status:>18}"

        )

    print("-" * 80)

    # ------------------------------------------------------
    # Select Station
    # ------------------------------------------------------

    while True:

        selection = input(

            "\nEnter station number (Q to Quit): "

        ).strip()

        if selection.upper() == "Q":

            print("\nGoodbye.")

            return

        try:

            selection = int(selection)

            if 1 <= selection <= len(stations):

                break

            print("Invalid station number.")

        except ValueError:

            print("Please enter a valid number.")

    station = stations[selection - 1]

    # ------------------------------------------------------
    # Run Comparison Manager
    # ------------------------------------------------------

    comparison = ComparisonManager(

        station

    )

    job = comparison.run()

    if job is None:

        print("\nComparison could not be completed.")

        return

    # ------------------------------------------------------
    # Run Statistical Analysis
    # ------------------------------------------------------

    analysis = StatisticalAnalysis(

        job

    )

    results = analysis.run()

    # ==========================================================
    # VERIFY STATISTICS RESULT QUALITY
    # ==========================================================

    print("\n")
    print("=" * 80)
    print("STATISTICS RESULT QUALITY CHECK")
    print("=" * 80)

    for result in results:

        if result.group != "Pressure":
            continue

        print("\n")
        print(result.label)
        print("-" * 80)

        print(
            f"Quality Status : "
            f"{result.quality.get('status', '')}"
        )

        print(
            f"Sensor Valid   : "
            f"{result.quality.get('sensor_valid', 0)}"
        )

        print(
            f"Sensor Faulty  : "
            f"{result.quality.get('faulty', 0)}"
        )

        print(
            f"Sensor Missing : "
            f"{result.quality.get('sensor_missing', 0)}"
        )

        print(
            f"Paired         : "
            f"{result.quality.get('paired', result.paired)}"
        )

        print(
            f"Comparison Missing : "
            f"{result.quality.get('missing', 0)}"
        )

        print(
            f"Validation     : "
            f"{result.validation_statistics}"
        )

        print(
            f"Performance    : "
            f"{result.performance_assessment.get('overall', '')}"
        )
# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()