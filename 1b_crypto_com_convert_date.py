import pandas as pd
import numpy as np
import os

def main(ready_for_ingest_filepath, reworked_df):
    
    # Define filepath to read and filepath to export

    cryptocom_2023_ready_for_ingest = pd.read_csv(ready_for_ingest_filepath, sep=',')

    # Convert date column
    cryptocom_2023_ready_for_ingest['Date'] = pd.to_datetime(cryptocom_2023_ready_for_ingest['Date'], format='%m/%d/%Y %H:%M:%S')

    # export
    cryptocom_2023_ready_for_ingest.to_csv(reworked_df, index=False)


ready_for_ingest_filepath = 'Data/1_ready_for_ingest/cryptocom_2023_ready_for_ingest.csv'
reworked_df = 'Data/1_ready_for_ingest/cryptocom_2023_ready_for_ingest_date_reworked.csv'

main(ready_for_ingest_filepath, reworked_df)