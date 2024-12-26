import pandas as pd
import sqlite3
import os
import streamlit as st
import re

from langchain_community.utilities import SQLDatabase
from src.db import db


def get_db(uri):
    db = SQLDatabase.from_uri(uri)
    return db


def standardize_column_names(columns):
    """
    Standardizes column names to lowercase and replaces non-alphanumeric characters with underscores.

    Parameters:
        columns (list): List of column names to standardize.

    Returns:
        list: List of standardized column names.
    """
    standardized = []
    for col in columns:
        col = re.sub(
            r"[^a-zA-Z0-9]", "_", col
        ).lower()  # Replace non-alphanumeric characters with underscores and lowercase
        standardized.append(col)
    return standardized


def add_table_to_sqlite_db(file_path, sheet_name, db_path, table_name):
    """
    Adds a new table to an existing SQLite database from an Excel or CSV file.

    Parameters:
        file_path (str): Path to the file (Excel or CSV).
        sheet_name (str or None): Name of the sheet (for Excel files only). Pass None for CSV files.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the new table to create in the database.

    Returns:
        None
    """
    try:
        # Step 1: Load data from the file
        print(f"Loading data from file: {file_path}")
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            df = (
                pd.read_excel(file_path, sheet_name=sheet_name)
                if sheet_name
                else pd.read_excel(file_path)
            )
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            raise ValueError(
                "Unsupported file format. Please provide an Excel or CSV file."
            )

        # Step 2: Standardize column names
        print("Standardizing column names...")
        df.columns = standardize_column_names(df.columns)
        print(f"Standardized column names: {df.columns.tolist()}")

        # Step 3: Connect to the SQLite database
        print(f"Connecting to SQLite database: {db_path}")
        conn = sqlite3.connect(db_path)

        # Step 4: Write the DataFrame to a new table in the database
        print(f"Adding new table: {table_name}")
        df.to_sql(
            table_name, conn, if_exists="fail", index=False
        )  # Fail if the table already exists
        print(f"Table '{table_name}' successfully added to the database.")

        # Optional: Verify data insertion
        query = f"SELECT * FROM {table_name} LIMIT 5;"
        print(f"Sample data from {table_name}:")
        print(pd.read_sql(query, conn))

    except sqlite3.OperationalError as e:
        if "table" in str(e) and "already exists" in str(e):
            print(f"Error: Table '{table_name}' already exists in the database.")
        else:
            print(f"An SQLite error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Step 5: Close the database connection
        if "conn" in locals():
            conn.close()
            print("Database connection closed.")


def add_table_to_sqlite_db_from_df(df, db_path, table_name):
    """
    Adds a new table to an existing SQLite database from an Excel or CSV file.

    Parameters:
        df (pd.DataFrame): The DataFrame to add.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the new table to create in the database.

    Returns:
        None
    """
    try:

        # Step 1: Standardize column names and table name
        print("Standardizing column names...")
        df.columns = standardize_column_names(df.columns)
        print("Standardizing table names...")
        table_name = standardize_column_names([table_name])[0]
        print(f"Standardized column names: {df.columns.tolist()}")

        # Step 2: Connect to the SQLite database
        print(f"Connecting to SQLite database: {db_path}")
        conn = sqlite3.connect(db_path)

        # Step 3: Write the DataFrame to a new table in the database
        print(f"Adding new table: {table_name}")
        df.to_sql(
            table_name, conn, if_exists="fail", index=False
        )  # Fail if the table already exists
        print(f"Table '{table_name}' successfully added to the database.")

        # Optional: Verify data insertion
        query = f"SELECT * FROM {table_name} LIMIT 5;"
        print(f"Sample data from {table_name}:")
        print(pd.read_sql(query, conn))

    except sqlite3.OperationalError as e:
        if "table" in str(e) and "already exists" in str(e):
            print(f"Error: Table '{table_name}' already exists in the database.")
        else:
            print(f"An SQLite error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Step 4: Close the database connection
        if "conn" in locals():
            conn.close()
            print("Database connection closed.")


def excel_to_sqlite(excel_file, sheet_name, db_path, table_name):
    """
    Converts an Excel sheet to a table in an SQLite database.

    Parameters:
        excel_file (str): Path to the Excel file.
        sheet_name (str): Name of the Excel sheet to read.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to create/replace in the database.

    Returns:
        None
    """
    try:
        # Step 1: Read the Excel sheet
        print(f"Reading Excel file: {excel_file}, Sheet: {sheet_name}")
        # df = pd.read_excel(excel_file, sheet_name=sheet_name)

        if excel_file.endswith(".xlsx") or excel_file.endswith(".xls"):
            if sheet_name:
                df = pd.read_excel(
                    excel_file, sheet_name=sheet_name
                )  # Read specific sheet from Excel
            else:
                df = pd.read_excel(
                    excel_file
                )  # Read the first sheet if no sheet name is provided
        elif excel_file.endswith(".csv"):
            df = pd.read_csv(excel_file)  # Read CSV file (no sheet_name needed)
        else:
            raise ValueError(
                "Unsupported file format. Please provide an Excel or CSV file."
            )

        # Step 2: Connect to the SQLite database
        print(f"Connecting to SQLite database: {db_path}")
        conn = sqlite3.connect(db_path)

        # Step 3: Write the DataFrame to a database table
        print(f"Writing data to table: {table_name}")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Data successfully written to table: {table_name}")

        # Optional: Verify data insertion
        query = f"SELECT * FROM {table_name} LIMIT 5;"
        print(f"Sample data from {table_name}:")
        print(pd.read_sql(query, conn))

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Step 4: Close the connection
        if "conn" in locals():
            conn.close()
            print("Database connection closed.")


# @st.cache_data
def df_to_sqlite(df, db_name, table_name):
    """
    Converts a pandas DataFrame to a SQLite database table.

    Parameters:
        df (pd.DataFrame): The DataFrame to convert.
        db_name (str): Name of the SQLite database file (e.g., "my_database.db").
        table_name (str): Name of the table to create in the database.

    Returns:
        None
    """
    try:
        # Connect to SQLite database (creates the database if it doesn't exist)
        conn = sqlite3.connect(db_name)

        # Write the DataFrame to the SQLite table
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"DataFrame successfully written to {table_name} table in {db_name}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        conn.close()


def delete_db(db_name):
    """
    Deletes a SQLite database file.

    Parameters:
        db_name (str): Name of the SQLite database file to delete (e.g., "my_database.db").

    Returns:
        None
    """
    try:
        # Check if the file exists
        if os.path.exists(db_name):
            print(f"connecting to db....")
            # Ensure the connection is closed
            db._engine.dispose()

            try:
                conn = sqlite3.connect(db_name)
                # Perform operations
            finally:
                conn.close()
            os.remove(db_name)
            print(f"Database '{db_name}' has been deleted successfully.")
        else:
            print(f"Database '{db_name}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")
