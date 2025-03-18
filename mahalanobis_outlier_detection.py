import numpy as np
import scipy as sp
from scipy.stats import chi2
from sklearn.covariance import MinCovDet

def detect_outliers_mahalanobis(df, alpha=0.001):
    """
    Detect outliers using the Mahalanobis Distance method with robust covariance estimation.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing numerical data.
    - alpha (float): Significance level for the chi-squared distribution (default is 0.001).

    Returns:
    - outlier (list): Indices of the detected outliers in the DataFrame.
    - md (np.ndarray): Mahalanobis distances of each observation in the DataFrame.
    """
    # Initialize random state for reproducibility
    rng = np.random.RandomState(0)
    
    # Calculate the real covariance of the DataFrame
    real_cov = np.cov(df.values.T)
    
    # Generate multivariate normal data with the mean and real covariance of the DataFrame
    X = rng.multivariate_normal(mean=np.mean(df, axis=0), cov=real_cov, size=506)
    
    # Fit Minimum Covariance Determinant (MCD) for robust covariance estimation
    cov = MinCovDet(random_state=0).fit(X)
    mcd = cov.covariance_  # Robust covariance matrix
    robust_mean = cov.location_  # Robust mean of the data
    inv_covmat = sp.linalg.inv(mcd)  # Inverse of the robust covariance matrix
    
    # Calculate the Mahalanobis distance for each observation
    x_minus_mu = df - robust_mean  # Difference from the robust mean
    left_term = np.dot(x_minus_mu, inv_covmat)  # Dot product with inverse covariance matrix
    mahal = np.dot(left_term, x_minus_mu.T)  # Final Mahalanobis distance calculation
    md = np.sqrt(mahal.diagonal())  # Extract diagonal elements and take square root
    
    # Identify outliers based on a critical value from the chi-squared distribution
    outlier = []
    C = np.sqrt(chi2.ppf((1 - alpha), df=df.shape[1]))  # Critical value, degrees of freedom = number of features
    
    # Flag observations as outliers if their Mahalanobis distance exceeds the critical value
    for index, value in enumerate(md):
        if value > C:
            outlier.append(index)
    
    return outlier, md
