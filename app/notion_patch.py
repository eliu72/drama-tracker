import requests
import json
import logging
from typing import Union, Dict, List, Any

import secrets
import notion_patch_helpers as helpers

JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
MOVIE_DB_API_KEY = secrets.MOVIE_DB_API_KEY
MOVIE_DB_BASE_URL = "https://api.themoviedb.org/3/"


def get_title_details(
    title: str = "", content_type: str = "", language: str = "en", year: str = ""
) -> Dict:
    # query search endpoint
    query_url = (
        MOVIE_DB_BASE_URL
        + f"search/{content_type}?api_key={MOVIE_DB_API_KEY}"
        + f"&language={language}&query={title}&year={year}"
    )
    response = requests.get(query_url)
    data = response.json()

    # check return status
    if response.status_code != 200:
        raise Exception(
            "Title Search Error "
            + str(response.status_code)
            + ": "
            + str(response.reason)
        )

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
        + f"{content_type}/{movie_id}/credits?api_key={MOVIE_DB_API_KEY}&language=en"
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
    cast_list = data["cast"][:5]
    return cast_list


def patch_notion_db_item(page_details: Dict = {}, NOTION_KEY: str = "") -> None:

    # extract details from new notion databse item
    page_id = page_details["id"]
    content_type = page_details["properties"]["Content Type"]["select"]["name"]
    title = page_details["properties"]["Name"]["title"][0]["text"]["content"].replace(
        " ", "%"
    )

    if page_details["properties"]["Language"]["select"]:
        language = page_details["properties"]["Language"]["select"]["name"]
    else:
        language = ""

    try:
        # get details of the specified title
        title_details = get_title_details(title, content_type, language)
        cast_list = get_main_actors(title_details["id"], content_type)
    except Exception as e:
        logging.info(e)
        return e

    if content_type == "movie":
        date = "release_date"
    else:
        date = "first_air_date"
    # create patch_request
    patch_request = helpers.patch_all(
        helpers.get_template(),
        year=int(title_details[date][:4]),
        overview=title_details["overview"],
        cast_list=cast_list,
        genres=title_details["genres"],
        cover=title_details["poster_path"],
        rating=title_details["vote_average"],
        language=title_details["original_language"],
    )

    # check if poster_path exists
    if title_details["poster_path"] == "null" and title_details["backdrop_path"]:
        patch_request = helpers.patch_cover(
            patch_request,
            "https://image.tmdb.org/t/p/original" + title_details["backdrop_path"],
        )
    print(patch_request)
    # Notion API request
    notion_base_url = f"https://api.notion.com/v1/pages/{page_id}"
    NOTION_HEADER = {
        "Authorization": NOTION_KEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16",
    }
    response = requests.patch(
        notion_base_url, data=json.dumps(patch_request), headers=NOTION_HEADER
    )
    print(response.json())
    # check status code
    if response.status_code != 200:
        error = (
            "Notion API Error "
            + str(response.status_code)
            + ": "
            + str(response.reason)
        )
        return error
    return response.status_code
