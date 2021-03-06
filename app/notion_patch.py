import os
import json
import requests
from typing import Union, Dict, List, Any

import app.notion_patch_helpers as helpers

JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
MOVIE_DB_API_KEY = os.environ["MOVIE_DB_API_KEY"]
MOVIE_DB_BASE_URL = "https://api.themoviedb.org/3/"


def get_title_details(content_type: str = "", **kwargs) -> Dict:
    # query search endpoint
    query_url = MOVIE_DB_BASE_URL + f"search/{content_type}?api_key={MOVIE_DB_API_KEY}"

    # unpack kwargs
    for key, val in kwargs.items():
        if val:
            query_url += f"&{key}={val}"
    response = requests.get(query_url)
    data = response.json()

    # if title cannot be found, populate notion page with N/A and raise Exception
    if response.json()['results'] == []:
        raise Exception("Title Search Error")

    # get full details using id
    id = data["results"][0]["id"]
    query_url = MOVIE_DB_BASE_URL + f"{content_type}/{id}?api_key={MOVIE_DB_API_KEY}"
    response = requests.get(query_url)

    # check return status
    if response.status_code != 200:
        raise Exception(
            "Get Title Details Error "
            + str(response.status_code)
            + ": "
            + str(response.reason)
        )

    return response.json()


def get_main_actors(movie_id: str = "", content_type: str = "") -> List[str]:
    # query credits endpoint
    query_url = (
        MOVIE_DB_BASE_URL
        + f"{content_type}/{movie_id}/credits?api_key={MOVIE_DB_API_KEY}"
    )
    response = requests.get(query_url)

    # check return status
    if response.status_code != 200:
        raise Exception(
            "Get Main Actors Error "
            + str(response.status_code)
            + ": "
            + str(response.reason)
        )

    data = response.json()
    max_cast_list = min(5, len(data))
    cast_list = data["cast"][:max_cast_list]

    return cast_list


def patch_notion_db_item(page_details: Dict = {}, NOTION_KEY: str = "") -> None:
    # return error if content_type is not specified
    if page_details["properties"]["Content Type"]["select"] is None:
        return "'Content Type' not specified!"

    # extract details from new notion database item
    page_id = page_details["id"]
    content_type = page_details["properties"]["Content Type"]["select"]["name"]

    # different year notation for movie vs tv
    if content_type == "movie":
        date = "release_date"
        year = "year"
    else:
        date = "first_air_date"
        year = "first_air_date_year"

    # kwargs for search query
    kwargs = {
        "query": page_details["properties"]["Name"]["title"][0]["text"][
            "content"
        ].replace(" ", "%20"),
        year: page_details["properties"]["Year"]["number"],
    }

    # Notion API request
    notion_base_url = f"https://api.notion.com/v1/pages/{page_id}"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }

    try:
        # get details of the specified title
        title_details = get_title_details(content_type, **kwargs)
        cast_list = get_main_actors(title_details["id"], content_type)
    except Exception as e:
        patch_request = helpers.patch_all(helpers.get_template())
        response = requests.patch(
            notion_base_url, data=json.dumps(patch_request), headers=NOTION_HEADER
        )
        # check status code
        if response.status_code != 200:
            error_message = (
                "Notion API Error "
                + str(response.status_code)
                + " ("
                + str(response.reason)
                + ")"
            )
            return str(e) + error_message
        return str(e)

    # create patch_request
    patch_request = helpers.patch_all(
        helpers.get_template(),
        year=int(title_details.get(date, "-1")[:4]),
        overview=title_details.get("overview", "N/A"),
        cast_list=cast_list,
        genres=title_details.get("genres", []),
        cover=title_details.get("poster_path", title_details.get("backdrop_path", "")),
        rating=title_details.get("vote_average", -1),
        language=title_details.get("original_language", "N/A"),
    )
 
    response = requests.patch(
        notion_base_url, data=json.dumps(patch_request), headers=NOTION_HEADER
    )

    # check status code
    if response.status_code != 200:
        return (
            "Notion API Error "
            + str(response.status_code)
            + " ("
            + str(response.reason)
            + ")"
        )
    return "Success!"
