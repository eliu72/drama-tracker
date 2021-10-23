import requests
import json
from flask import Flask
from flask import request
from flask_cors import CORS


from app.notion_patch import patch_notion_db_item
from app.notion_create_db_helpers import get_empty_template

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
    DATABASE_TITLE = query_parameters.get("database_title")

    # search for page id
    notion_base_url = "https://api.notion.com/v1/search"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    body = {"query": DATABASE_TITLE}
    response = requests.post(
        notion_base_url, data=json.dumps(body), headers=NOTION_HEADER
    )

    # page id should be first search result
    DATABASE_ID = response.json()["results"][0]["id"]

    # create notion database
    notion_base_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    body = {
        "properties": get_empty_template(),
    }
    response = requests.patch(
        notion_base_url, data=json.dumps(body), headers=NOTION_HEADER
    )
    if response.status_code != 200:
        return "Error with creating Notion database. Please check your Notion Key and Parent Page ID. Make sure your integration is shared to the parent page."  # noqa: E501
    return "Success! Feel free to customize the title, icon, and cover, but do not change the table properties! Add this link to your description: <> to sync changes."  # noqa: E501


@app.route("/api")
def api():
    query_parameters = request.args

    # get notion api key
    NOTION_KEY = query_parameters.get("notion_key")
    DATABASE_TITLE = query_parameters.get("database_title")

    # search for page id
    notion_base_url = "https://api.notion.com/v1/search"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    body = {"query": DATABASE_TITLE}
    response = requests.post(
        notion_base_url, data=json.dumps(body), headers=NOTION_HEADER
    )

    # page id should be first search result
    DATABASE_ID = response.json()["results"][0]["id"]

    # read notion database and filter only new entries
    notion_base_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    page_filter = {
        "filter": {
            "and": [
                {"property": "Overview", "text": {"is_empty": True}},
                {"property": "Actors", "multi_select": {"is_empty": True}},
                {"property": "Genres", "multi_select": {"is_empty": True}},
            ]
        }
    }
    response = requests.post(
        notion_base_url, data=json.dumps(page_filter), headers=NOTION_HEADER
    )

    pages = response.json()["results"]
    status = str(len(pages)) + " new title(s) queried!\n"
    for page in pages:
        status += page["properties"]["Name"]["title"][0]["text"]["content"] + ": " + patch_notion_db_item(page, NOTION_KEY) + "\n"

    return str(status)
