SERVER_NAME = r"JULY-01\SQLLEARNING" 
DATABASE_NAME = "demo"
DB_CONNECTION_STRING = f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
import urllib.parse
ODBC_PARAMS = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    "Trusted_Connection=yes;"
)
ODBC_CONNECTION_STRING = f"mssql+pyodbc:///?odbc_connect={ODBC_PARAMS}"
