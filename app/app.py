from typing import Dict
import requests
import json
from flask import Flask
from flask import request
from flask_cors import CORS


from notion_patch import patch_notion_db_item
from notion_create_db_helpers import get_empty_template

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


@app.route("/create-database")
def create_database():
    query_parameters = request.args

    # get notion api key
    NOTION_KEY = query_parameters.get("notion_key")
    PAGE_TITLE = query_parameters.get("page_title")

    # search for page id
    notion_base_url = f"https://api.notion.com/v1/search"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    body = {"query": PAGE_TITLE}
    response = requests.post(
        notion_base_url, data=json.dumps(body), headers=NOTION_HEADER
    )

    # page id should be first search result
    PARENT_ID = response.json()["results"][0]["id"]

    # read notion database
    notion_base_url = f"https://api.notion.com/v1/databases"
    body = {
        "parent": {"type": "page_id", "page_id": PARENT_ID},
        "icon": {"type": "emoji", "emoji": "📺"},
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Show Tracker",
                },
            }
        ],
        "properties": get_empty_template(),
    }
    print(body)
    response = requests.post(
        notion_base_url, data=json.dumps(body), headers=NOTION_HEADER
    )
    print(response.reason)
    if response.status_code != 200:
        return "Error with creating Notion database. Please check your Notion Key and Parent Page ID. Make sure your integration is shared to the parent page."
    return "Success! Feel free to customize the title, icon, and cover but do not change the table properties!"


@app.route("/api")
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
    status = "Success!"
    for page in pages:
        if is_new_page(page):
            status = patch_notion_db_item(page, NOTION_KEY)

    return str(status)


def is_new_page(page: Dict = {}):
    if (
        page["properties"]["Overview"]["rich_text"] == []
        or page["properties"]["Actors"]["multi_select"] == []
        or page["properties"]["Genres"]["multi_select"] == []
        or page["cover"] is None
    ):
        return True
    return False
