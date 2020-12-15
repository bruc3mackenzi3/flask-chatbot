import json
import sqlite3
from typing import Dict, List

import config
from util import Util


class Search:
    """
    Represents search objects and interfaces to the answers and blocks DB
    tables
    """

    # Keys on which to skip search in content.block JSON objects
    CONTENT_OMIT_KEYS = ["type"]

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
        ids = [a["id"] for a in answers]
        answers.extend(Search._search_remaining_blocks(query_terms, ids))

        return answers

    @staticmethod
    def _search_answers(query_terms: List[str]) -> List[Dict]:
        # Keyword search requires splitting query into words and generating
        # SQL where clause with dynamic number of expressions
        where_clause, params = Util.build_substring_query(query_terms, "title")

        with sqlite3.connect(config.DB_PATH) as conn:
            # Execute search on DB, retrieving data from answers and blocks
            # tables
            # NOTE: The LIKE operator performs string comparisons as case-insensitive
            res = conn.execute(
                ("SELECT answers.id, title, content FROM answers "
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
        # Build parameters
        where_clause, params = Util.build_substring_query(
                query_terms,
                "title || content"
        )
        omit_ids_sql = Util.to_sql_list(omit_ids)

        # First query the DB for matching records, omitting answers already
        # matched
        with sqlite3.connect(config.DB_PATH) as conn:
            res = conn.execute(
                ("SELECT answers.id, title, content FROM answers "
                 "LEFT JOIN blocks on answers.id = blocks.answer_id "
                 f"WHERE answers.id NOT IN {omit_ids_sql} "
                 f"AND {where_clause}"),
                params,
            )
        answers = [
            {"id": r[0], "title": r[1], "content": json.loads(r[2])}
            for r in res
        ]

        # Search only the content values to verify the results.  This prevents
        # matches on key names and metadata
        final_match = []
        for a in answers:
            match_found = True
            for term in query_terms:
                if term.lower() in a["title"].lower():
                    # Skip search if term matched with title
                    continue
                res = Util.search_nested_dict_values(
                        a["content"],
                        term,
                        Search.CONTENT_OMIT_KEYS
                )
                if res == False:
                    match_found = False
                    break
            if match_found:
                final_match.append(a)

        return final_match
