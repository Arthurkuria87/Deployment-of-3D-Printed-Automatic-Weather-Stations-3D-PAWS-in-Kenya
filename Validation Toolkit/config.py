"""
==========================================================================
3DPAWS Validation Toolkit
Configuration File
==========================================================================

Central configuration for:

• Project directories
• Time settings
• Sensor definitions
• Sensor aliases
• Quality control rules
• Rainfall settings

The toolkit uses logical sensor names throughout.
Actual dataset column names are resolved dynamically using SENSOR_ALIASES.
==========================================================================
"""

from pathlib import Path

# ==========================================================================
# PROJECT PATHS
# ==========================================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "cleaned"
DAILY_DATA_DIR = DATA_DIR / "daily"
QC_DATA_DIR = DATA_DIR / "qc"
REPORT_DIR = DATA_DIR / "reports"

# --------------------------------------------------------------------------
# OUTPUTS
# --------------------------------------------------------------------------

OUTPUT_DIR = BASE_DIR / "output"      # or "outputs" if that's your folder

OUTPUT_TABLES = OUTPUT_DIR / "tables"
OUTPUT_FIGURES = OUTPUT_DIR / "figures"

# --------------------------------------------------------------------------
# STATION DATASETS
# --------------------------------------------------------------------------

STATIONS_OUTPUT_DIR = OUTPUT_DIR / "Stations"

# ==========================================================================
# TIME SETTINGS
# ==========================================================================

TIME_COLUMN = "measurement_time"

# ==========================================================================
# LOGICAL SENSOR DEFINITIONS
#
# These are the canonical sensor names used throughout the toolkit.
# Every validation routine should reference these names rather than
# physical dataset column names.
# ==========================================================================

SENSORS = [

    # Temperature
    "temperature",
    "temperature_secondary",

    # Humidity
    "humidity",

    # Pressure
    "pressure",

    # Rainfall
    "rain_increment_1",
    "rain_increment_2",
    "rain_total_1",
    "rain_total_2",
    "rain_previous_1",
    "rain_previous_2",

    # Derived Variables
    "wet_bulb",
    "heat_index",
    "wbgt",
]

# ==========================================================================
# SENSOR ALIASES
#
# Maps logical sensor names to possible dataset column names.
#
# Example:
#
# temperature
#     ↓
# mt1 / temperature / temp / air_temperature
#
# The first matching column found in a dataset is used.
# ==========================================================================

SENSOR_ALIASES = {

    # ------------------------------------------------------
    # Temperature
    # ------------------------------------------------------

    "temperature": [
        "mt1",
        "temperature",
        "temp",
        "air_temperature",
    ],

    "temperature_secondary": [
        "st1",
        "st",
        "secondary_temperature",
    ],

    # ------------------------------------------------------
    # Relative Humidity
    # ------------------------------------------------------

    "humidity": [
        "sh1",
        "humidity",
        "rh",
        "relative_humidity",
    ],

    # ------------------------------------------------------
    # Atmospheric Pressure
    # ------------------------------------------------------

    "pressure": [
        "bp1",
        "bp",
        "pressure",
        "air_pressure",
    ],

    # ------------------------------------------------------
    # Rainfall
    # ------------------------------------------------------

    "rain_increment_1": [
        "rg1",
        "rg",
    ],

    "rain_increment_2": [
        "rg2",
    ],

    "rain_total_1": [
        "rgt1",
        "rgt",
    ],

    "rain_total_2": [
        "rgt2",
    ],

    "rain_previous_1": [
        "rgp1",
        "rgp",
    ],

    "rain_previous_2": [
        "rgp2",
    ],

    # ------------------------------------------------------
    # Derived Variables
    # ------------------------------------------------------

    "wet_bulb": [
        "wbt",
        "wet_bulb",
    ],

    "heat_index": [
        "hi",
        "heat_index",
    ],

    "wbgt": [
        "wbgt",
    ],
}

# ==========================================================================
# QUALITY CONTROL RULES
#
# Rules are referenced using the logical sensor names.
#
# Any sensor without a QC rule should simply be skipped by the QC engine.
# ==========================================================================

