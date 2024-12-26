from pydantic import BaseModel, Field
from typing import List


class SubmitFinalAnswer(BaseModel):
    """Provide the user with the final answer obtained from the query results."""

    final_answer: str = Field(
        ..., description="Response to the user's query with the final answer."
    )


class Tables(BaseModel):
    """A table in a database."""

    name: List[str] = Field(..., description="Names of the tables in database.")


class Table(BaseModel):
    """A table in a database."""

    name: str = Field(..., description="Name of the table in database.")
