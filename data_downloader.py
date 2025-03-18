def get_well_data(basin, flowunit_of_interest, min_completion_year):
    """
    Retrieve well data from the specified basin and flow unit, filtered by completion year and well status.

    Parameters:
    - basin (str): The name of the basin to filter.
    - flowunit_of_interest (str): The flow unit of interest to filter wells.
    - min_completion_year (int): The minimum completion year to filter the wells.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the filtered well data.
    """
    well_data = spark.sql(
        f"""
        SELECT
            API10, API14, tcaID, primary_phase, wellStatus, OperatorGold,
            CompletionYear, LateralLength_FT, Proppant_LBSPerFT,
            Fluid_BBLPerFT, SpacingHzAnyZoneAtDrill, BoundingAnyZoneAtDrill
        FROM
            hive_metastore.produced.analog_well_selection
        WHERE
            recentWell = 'true'
            AND flowUnit_Analog = '{flowunit_of_interest}'
            AND BasinQuantum = '{basin}'
            AND wellStatus = 'PRODUCING'
            AND CompletionYear >= {min_completion_year}
        """
    ).toPandas()
    
    return well_data

