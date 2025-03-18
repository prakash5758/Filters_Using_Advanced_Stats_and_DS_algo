import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import r2_score
from mahalanobis_outlier_detection import detect_outliers_mahalanobis  
from statistical_test import find_similar_years_cutoff  
# from data_downloader import get_well_data
from data_downloader_postgress import get_well_data


dbutils.widgets.text("secret_scope_name", "wfdoqbiapidevqvc")
secret_scope = dbutils.widgets.get("secret_scope_name")
connection_string = dbutils.secrets.get(secret_scope, "qbi-db-connection-string").split("?")[0]

def calculate_final_percentile(r2):
    """
    Calculate the final percentile based on the R-squared value using linear interpolation.

    Parameters:
    - r2 (float): R-squared value.

    Returns:
    - float: Final percentile value adjusted based on R-squared.
    """
    if r2 >= 0.95:
        return 0.95
    elif r2 <= 0.80:
        return 0.80
    else:
        # Linear interpolation between (0.80, 0.80) and (0.95, 0.95)
        x1, y1 = 0.80, 0.80
        x2, y2 = 0.95, 0.95
        slope = (y2 - y1) / (x2 - x1)
        return y1 + slope * (r2 - x1)

def prepare_data_and_calculate_metrics(basin, flowunit_of_interest, excluded_tca_ids=None, connection_string=connection_string, min_completion_year=2016, feature='LateralLength_FT'):
    """
    Prepare data by filtering, converting types, and calculating metrics.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing well data.
    - feature (str): The column name of the feature to be used.
    - tca (int or None): TCA ID filter for specific analysis (default is None).

    Returns:
    - pd.DataFrame or None: The processed DataFrame with outlier classification or None if insufficient data.
    """
    # Filter out rows where 'BoundingAnyZoneAtDrill' is 'UNBOUND'

    df = get_well_data(basin, flowunit_of_interest, min_completion_year, connection_string)

    df = df[df.BoundingAnyZoneAtDrill != 'UNBOUND']
    
    # Filter by TCA if specified

    if excluded_tca_ids is not None:
        df = df[~df.tcaID.isin(excluded_tca_ids)]
    
    # Convert selected columns to numeric
    numerical_cols = ["CompletionYear", "LateralLength_FT", "Proppant_LBSPerFT", "Fluid_BBLPerFT", "SpacingHzAnyZoneAtDrill"]
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with missing values in the specified columns
    df_nona = df[['API10', "CompletionYear", "LateralLength_FT", "Proppant_LBSPerFT", "Fluid_BBLPerFT", "SpacingHzAnyZoneAtDrill"]].dropna()

    # Determine the minimum year cutoff using the statistical test
    threshold = df_nona.groupby('CompletionYear', as_index=False)['API10'].count()['API10'].quantile(0.25)

    if df_nona[df_nona.CompletionYear == df_nona.CompletionYear.max()].shape[0] >= threshold:
        start_year = df_nona.CompletionYear.max()

    else:
        start_year = df_nona.CompletionYear.max()-1
      
    min_year_cutoff = find_similar_years_cutoff(df_nona, feature, start_year, threshold)

    # Filter data based on the year range
    df_nona = df_nona[(df_nona["CompletionYear"] >= min_year_cutoff) & (df_nona["CompletionYear"] <= start_year)]

    # Proceed if sufficient data is available
    if len(df_nona) >= 40:
        # Define lateral length boundaries
        min_ll = 3500
        max_ll = max(20000, df_nona["LateralLength_FT"].describe(percentiles=[0.975])["97.5%"])
     
        # Filter data within lateral length boundaries
        df_nona = df_nona[(df_nona["LateralLength_FT"] >= min_ll) & (df_nona["LateralLength_FT"] <= max_ll)]
        
        # Calculate Mahalanobis distances and identify outliers
        outliers, md = detect_outliers_mahalanobis(df_nona[['Proppant_LBSPerFT', 'Fluid_BBLPerFT', 'SpacingHzAnyZoneAtDrill']], alpha=0.1)
        df_nona['md'] = md
        
        # Determine bin count for histogram
        bins = min(30, len(df_nona) // 6)
        bins = max(10, bins)
        
        # Fit normal distribution to log-transformed Mahalanobis distances
        log_md = np.log(md)
        hist, bin_edges = np.histogram(log_md, bins=bins, density=True)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        mu, std = norm.fit(log_md)

        # Calculate metrics for model evaluation
        pdf = norm.pdf(bin_centers, mu, std)
        sse = np.sum((hist - pdf) ** 2)
        r2 = r2_score(hist, pdf)
        log_likelihood = np.sum(norm.logpdf(hist, mu, std))
        
        # Determine the final percentile and threshold for classifying outliers
        final_percentile = calculate_final_percentile(r2)
        threshold_md = norm.ppf(final_percentile, mu, std)
        
        # Classify outliers based on threshold
        df_nona = df_nona.loc[np.log(df_nona['md']) < threshold_md]
        
        if df_nona is not None and not df_nona.empty:
            columns_of_interest = ['Proppant_LBSPerFT', 'Fluid_BBLPerFT', 'SpacingHzAnyZoneAtDrill', 'CompletionYear']
            min_max_values = {col: {'min': df_nona[col].min(), 'max': df_nona[col].max()} for col in columns_of_interest}
            # min_max_json = json.dumps(min_max_values, indent=4)
            return min_max_values
        else:
            return "Not enough data available to calculate metrics"
    else:
        return "Not enough data available to calculate metrics"
