import pandas as pd

from modules.statistics_utils import (
    classify_observations,
    quality_summary,
    prepare_valid_series,
)


def main():

    print("\n")
    print("=" * 80)
    print("TEST STATISTICS UTILS")
    print("=" * 80)

    # ------------------------------------------------------
    # Pressure
    # ------------------------------------------------------

    pressure = pd.Series([
        823.4,
        824.1,
        0,
        822.8,
        0,
        825.0,
    ])

    print("\nPRESSURE")
    print("-" * 80)

    print(
        classify_observations(
            pressure,
            "pressure"
        ).to_list()
    )

    print(
        quality_summary(
            pressure,
            "pressure"
        )
    )

    print(
        "\nClean pressure:"
    )

    print(
        prepare_valid_series(
            pressure,
            "pressure"
        ).to_list()
    )

    # ------------------------------------------------------
    # Rainfall
    # ------------------------------------------------------

    rainfall = pd.Series([
        0,
        0.2,
        5.4,
        0,
        10.1,
    ])

    print("\nRAINFALL")
    print("-" * 80)

    print(
        classify_observations(
            rainfall,
            "rainfall"
        ).to_list()
    )

    print(
        quality_summary(
            rainfall,
            "rainfall"
        )
    )

    print(
        "\nClean rainfall:"
    )

    print(
        prepare_valid_series(
            rainfall,
            "rainfall"
        ).to_list()
    )


if __name__ == "__main__":
    main()