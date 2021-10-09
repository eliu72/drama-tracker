import requests
from typing import Union, Dict, List, Any

from drama_tracker import secrets

JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
MOVIE_DB_API_KEY = secrets.MOVIE_DB_API_KEY


def get_title_details(page_properties: Dict) -> Dict:
    # get specific properties about request title
    content_type = page_properties["Content Type"][0]["text"]
    title = page_properties["Title"][0]["text"]
    language = page_properties["Language"]["name"]

    # send request to the Movie DB API
    MOVIE_DB_BASE_URL = (
        f"https://api.themoviedb.org/3/search/{content_type}?api_key={MOVIE_DB_API_KEY}"
    )
    request_url = MOVIE_DB_BASE_URL + f"&language={language}&query={title}"
    response = requests.get(request_url).json()

    # return closest search result
    return response["results"][0]


# def patch_notion_db_item(page_details: JSON = None) -> None:
#     page_details = json.loads(page_details)
#     page_id = page_details["id"]
#     page_properties = page_details["properties"]

#     title_details = get_title_details(page_properties)
