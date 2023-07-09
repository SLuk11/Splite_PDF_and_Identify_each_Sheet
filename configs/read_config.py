import json
import os


def read_config():

    global setting, sql_db, sql_db_conn_str

    #   Read JSON config file
    json_file_fullpath = os.path.join("./configs","config.json")
    with open(json_file_fullpath, "r") as f:
        config = json.load(f)

    ## Call config and excel's sheets detail & Excel's file directory
    setting = config['shipping_pdf_cf']
    sql_db = config['Shipping_SqlDb']
    sql_db_conn_str = '{}://{}:{}@{}/{}?driver={}'.format(sql_db['dialect']
                                                          , sql_db['sql_username']
                                                          , sql_db['sql_password']
                                                          , sql_db['sql_host']
                                                          , sql_db['sql_database_name']
                                                          , sql_db['sql_driver'])

__all__ = ['read_config']
