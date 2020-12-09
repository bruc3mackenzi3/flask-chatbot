import re
import sqlite3
from typing import List

import config


class Messages:
    """
    Represents message objects and interfaces to the messages DB table
    """

    @staticmethod
    def get_filled_messages() -> List[str]:
        """Retrieve all messages from the database and fills in the variables.

        Returns:
            list: The filled in messages
        """

        with sqlite3.connect(config.DB_PATH) as conn:
            messages_res = conn.execute("select body from messages")
            return [Messages.fill_message(m[0]) for m in messages_res]

    @staticmethod
    def fill_message(message: str) -> str:
        """Given a message retrieved from the messages table fill each variable
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
        variable_id, _, fallback_value = re.split('(\|)', token)
        return fallback_value
