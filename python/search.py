import json
import sqlite3
from typing import Dict, List, Tuple

import config


class Search:
    """
    Represents search objects and interfaces to the answers and blocks DB
    tables
    """

    @staticmethod
    def search_answers(query: str) -> List[Dict]:
        """
        Search for answers!  More specifically, search answers table for
        matches to query.

        The current search implementation tokenizes query and returns results
        where ALL search terms are found SOMEWHERE in answers (or content).

        Args:
            query (str): The search string to match in answers

        Returns: A list of results each containing the deserialized JSON
            content as a dictionary.
        """
        # First search answers table for matches
        query_terms = query.split()
        answers = Search._search_answers(query_terms)

        # Omit matched records and search in remaining blocks
        ids = [a['id'] for a in answers]
        answers.extend(Search._search_remaining_blocks(query_terms, ids))

        return answers

    @staticmethod
    def _search_answers(query_terms: List[str]) -> List[Dict]:
        # Keyword search requires splitting query into words and generating
        # SQL where clause with dynamic number of expressions
        where_clause, params = Search._build_substring_query(query_terms, 'title')

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
            return [
                {"id": r[0], "title": r[1], "content": json.loads(r[2])}
                for r in res
            ]

    @staticmethod
    def _search_remaining_blocks(
            query_terms: List[str],
            omit_ids: List[str]
    ) -> List[Dict]:

        return []


    @staticmethod
    def _build_substring_query(
            query_terms: List[str],
            column: str
    ) -> Tuple[List, List]:
        # Build parameter list by mapping query terms into SQL wildcards
        parameters = [f"%{term}%" for term in query_terms]

        # Build where clause by duplicating the condition by the number of search terms
        where = " and ".join([f"{column} LIKE ?"] * len(parameters))

        return (where, parameters)
