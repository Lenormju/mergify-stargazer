from github_api import _extract_next_from_header_link_value as extract


def test__extract_link_next__from_next_last() -> None:
    link_value = '<https://api.github.com/repositories/699532645/stargazers?per_page=100&page=2>; rel="next", <https://api.github.com/repositories/699532645/stargazers?per_page=100&page=400>; rel="last"'
    expected_next = "https://api.github.com/repositories/699532645/stargazers?per_page=100&page=2"
    actual_next = extract(link_value)
    assert actual_next == expected_next


# def test__extract_link_next__from_next_
