# import pytest

from drama_tracker import notion_patch_helpers as helpers


def test_patch_year():
    template = helpers.patch_year(helpers.get_template(), 2021)
    assert template["properties"]["Year"]["number"] == 2021


def test_patch_overview():
    template = helpers.patch_overview(helpers.get_template(), "Random Text")
    assert template["properties"]["Overview"]["rich_text"] == [
        {"text": {"content": "Random Text"}}
    ]


def test_patch_actors():
    template = helpers.patch_actors(
        helpers.get_template(), [{"name": "Suzy Bae"}, {"name": "Simu Liu"}]
    )
    assert template["properties"]["Actors"]["multi_select"] == [
        {"name": "Suzy Bae"},
        {"name": "Simu Liu"},
    ]


def test_patch_genres():
    template = helpers.patch_genres(
        helpers.get_template(), [{"name": "Sci-fi"}, {"name": "Romance"}]
    )
    assert template["properties"]["Genres"]["multi_select"] == [
        {"name": "Sci-fi"},
        {"name": "Romance"},
    ]


def test_patch_cover():
    template = helpers.patch_cover(helpers.get_template(), "/bogus_filepath.jpg")
    assert (
        template["cover"]["external"]["url"]
        == "https://image.tmdb.org/t/p/original/bogus_filepath.jpg"
    )
