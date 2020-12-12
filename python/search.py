import sqlite3
from typing import Dict, List

import config

class Search:
    """
    """

    @staticmethod
    def search_answers(query: Dict) -> List[Dict]:
        with sqlite3.connect(config.DB_PATH) as conn:
            res = conn.execute(
                "select id, title from answers where title like ? ",
                [f"%{query}%"],
            )
            return [{"id": r[0], "title": r[1]} for r in res]
