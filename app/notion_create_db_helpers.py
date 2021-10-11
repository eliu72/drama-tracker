from typing import Dict 
 
def get_empty_template() -> Dict:
    return {
        "Name": {
            "title": {}
        },
        "Content Type": {"select": {}},
        "Year": {"number":{}},
        "Overview": {"rich_text": {}},
        "Actors": {"multi_select": {}},
        "Genres": {"multi_select": {}},
        "Rating": {"number": {}},
        "Language": {"select": {}},
    }