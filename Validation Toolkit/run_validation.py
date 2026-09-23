from pathlib import Path

from modules.chords_processor import CHORDSProcessor
from utils.file_utils import extract_metadata, clean_station_filename


def main():
    """
    ==========================================================
    3DPAWS Network Validation Toolkit

    Processes every CHORDS CSV dataset found in data/raw.

    Workflow

        1. Load dataset
        2. Pre-process observations
        3. Validate observations
        4. Generate summaries
        5. Export reports
        6. Record processing log

    ==========================================================
    """

    raw_folder = Path("data/raw")

    csv_files = sorted(raw_folder.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in data/raw/"
        )

    print("=" * 70)
    print("3DPAWS NETWORK VALIDATION TOOLKIT")
    print("=" * 70)

    print(f"\nDatasets Found : {len(csv_files)}")

    successful = 0
    failed = 0

    # ==========================================================
    # Process each dataset
    # ==========================================================

    for index, input_file in enumerate(csv_files, start=1):

        station_name, period = extract_metadata(input_file)

        print("\n" + "=" * 70)
        print(f"Dataset {index} of {len(csv_files)}")
        print(f"Station : {station_name}")
        print(f"Period  : {period}")
        print("=" * 70)

        processor = CHORDSProcessor(input_file)

        try:

            # --------------------------------------------------
            # Load
            # --------------------------------------------------

            processor.load_data()

            # --------------------------------------------------
            # Update station name from CHORDS metadata
            # --------------------------------------------------

            # --------------------------------------------------
            # Use CHORDS metadata only if it is valid
            # Otherwise keep filename-derived station name
            # --------------------------------------------------

            station_name = processor.get_station_name(
            fallback=station_name
)

            # --------------------------------------------------
            # Pre-processing
            # --------------------------------------------------

            processor.parse_timestamps()
            processor.normalize_columns()
            processor.clean_dataset()

            print("\n>>> assess_sensor_availability")
            processor.assess_sensor_availability()

            print("\n>>> validate_dataset")
            processor.validate_dataset()

            print("\n>>> quality_control")
            processor.quality_control()

            print("\n>>> constant_value_check")
            processor.constant_value_check()

            print("\n>>> spike_check")
            processor.spike_check()

            print("\n>>> persistence_check")
            processor.persistence_check()

            print("\n>>> detect_rainfall_reset")
            processor.detect_rainfall_reset()

            print("\n>>> rainfall_integrity_check")
            processor.rainfall_integrity_check()

            print("\n>>> meteorological_consistency_check")
            processor.meteorological_consistency_check()


            processor.build_parameter_validation()

            print("\n>>> export_validation_workbook")
            processor.export_validation_workbook

            print("\nPARAMETER VALIDATION SUMMARY")
            print("=" * 100)
            print(processor.parameter_validation)
            print("=" * 100)


            print("\n>>> generate_daily_summary")
            processor.generate_daily_summary()

            # --------------------------------------------------
            # Export
            # --------------------------------------------------

            processor.export_results(

                station_name=station_name,

                period=period

            )

            processor.write_processing_log(

                station_name=station_name,

                period=period,

                input_file=input_file.name,

                status="SUCCESS"

            )

            successful += 1

            print("\n✓ Dataset processed successfully")

        except Exception as e:

            failed += 1

            print(f"\n✗ Processing failed")

            print(e)

            processor.write_processing_log(

                station_name=station_name,

                period=period,

                input_file=input_file.name,

                status=f"FAILED: {e}"

            )

    # ==========================================================
    # Final Summary
    # ==========================================================

    print("\n" + "=" * 70)
    print("NETWORK VALIDATION COMPLETE")
    print("=" * 70)

    print(f"Datasets Processed : {len(csv_files)}")
    print(f"Successful         : {successful}")
    print(f"Failed             : {failed}")

    print("=" * 70)


if __name__ == "__main__":
    main()