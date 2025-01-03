import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')
ZYLINK_ODBC_USER = os.environ.get('ZYLINK_ODBC_USER')
ZYLINK_ODBC_PASS = os.environ.get('ZYLINK_ODBC_PASS')
ZYLINK_ODBC_HOST = os.environ.get('ZYLINK_ODBC_HOST')
ZYLINK_ODBC_DATABASE = os.environ.get('ZYLINK_ODBC_DATABASE')
CSV_PATH = os.environ.get('CSV_PATH')
ZYLINC_URL = os.environ["ZYLINC_URL"].strip()
ZYLINC_REALM = os.environ["ZYLINC_REALM"].strip()
ZYLINC_CLIENT = os.environ["ZYLINC_CLIENT"].strip()
ZYLINC_SECRET = os.environ["ZYLINC_SECRET"].strip()
QUEUES = ['IT_Digitalisering_1818']
KEYCLOAK_URL = os.environ["KEYCLOAK_URL"].strip()
KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"].strip()
KEYCLOAK_CLIENT_ID = os.environ["KEYCLOAK_CLIENT_ID"].strip()
