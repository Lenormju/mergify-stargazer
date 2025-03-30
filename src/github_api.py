"""Interface to fetch the GitHub API for Stargazer-specific purposes."""

from __future__ import annotations

import functools
import logging
import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable, ParamSpec, TypeVar, TypeAlias

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


token = os.getenv(
    "GITHUB_API_ACCESS_TOKEN",
).strip()  # FIXME: store the secret another way


class GithubApiError(Exception):  # noqa: D101
    pass


class RateLimitError(GithubApiError):  # noqa: D101
    pass


class UnexpectedGithubResponseError(GithubApiError):  # noqa: D101
    pass


Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def _reraise_key_error_exception_as_unexpected_github_response(
    func: Callable[Param, RetType],
) -> Callable[[Param], RetType]:
    @functools.wraps(func)
    def wrapper(*args: Param, **kwargs: Param) -> RetType:
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            raise UnexpectedGithubResponseError from e

    return wrapper


logger = logging.getLogger("stargazer.github_api")


DEFAULT_TIMEOUT_SECONDS = 10
MAXIMUM_GET_STARGAZERS_PER_PAGE = 100
MAXIMUM_GET_STARGAZERS_REPOS_PER_PAGE = 100


@_reraise_key_error_exception_as_unexpected_github_response
def get_rate_limit_core_remaining() -> int:
    """Get the number of remaining requests that can me made on the API."""
    response = _github_api_get(
        # https://docs.github.com/en/rest/rate-limit/rate-limit
        url="https://api.github.com/rate_limit",
    )
    if response.status_code != requests.codes.ok:
        raise UnexpectedGithubResponseError(f"unexpected {response.status_code=!r}")
    return response.json_data["resources"]["core"]["remaining"]


@_reraise_key_error_exception_as_unexpected_github_response
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
        raise RateLimitError(f"received {response.status_code=!r}")
    if response.status_code == requests.codes.ok:
        stargazers = tuple(stargazer["login"] for stargazer in response.json_data)
        logger.debug(f"found {len(stargazers)=!r} for repo {owner_name}/{repo_name}")
        logger.debug(f"{stargazers=!r}")
        # FIXME: pagination !!!!
        return stargazers
    raise UnexpectedGithubResponseError(f"unexpected {response.status_code=!r}")


@_reraise_key_error_exception_as_unexpected_github_response
def get_stargazer_repos(user_name: str) -> Sequence[str]:
    """Get the repositories that the user have starred."""
    response = _github_api_get(
        # https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-repositories-starred-by-a-user
        url=f"https://api.github.com/users/{user_name}/starred",
        params={
            "per_page": MAXIMUM_GET_STARGAZERS_REPOS_PER_PAGE,
            # "sort" ignored
        },
        custom_accept_param=None,  # no need for the starring timestamp
    )
    if response.status_code == requests.codes.ok:
        stargazer_repos = tuple(repo["full_name"] for repo in response.json_data)
        logger.debug(f"found {len(stargazer_repos)=!r} for user {user_name}")
        logger.debug(f"{stargazer_repos=!r}")
        # FIXME: pagination !!!!
        return stargazer_repos
    raise UnexpectedGithubResponseError(f"unexpected {response.status_code=!r}")


_SESSION = requests.Session()  # to be reused between calls


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None  # https://stackoverflow.com/a/77361801/11384184


@dataclass
class _GitHubApiResponse:
    status_code: int
    json_data: JSON


def _github_api_get(
    *,
    url: str,
    params: dict[str, str | int] | None = None,
    custom_accept_param: str | None = None,
) -> _GitHubApiResponse:
    """Make a GET request on the GitHub API using good defaults."""
    logger.debug(f"get github {url=!r} with {params=!r}")
    response = _SESSION.get(
        url=url,
        params=params,
        allow_redirects=True,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        headers={
            "Accept": (
                "application/vnd.github+json"
                if custom_accept_param is None
                else custom_accept_param
            ),
            "Authorization": f"Bearer {token}",
            "User-Agent": "Lenormju/mergify-stargazer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if retry_after_value := response.headers.get("retry-after"):  # FIXME: untested !
        raise RateLimitError(
            f'received a "retry-after" by GitHub: {retry_after_value!r}',
        )
    if response.headers.get("X-RateLimit-Remaining") == "0":
        reset_value = response.headers.get("X-RateLimit-Reset")
        # reset_value is an UTC timestamp of when the rate will be replenished
        raise RateLimitError(
            f'received "X-RateLimit-Remaining"==0 by GitHub: {reset_value=!r}',
        )
    return _GitHubApiResponse(
        status_code=response.status_code,
        json_data=response.json(),
    )


def _extract_next_from_header_link_value(link_value: str) -> str | None:
    links = link_value.split(",")
    for link in links:
        link_url, link_rel = link.split(";")
        if link_rel.strip() == 'rel="next"':
            return link_url.strip("<>")
