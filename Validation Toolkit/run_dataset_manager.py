"""
Test Dataset Manager

Tests station discovery and dataset inventory.
"""

import config

from modules.dataset_manager import DatasetManager


def main():

    manager = DatasetManager(

        root_folder=config.STATIONS_OUTPUT_DIR

    )

    stations = manager.run()

    print("\n")
    print("=" * 80)
    print("DISCOVERED STATIONS")
    print("=" * 80)

    print(f"Stations Found : {len(stations)}")

    for station in stations:

        print()

        print("=" * 80)
        print(station.name)
        print("=" * 80)

        print(f"3DPAWS Datasets : {station.paws_count}")
        print(f"KMD Datasets    : {station.kmd_count}")
        print(f"Total Datasets  : {station.total_datasets}")

        # --------------------------------------------------
        # 3DPAWS
        # --------------------------------------------------

        if station.paws_datasets:

            print("\n3DPAWS")

            for dataset in station.paws_datasets:

                print(f"   • {dataset.filepath.name}")

        # --------------------------------------------------
        # KMD
        # --------------------------------------------------

        if station.kmd_datasets:

            print("\nKMD")

            for dataset in station.kmd_datasets:

                print(f"   • {dataset.filepath.name}")


if __name__ == "__main__":

    main()