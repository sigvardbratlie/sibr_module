from google.oauth2 import service_account
import bigframes.pandas as bf
from google.cloud import bigquery
import pandas_gbq as pbq
import numpy as np



class BigQuery:
    def __init__(self,CREDENTIALS_PATH,logger):
        self._credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        self._bq_client = bigquery.Client(credentials=self._credentials, project=self._credentials.project_id)
        self._project_id = self._credentials.project_id
        self._logger = logger
        bf.reset_session()
        bf.options.bigquery.credentials = self._credentials
        bf.options.bigquery.project = self._project_id
        bf.options.bigquery.location = 'EU'
    def to_bq(self, df, table_name, dataset_name, if_exists='append'):
        dataset_id = f'{self._project_id}.{dataset_name}'
        table_id = f"{dataset_id}.{table_name}"
        # Check if table exists
        try:
            self._bq_client.get_table(table_id)
            table_exists = True
        except Exception:
            table_exists = False

        if if_exists == 'append':
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND" if table_exists else "WRITE_TRUNCATE",
                autodetect=True,
            )
        elif if_exists == 'replace':
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_TRUNCATE",
                autodetect=True,
            )
        else:
            raise ValueError(f"Invalid if_exists value: {if_exists}")

        job = self._bq_client.load_table_from_dataframe(
            df, table_id, job_config=job_config
        )
        job.result()
        self._logger.info(f"{len(df)} rader lagret i {table_id}")
    def read_bq(self, query,read_type = 'bigframes'):
        '''
        Leser en BigQuery-spørring og returnerer en DataFrame.
        :param query:
        :param read_type: choose between 'bigframes', 'bq_client' and 'pandas_gbq'
        :return:
        '''
        if read_type == 'bigframes':
            df = bf.read_gbq(query).to_pandas()
        elif read_type == 'bq_client':
            df = self._bq_client.query(query).to_arrow().to_pandas()
        elif read_type == 'pandas_gbq':
            df = pbq.read_gbq(query,credentials=self._credentials)
        else:
            raise ValueError(f"Invalid read_type: {read_type}. Choose between 'bigframes', 'bq_client' and 'pandas_gbq'")
        df.replace(['nan','None','','null','NA','np.nan','<NA>','NaN','NAType','np.nan'],np.nan,inplace=True)
        self._logger.info(f"{len(df)} rader lest fra BigQuery")
        return df
    def exe_query(self, query):
        '''
        Execute a BigQuery query
        :param query:
        :return:
        '''
        job = self._bq_client.query(query)
        job.result()
        self._logger.info(f"Query executed: {query}")

class CSVoperator:
    def __init__(self,logger):
        self._logger = logger
