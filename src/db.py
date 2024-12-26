from langchain_community.utilities import SQLDatabase

# db = get_db(uri=os.getenv("SQL_SAMPLE_DB_URI"))
db = SQLDatabase.from_uri(
    "sqlite:///E:\python projects\sql-agent-langgraph-streamlit\sql_db\sample_sqlite3.db"
)

# Check if the db object is valid and connected
if db is not None and db._engine:
    print("Database connection exists.")
else:
    print("Database connection does not exist.")

# Query to check if any tables exist
query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = db.run(query)

# If no tables exist, the database is empty
if not tables:
    print("Database is empty (no tables found).")
