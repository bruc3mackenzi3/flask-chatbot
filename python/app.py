from pprint import pprint
import sqlite3

from flask import Flask, request, jsonify

import config
from messages import Messages


app = Flask(__name__)

@app.route("/messages", methods=["GET"])
def messages_route():
    """
    Return all the messages
    """
    messages = Messages.get_filled_messages()
    return jsonify(messages), 200


@app.route("/search", methods=["POST"])
def search_route():
    """
    Search for answers!

    Accepts a 'query' as JSON post, returns the full answer.

    curl -d '{"query":"Star Trek"}' -H "Content-Type: application/json" -X POST http://localhost:5000/search
    """

    with sqlite3.connect(config.DB_PATH) as conn:
        query = request.get_json().get("query")
        res = conn.execute(
            "select id, title from answers where title like ? ", [f"%{query}%"],
        )
        answers = [{"id": r[0], "title": r[1]} for r in res]
        print(query, "--> ")
        pprint(answers)
        return jsonify(answers), 200


if __name__ == "__main__":
    app.run(debug=True)
