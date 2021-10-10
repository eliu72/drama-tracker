from typing import Dict, List


def get_template() -> Dict:
    return {
        "properties": {
            "Year": {"number": 2021},
            "Overview": {"rich_text": [{"text": {"content": ""}}]},
            "Actors": {"multi_select": []},
            "Genres": {"multi_select": []},
            "Rating": {"number": 0},
            "Language": {"select": {"name": "en"}},
        },
        "cover": {"type": "external", "external": {"url": ""}},
    }


def patch_year(template: Dict = {}, year: int = 0):
    template["properties"]["Year"]["number"] = year
    return template


def patch_overview(template: Dict = {}, overview: str = ""):
    template["properties"]["Overview"]["rich_text"] = [{"text": {"content": overview}}]
    return template


def patch_actors(template: Dict = {}, cast_list: List[Dict] = []):
    for actor in cast_list:
        template["properties"]["Actors"]["multi_select"].append({"name": actor["name"]})
    return template


def patch_genres(template: Dict = {}, genres_list: List[Dict] = []):
    for genre in genres_list:
        template["properties"]["Genres"]["multi_select"].append({"name": genre["name"]})
    return template


def patch_cover(template: Dict = {}, filepath: str = ""):
    template["cover"]["external"]["url"] = "https://image.tmdb.org/t/p/w500" + filepath
    return template


def patch_rating(template: Dict = {}, rating: int = 0):
    template["properties"]["Rating"]["number"] = rating
    return template


def patch_language(template: Dict = {}, language: str = "en"):
    template["properties"]["Language"]["select"]["name"] = language
    return template


def patch_all(template: Dict = {}, **kwargs):
    template = patch_year(template, kwargs["year"])
    template = patch_overview(template, kwargs["overview"])
    template = patch_actors(template, kwargs["cast_list"])
    template = patch_genres(template, kwargs["genres"])
    template = patch_cover(template, kwargs["cover"])
    template = patch_rating(template, kwargs["rating"])
    template = patch_language(template, kwargs["language"])
    return template
