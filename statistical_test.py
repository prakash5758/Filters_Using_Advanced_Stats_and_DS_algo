from scipy.stats import ttest_ind

def find_similar_years_cutoff(df, feature, start_year, threshold, min_year=2016):
    """
    Find the earliest year with similar feature distribution to the start year using T-tests 
    and ensure a minimum data threshold.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data.
    - feature (str): The column name of the feature to compare between years.
    - start_year (int): The starting year for comparison.
    - threshold (int): Minimum number of data points required for the similar years 
    - min_year (int): The earliest year to consider for comparison (default is 2016).

    Returns:
    - int: The earliest year found with similar feature distribution to the start year.
    """
    
    # Initialize the list with the starting year
    similar_years = [start_year]
    
    # Start with the year just before the start year
    current_year = start_year - 1
    
    # Loop to find years with similar distribution using T-tests
    while current_year >= min_year:
      
        # Extract data for the current and start years, dropping missing values
        data_current_year = df[df['CompletionYear'] == current_year][feature].dropna()
        data_start_year = df[df['CompletionYear'] == start_year][feature].dropna()

        # Proceed only if both years have data available
        if len(data_current_year) > 0 and len(data_start_year) > 0:
            # Perform a T-test to compare the distributions
            t_statistic, p_value = ttest_ind(data_start_year, data_current_year)
            
            # If p-value indicates no significant difference, add the current year to the list

            if p_value > 0.01:
                similar_years.append(current_year)
                current_year -= 1
            else:
                # Stop if a significant difference is found
                break
        else:
            # Stop if there is no data for one of the years
            break
    
    # Filter the DataFrame to include only the years in the similar_years list
    remaining_data = df[df['CompletionYear'].isin(similar_years)]
    
    # Ensure the count of data points meets the threshold
    while len(remaining_data) < threshold and current_year >= min_year:
        similar_years.append(current_year)
        current_year -= 1
        remaining_data = df[df['CompletionYear'].isin(similar_years)]
    
    # Return the earliest year found
    return min(similar_years)


