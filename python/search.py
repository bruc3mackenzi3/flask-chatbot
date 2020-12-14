import json
import sqlite3
from typing import Dict, List, Tuple

import config

class Search:
    """
    """

    @staticmethod
    def search_answers(query: str) -> List[Dict]:
        where_clause, params = Search._build_substring_query(query)

        with sqlite3.connect(config.DB_PATH) as conn:
            # Execute search on DB, retrieving data from answers and blocks
            # tables
            # NOTE: The LIKE operator performs string comparisons as case-insensitive
            res = conn.execute(
                ("SELECT answers.id, title, blocks.content FROM answers "
                 "LEFT JOIN blocks on answers.id = blocks.answer_id "
                 f"WHERE {where_clause}"),
                params,
            )

            # Convert each search result into a dictionary, with content
            # containing a nested dictionary from the serialized JSON stored
            # in the DB.
            answers = [
                {"id": r[0], "title": r[1], "content": json.loads(r[2])} for r in res
            ]
            return answers

    @staticmethod
    def _build_substring_query(query: str) -> Tuple[List, List]:
        # Build parameter list by splitting query by whitespace into search terms
        parameters = [f"%{token}%" for token in query.split()]

        # Build where clause by duplicating the condition by the number of search terms
        where = " and ".join(["title LIKE ?"] * len(parameters))

        return (where, parameters)
