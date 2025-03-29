import os
from typing import Sequence

import requests


# see https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28
# rate limit, cf https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28
# - primary :
#   - if unauthenticated : 60 calls per hour
#   - if authenticated : 5000 calls per hour (when not being a GitHub App)
# - secondary :
#   - 100 max concurrent requests
#   - 900 calls per minute on a single endpoint
#   - ... and others
# https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api?apiVersion=2022-11-28
# if rate limited :
# - check for "retry-after" response header
# - check for "x-ratelimit-remaining" response header being 0, then "x-ratelimit-reset"
# - wait exponential time
# - avoid being banned by making the calls anyway
# redirections : 301, 302, 307
# condition requests (time/change-based)
# https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
# - check for "link" header : rel="next"
# - "per_page" query parameter


token = os.getenv("GITHUB_API_ACCESS_TOKEN").strip()  # FIXME: store the secret another way


DEFAULT_TIMEOUT_SECONDS = 10
MAXIMUM_GET_STARGAZERS_PER_PAGE = 100


def get_rate_limit_core_remaining():
    """Get the number of remaining requests that can me made on the API."""
    response = _github_api_get(
        # https://docs.github.com/en/rest/rate-limit/rate-limit
        url=f"https://api.github.com/rate_limit",
    )
    if response.status_code != requests.codes.ok:
        raise ValueError(f"unexpected {response.status_code=!r}")  # FIXME better error
    else:
        data = response.json()
        # print(data)  # FIXME debug
        return data["resources"]["core"]["remaining"]


def get_stargazers_of_repo(owner_name: str, repo_name: str) -> Sequence[str]:
    """Get the users that have starred this repository."""
    response = _github_api_get(
        # https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers
        url=f"https://api.github.com/repos/{owner_name}/{repo_name}/stargazers",
        params={
            "per_page": MAXIMUM_GET_STARGAZERS_PER_PAGE,
        },
        custom_accept_param=None,  # no need for the starring timestamp
    )
    if response.status_code == requests.codes.unprocessable:
        raise ValueError(f"received {response.status_code=!r}")  # FIXME better error
    elif response.status_code == requests.codes.ok:
        response_data = response.json()
        stargazers = tuple(stargazer["login"] for stargazer in response_data)
        # FIXME: pagination !!!!
        return stargazers
    else:
        print(response.text)  # FIXME debug
        raise ValueError(f"unexpected {response.status_code=!r}")  # FIXME better error



def _github_api_get(*,
                    url: str,
                    params: dict[str, str | int] | None = None,
                    custom_accept_param: str | None = None,
                    ) -> requests.Response:
    """Make a GET request on the GitHub API using good defaults."""
    response = requests.get(
        url=url,
        params=params,
        allow_redirects=True,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        headers={
            "Accept": ("application/vnd.github+json" if custom_accept_param is None
                       else custom_accept_param),
            "Authorization": f"Bearer {token}",
            "User-Agent": "Lenormju/mergify-stargazer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if retry_after_value := response.headers.get("retry-after"):
        raise ValueError(f'received a "retry-after" by GitHub: {retry_after_value!r}')  # FIXME better error
    elif response.headers.get("X-RateLimit-Remaining") == "0":
        reset_value = response.headers.get("X-RateLimit-Reset")
        raise ValueError(f'received "X-RateLimit-Remaining"==0 by GitHub: {reset_value=!r}')  # FIXME better error
    else:
        return response
