
import psycopg2
import pandas as pd

def get_well_data(basin, flowunit_of_interest, min_completion_year, main_url):
    """
    Retrieve well data from the specified basin and flow unit, filtered by completion year and well status.

    Parameters:
    - basin (str): The name of the basin to filter.
    - flowunit_of_interest (str): The flow unit of interest to filter wells.
    - min_completion_year (int): The minimum completion year to filter the wells.

    Returns:
    - pd.DataFrame: A Pandas DataFrame containing the filtered well data.
    """

    query = f"""
        SELECT
            API10 as "API10",
            API14 as "API14",
            tca_id as "tcaID",
            well_status as "wellStatus",
            operator_gold as "OperatorGold",
            completion_year as "CompletionYear",
            lateral_length_ft as "LateralLength_FT",
            proppant_lbs_per_ft as "Proppant_LBSPerFT",
            fluid_bbl_per_ft as "Fluid_BBLPerFT",
            ws.spacing_hz_same_zone_at_drill as "SpacingHzAnyZoneAtDrill",
            ws.bounding_any_zone_at_drill as "BoundingAnyZoneAtDrill"
            FROM
            public.well_one_line one
            INNER JOIN public.flow_unit fu 
            ON fu.fu_id = one.fu_id
            INNER JOIN public.basin b
            ON b.basin_id = fu.basin_id
            LEFT JOIN public.well_spacing ws
            ON one.well_id = ws.well_id
            LEFT JOIN public.well_spacing_scenario wss
            ON ws.wss_id = wss.wss_id and fu.fu_id=wss.fu_id
            WHERE
            one.longest_lateral_flag = 'true'
            AND fu.fu_Analog = '{flowunit_of_interest}'
            AND b.basin_name = '{basin}'
            AND one.well_status = 'PRODUCING'
            AND one.completion_year >= {min_completion_year}

        """

    
    with psycopg2.connect(main_url) as connection:
        prodTax = pd.read_sql_query(query, connection)

    return prodTax

