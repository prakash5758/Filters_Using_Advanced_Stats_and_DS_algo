# Analog Well Selection with Outlier Removal

This repository contains multiple Python files to assist in the selection of analog wells by removing outliers. The key focus of this project is to identify wells that match certain characteristics, perform preprocessing, apply statistical tests, and remove outliers using the Mahalanobis distance technique. The final filters are applied to the following features:
- `Proppant_LBSPerFT`
- `Fluid_BBLPerFT`
- `SpacingHzAnyZoneAtDrill`
- `CompletionYear`

## How it Works
The process starts by downloading well data from a PostgreSQL database, followed by preprocessing and filtering. A statistical test is applied to get a similar year filter. Outliers are then detected and removed using the Mahalanobis distance technique. The final result provides wells that meet the given criteria and are free from outliers based on the specified features.

## Required Parameters
To run the process, the following three parameters must be provided by the user:
- **Basin**: The basin of interest.
- **Flowunit_of_interest**: The specific flow unit you are analyzing.
- **TCA**: The Type Curve Area of interest.

These parameters are passed to the `prepare_data_and_calculate_metrics` function inside `main.py`.
