import streamlit as st
import os
import pandas as pd
from typing import Generator
from langchain_core.messages import HumanMessage, AIMessage


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

from src.sql_utils import excel_to_sqlite, add_table_to_sqlite_db_from_df, delete_db
from src.agent import graph
from src.db import db


def stream_values(response) -> Generator[str, None, None]:
    for msg, metadata in response:
        if (
            msg.content
            and not isinstance(msg, HumanMessage)
            and metadata["langgraph_node"] == "give_final_answer"
        ):
            # print(msg.content, end="|", flush=True)
            # print(msg.content, end="", flush=True)
            yield msg.content


def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    st.subheader(
        "Interact with SQL DataBase using Natural Language",
        divider="gray",
        anchor=False,
    )

    # Create layout
    col1, col2 = st.columns([1.5, 2])

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "use_sample" not in st.session_state:
        st.session_state["use_sample"] = False
    if "excel_file" not in st.session_state:
        st.session_state["excel_file"] = []
    if "sql_db" not in st.session_state:
        st.session_state["sql_db"] = []

    file_upload = col1.file_uploader(
        "Upload EXCEL file ↓",
        type=["csv"],
        accept_multiple_files=True,
        key="excel_uploader",
    )
    st.session_state["excel_file"] = file_upload

    # Delete collection button
    delete_collection = col1.button(
        "⚠️ Delete collection", type="secondary", key="delete_button"
    )

    if st.session_state["excel_file"]:
        # if st.session_state["sql_db"] is None:
        with st.spinner("Processing uploaded EXCEL..."):

            # Button to show the selected sheets
            if col1.button("Create SQL DB"):
                if st.session_state["excel_file"]:
                    # Iterate over each uploaded file
                    i = 0
                    for file in st.session_state["excel_file"]:
                        print()
                        print(f"processing file {i+1}:>>>>>>")
                        i += 1
                        # Display PDF pages
                        with col1:
                            with st.container(height=410, border=True):
                                st.write(f"Showing sheets for {file.name}:")

                                # Try reading the sheets
                                try:
                                    df = pd.read_csv(file)
                                    # st.write(f"Sheet: {sheet}")
                                    st.write(df)
                                    print(f"Creating SQL DB......")
                                    db_path = os.getenv("SQL_DB_PATH_VAR")

                                    add_table_to_sqlite_db_from_df(
                                        df=df,
                                        db_path=db_path,
                                        table_name=os.path.splitext(file.name)[0],
                                    )
                                    st.session_state["sql_db"].append(db_path)

                                except Exception as e:
                                    st.error(f"Error reading {file.name}: {str(e)}")
                else:
                    st.warning("Please upload files first...")

    if delete_collection:
        for sql_db in st.session_state["sql_db"]:
            delete_db(sql_db)
        if os.getenv("SQL_DB_PATH_VAR"):
            delete_db(os.getenv("SQL_DB_PATH_VAR"))
    with col2:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = db.run(query)
        print(f"db status: {tables}")
        message_container = st.container(height=500, border=True)
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with message_container.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter your input here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with message_container.chat_message("user"):
                st.markdown(prompt)

            try:
                if tables != "" and db._engine:
                    response = graph.stream(
                        input={"messages": st.session_state.messages},
                        stream_mode="messages",
                    )
                    with message_container.chat_message("ai"):
                        full_response = st.write_stream(stream_values(response))
                        # full_response = final_answer
                        # st.markdown(response)
                else:
                    full_response = "Please upload some file first and then click 'Create SQL DB Button'..."
                    with message_container.chat_message("ai"):
                        st.write(full_response)

            except Exception as e:
                st.error(e, icon="🚨")

            # Append the full response to session_state.messages
            if isinstance(full_response, str):
                st.session_state.messages.append(
                    {"role": "ai", "content": full_response}
                )
            else:
                # Handle the case where full_response is not a string
                combined_response = "\n".join(str(item) for item in full_response)
                st.session_state.messages.append(
                    {"role": "ai", "content": combined_response}
                )


if __name__ == "__main__":
    main()
