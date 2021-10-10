from typing import Dict
import requests
from flask import Flask
from flask import request
from flask_cors import CORS


from notion_patch import patch_notion_db_item

app = Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config["CORS_HEADERS"] = "Content-Type"


# running flask
###############################################
# poetry shell
# cd app
# python app.py
# python -m flask run

# Local Testing Params
###############################################
# http://127.0.0.1:5000/api?notion_key=<your-key>&database_id=<db-id>


@app.route("/api", methods=["GET"])
def api():
    query_parameters = request.args

    # get notion api key
    NOTION_KEY = query_parameters.get("notion_key")
    DATABASE_ID = query_parameters.get("database_id")

    # read notion database
    notion_base_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    response = requests.post(notion_base_url, headers=NOTION_HEADER)

    pages = response.json()["results"]
    status = 200
    for page in pages:
        if is_new_page(page):
            status = patch_notion_db_item(page, NOTION_KEY)

    return str(status)


def is_new_page(page: Dict):
    if (
        page["properties"]["Overview"]["rich_text"] == []
        or page["properties"]["Actors"]["multi_select"] == []
        or page["properties"]["Genres"]["multi_select"] == []
        or page["cover"] is None
    ):
        return True
    return False