QC_RULES = {

    # ------------------------------------------------------
    # Temperature
    # ------------------------------------------------------

    "temperature": {
        "range": (-40.0, 60.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },

    "temperature_secondary": {
        "range": (-40.0, 60.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },

    # ------------------------------------------------------
    # Relative Humidity
    # ------------------------------------------------------

    "humidity": {
        "range": (0.0, 100.0),
        "constant": 95,
        "spike": 15.0,
        "persistence": 8,
    },

    # ------------------------------------------------------
    # Atmospheric Pressure
    # ------------------------------------------------------

    "pressure": {
        "range": (800.0, 1100.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },

    # ------------------------------------------------------
    # Rainfall Increment
    # ------------------------------------------------------

    "rain_increment_1": {
        "range": (0.0, None),
        "constant": 99,
        "spike": 25.0,
        "persistence": 96,
    },

    "rain_increment_2": {
        "range": (0.0, None),
        "constant": 99,
        "spike": 25.0,
        "persistence": 96,
    },

    # ------------------------------------------------------
    # Derived Variables
    # ------------------------------------------------------

    "wet_bulb": {
        "range": (-40.0, 60.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },

    "heat_index": {
        "range": (-40.0, 70.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },

    "wbgt": {
        "range": (-20.0, 60.0),
        "constant": 95,
        "spike": 5.0,
        "persistence": 8,
    },
}

# ==========================================================================
# RAINFALL SETTINGS
# ==========================================================================

RAINFALL_RESET_HOUR = 6
RAINFALL_RESET_MINUTE = 0

# Maximum acceptable difference (mm) between rain gauges

RAINFALL_TOLERANCE = 0.01

# ==========================================================================
# DATASET DISCOVERY
# ==========================================================================
#
# DatasetManager discovers datasets dynamically.
# Dataset identification is based on workbook contents rather than
# filenames or folder names.
# ==========================================================================

# Supported workbook extensions

SUPPORTED_DATASET_EXTENSIONS = {

    ".xlsx",
    ".xls"

}

# Supported dataset sources

SUPPORTED_DATA_SOURCES = {

    "3DPAWS",
    "KMD"

}

# Dataset types recognised by the toolkit

SUPPORTED_DATASET_TYPES = {

    "Daily Summary",
    "KMD Standardized",
    "Merged Dataset"

}

# Dataset types that should never be processed

IGNORED_DATASET_TYPES = {

    "Validation Report",
    "Comparison Report",
    "Statistics",
    "Plots",
    "Reports",
    "Logs"

}

# ==========================================================================
# DATASET SIGNATURES
# ==========================================================================
#
# Used by DatasetInfoReader to identify workbook types.
# A workbook matches when all required columns are present.
# ==========================================================================

DATASET_SIGNATURES = {

    "Daily Summary": {

        "required_columns": {

            "Date",
            "Tmax",
            "Tmin",
            "Tmean",
            "RH_Max",
            "RH_Min",
            "RH_Mean",
            "Pressure_Max",
            "Pressure_Min",
            "Pressure_Mean",
            "Rain_RG1",
            "Rain_RG2"

        }

    },

    "KMD Standardized": {

        "required_columns": {

            "Station_Name",
            "Date",
            "Tmax",
            "Tmin",
            "Rain"

        }

    }

}
# ==========================================================================
# DATASET MATCHING
# ==========================================================================
#
# Rules used when pairing 3DPAWS datasets with KMD datasets.
# ==========================================================================

# Match station names

MATCH_ON_STATION = True

# Ignore upper/lower case when comparing station names

IGNORE_CASE_IN_STATION_NAMES = True

# Trim leading/trailing spaces before matching

TRIM_STATION_NAMES = True

# Match overlapping observation periods

MATCH_ON_DATE_OVERLAP = True

# Minimum number of overlapping days required

MINIMUM_OVERLAP_DAYS = 5

# Allow partial overlap

ALLOW_PARTIAL_MATCHES = True

# ==========================================================================
# DUPLICATE DATASETS
# ==========================================================================
#
# Controls duplicate handling during dataset discovery.
# ==========================================================================

ALLOW_DUPLICATE_DATASETS = False

KEEP_NEWEST_DUPLICATE = True

EXPORT_DUPLICATE_REPORT = True

# ==========================================================================
# DATASET INVENTORY
# ==========================================================================
#
# DatasetManager automatically builds an inventory before processing.
# ==========================================================================

BUILD_DATASET_INVENTORY = True

EXPORT_DATASET_INVENTORY = True

EXPORT_PROCESSING_QUEUE = True

EXPORT_REJECTED_DATASETS = True

# ==========================================================================
# OUTPUT PRODUCTS
# ==========================================================================
#
# Products generated during validation.
# These names are also used as output folder names.
# ==========================================================================

OUTPUT_PRODUCTS = {

    "comparison": "Comparison",

    "statistics": "Statistics",

    "plots": "Plots",

    "reports": "Reports",

    "logs": "Logs"

}

# ==========================================================================
# COMPARISON SETTINGS
# ==========================================================================
#
# Controls creation of merged datasets.
# ==========================================================================

EXPORT_MERGED_DATASET = True

EXPORT_COMPARISON_SUMMARY = True

EXPORT_DAILY_DIFFERENCES = True

EXPORT_MATCH_INFORMATION = True

# ==========================================================================
# VALIDATION STATISTICS
# ==========================================================================
#
# Statistical metrics computed when comparing
# 3DPAWS observations against KMD observations.
# ==========================================================================

VALIDATION_METRICS = [

    "Bias",

    "Mean Absolute Error",

    "Root Mean Square Error",

    "Correlation",

    "Coefficient of Determination",

    "Nash Sutcliffe Efficiency"

]

# ==========================================================================
# PLOTTING
# ==========================================================================
#
# Figures generated automatically after comparison.
# ==========================================================================

PLOT_TYPES = [

    "Time Series",

    "Scatter",

    "Residual",

    "Histogram",

    "Box Plot"

]

EXPORT_PLOTS = True

PLOT_FORMAT = "png"

PLOT_DPI = 300

# ==========================================================================
# REPORTING
# ==========================================================================
#
# Controls automatic report generation.
# ==========================================================================

GENERATE_REPORT = True

REPORT_FORMAT = "xlsx"

REPORT_SECTIONS = [

    "Dataset Information",

    "Validation Summary",

    "Comparison Summary",

    "Statistical Metrics",

    "Rainfall Analysis",

    "Plots",

    "Conclusions"

]

# ==========================================================================
# LOGGING
# ==========================================================================
#
# Processing log configuration.
# ==========================================================================

ENABLE_PROCESSING_LOG = True

ENABLE_ERROR_LOG = True

ENABLE_DATASET_LOG = True

LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================================
# FUTURE DATA SOURCES
# ==========================================================================
#
# Reserved for future expansion.
# Additional sources can be added without modifying
# DatasetManager or comparison modules.
# ==========================================================================

FUTURE_DATA_SOURCES = [

    "AWS",

    "NOAA",

    "WMO",

    "SYNOP",

    "NetCDF",

    "CSV"

]
