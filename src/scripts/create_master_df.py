import pandas as pd
from flask import current_app


def create_user_master_df(conn, table_name, query):
    """
    Creates a pandas dataframe placeholder with key meta-data to fuzzy-match
    the users from different datasets.

    Pseudo-code:
        Create a blank pandas dataframe (e.g. pd.DataFrame) with columns for
        Name (last, first), address, zip code, phone number, email, etc.

        Include "ID" fields for each of the datasets that will be merged.

        Populate/Initialize the dataframe with data from one of the datasets
        (e.g. Salesforce)
    """

    # pull the dataframe from SQL database, call cleaning function,
    # and add empty columns for the datasets that will be merged
    conn.execute(f'DROP TABLE IF EXISTS {table_name}')
    conn.execute('create table ' + table_name + ' ' + query)
    df = pd.read_sql('select * from ' + table_name, conn)

    return df


def main(conn):
    # Create a simple table with the following values:
    # ------------> master_db (primary key), petpoint_id, volgistics_id, salesforce_id, email_address
    # petpoint[[outcome_person_id]]
    # volgistics[[number]]
    # salesforcecontacts[[account_id]]

    # Create a new master_df table
    current_app.logger.info('Start Creating master_df')
    # master_df = create_user_master_df(
    # conn, 'master_df',
    # '(master_id INT PRIMARY KEY NOT NULL, petpoint_id text, volgistics_id text, salesforce_id text, email_address text )'
    # )

    # Merge Petpoint data to the master_df
    #petpoint = pd.read_sql('select * from petpoint', conn)
    #master_df = petpoint[['outcome_person_id', 'out_email']].rename(
    #    columns={'outcome_person_id': 'petpoint_id', 'out_email': 'email_address'})

    # Merge Salesforce data to the master_df
    salesforcecontacts = pd.read_sql('select * from salesforcecontacts', conn)
    master_df = salesforcecontacts[['account_id', 'email']].rename(
        columns={'account_id': 'salesforce_id', 'email': 'email_address'})
    current_app.logger.info('  -Successfully created salesforcecontact (Primary key) in master_df')

    # Merge Volgistics data into the master dataframe
    volgistics = pd.read_sql('select * from volgistics', conn)
    master_df = master_df.merge(
        volgistics[['number', 'email']].rename(columns={'number': 'volgistics_id', 'email': 'email_address'}),
        how='outer')
    current_app.logger.info('  -Successfully created volgistics row in master_df')

    master_df.to_sql('master_df', conn, if_exists='append', index_label='master_id')