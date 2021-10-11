from typing import Dict


def get_empty_template() -> Dict:
    return {
        "Content Type": {"select": {"options": [{"name": "movie"}, {"name": "tv"}]}},
        "Year": {"number": {}},
        "Overview": {"rich_text": {}},
        "Actors": {"multi_select": {}},
        "Genres": {"multi_select": {}},
        "Rating": {"number": {}},
        "Language": {"select": {}},
        "Tags": None,
        "Personal Rating": {"select": {"options": [
            {"name": "⭐", "color": "default"},
            {"name": "⭐⭐", "color": "default"},
            {"name": "⭐⭐⭐", "color": "default"},
            {"name": "⭐⭐⭐⭐", "color": "default"},
            {"name": "⭐⭐⭐⭐⭐", "color": "default"}
        ]}},
        "Personal Review": {"rich_text": {}}
    }
