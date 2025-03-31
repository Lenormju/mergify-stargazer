from github_api import _generate_all_next_pages_to_fetch as generate


def test__generate_with_next_and_last_different() -> None:
    next_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=8'
    last_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=13'
    next_pages_links = generate(next_url=next_link, last_url=last_link)
    assert next_pages_links == (
        'https://api.github.com/user/3281104/starred?per_page=100&page=8',
        'https://api.github.com/user/3281104/starred?per_page=100&page=9',
        'https://api.github.com/user/3281104/starred?per_page=100&page=10',
        'https://api.github.com/user/3281104/starred?per_page=100&page=11',
        'https://api.github.com/user/3281104/starred?per_page=100&page=12',
        'https://api.github.com/user/3281104/starred?per_page=100&page=13',
    )


def test__generate_with_next_and_last_same() -> None:
    next_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=8'
    last_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=8'
    next_pages_links = generate(next_url=next_link, last_url=last_link)
    assert next_pages_links == (
        'https://api.github.com/user/3281104/starred?per_page=100&page=8',
    )


def test__generate_without_next() -> None:
    next_link = None
    last_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=13'
    next_pages_links = generate(next_url=next_link, last_url=last_link)
    assert next_pages_links == ()


def test__generate_without_last() -> None:
    next_link = 'https://api.github.com/user/3281104/starred?per_page=100&page=8'
    last_link = None
    next_pages_links = generate(next_url=next_link, last_url=last_link)
    assert next_pages_links == ()
