import json
import sqlite3
from typing import Dict, List

import config

class Search:
    """
    """

    @staticmethod
    def search_answers(query: Dict) -> List[Dict]:
        with sqlite3.connect(config.DB_PATH) as conn:
            # Execute search on DB, retrieving data from answers and blocks
            # tables
            res = conn.execute(
                ("SELECT answers.id, title, blocks.content FROM answers "
                 "LEFT JOIN blocks on answers.id = blocks.answer_id "
                 "WHERE title LIKE ? "),
                [f"%{query}%"],
            )

            # Convert each search result into a dictionary, with content
            # containing a nested dictionary from the serialized JSON stored
            # in the DB.
            answers = [
                {"id": r[0], "title": r[1], "content": json.loads(r[2])} for r in res
            ]
            return answers
