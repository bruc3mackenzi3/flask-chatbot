import re
import sqlite3
from typing import List, Union

import config


class Messages:
    """
    Represents message objects and interfaces to the messages and state DB
    tables
    """
    @staticmethod
    def get_filled_messages() -> List[str]:
        """
        Retrieve all messages from the database and fills in the variables.

        Returns:
            list: The filled in messages
        """
        with sqlite3.connect(config.DB_PATH) as conn:
            messages_res = conn.execute("select body from messages")
            return [Messages._fill_message(m[0]) for m in messages_res]

    @staticmethod
    def _fill_message(message: str) -> str:
        """
        Given a message retrieved from the messages table fill each variable
        with the appropriate value.

        Args:
            message (str): The message to parse and fill

        Returns:
            str: The processed message with values filled in
        """
        tokens = re.split('([{}])', message)
        i = 0
        while i < len(tokens):
            if tokens[i] == '{':
                tokens.pop(i)  # pop {, i becomes next token
                tokens[i] = Messages._substitute_value(tokens[i])
                tokens.pop(i+1)  # pop }
            i += 1

        return ''.join(tokens)

    @staticmethod
    def _substitute_value(token: str) -> str:
        """
        Given a token from a parsed message parse further to extract the
        variable ID and fallback value.  Returns the appropriate value to be
        replaced.

        Args:
            token (str):
                The token from which variable ID and fallback value are
                extracted.

                The token passed should take the following form:
                    <variable ID>|<fallback value>

                E.g.:
                    asdf|something

        Returns:
            str: The value associated with the ID if it exists, otherwise
                returns the fallback value.
        """
        variable_id, _, fallback_value = re.split(r'(\|)', token)
        return Messages._get_state_value(variable_id, fallback_value)

    @staticmethod
    def _get_state_value(id: str, fallback=None) -> Union[str,None]:
        """
        Given a variable ID, attempt to retrieve the associated value from the
        database's state table.

        Args:
            id (str): The ID of an associated value
            fallback (str): The fallback value in case the variable is not
                found

        Returns:
            str: The value associated with the ID if it exists, otherwise
                returns the fallback value.
        """
        with sqlite3.connect(config.DB_PATH) as conn:
            cur = conn.execute(f"SELECT value FROM state WHERE id == '{id}'")
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return fallback
