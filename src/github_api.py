"""Interface to fetch the GitHub API for Stargazer-specific purposes."""

from __future__ import annotations

import asyncio
import functools
import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    Callable,
    ParamSpec,
    TypeAlias,
    TypeVar,
)

import httpx

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


MAXIMUM_PARALLEL_FETCHES = 20  # to prevent saturating GitHub rate API or our connection


JSON: TypeAlias = (
    dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
)  # https://stackoverflow.com/a/77361801/11384184


@dataclass
class _GitHubApiResponse:
    status_code: int
    json_data: JSON


class GithubApi:
    """
    Interface to request the GitHub API.

    It obeys rate-limiting and follows good practices.
    """

    def __init__(self, token: str) -> None:
        """Create a new GitHub API, sharing an HTTP client and limitations."""
        self.__token = token
        self.__client = httpx.AsyncClient()  # to be reused between calls
        self.__semaphore = asyncio.BoundedSemaphore(MAXIMUM_PARALLEL_FETCHES)

    @_reraise_key_error_exception_as_unexpected_github_response
    async def get_rate_limit_core_remaining(self) -> int:
        """Get the number of remaining requests that can me made on the API."""

        def raise_if_not_ok(status_code: int) -> None:
            if status_code != httpx.codes.OK:
                raise UnexpectedGithubResponseError(f"unexpected {status_code=!r}")

        result = self._github_api_get(
            # https://docs.github.com/en/rest/rate-limit/rate-limit
            url="https://api.github.com/rate_limit",
            final_status_code_handler=raise_if_not_ok,
        )
        return (await result)["resources"]["core"]["remaining"]
        # TODO: returning
        #  `datetime.datetime.fromtimestamp(result["resources"]["core"]["remaining"])`
        #  also could be useful

    @_reraise_key_error_exception_as_unexpected_github_response
    async def get_stargazers_of_repo(
        self, owner_name: str, repo_name: str
    ) -> Sequence[str]:
        """Get the users that have starred this repository."""

        def raise_if_not_processable_or_not_ok(status_code: int) -> None:
            if status_code == httpx.codes.UNPROCESSABLE_ENTITY:
                raise RateLimitError(f"received {status_code=!r}")
            if status_code != httpx.codes.OK:
                raise UnexpectedGithubResponseError(f"unexpected {status_code=!r}")

        result = self._github_api_get(
            # https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers
            url=f"https://api.github.com/repos/{owner_name}/{repo_name}/stargazers",
            final_status_code_handler=raise_if_not_processable_or_not_ok,
            params={
                "per_page": MAXIMUM_GET_STARGAZERS_PER_PAGE,
            },
            custom_accept_param=None,  # no need for the starring timestamp
            fetch_all_across_pagination=True,
        )
        return tuple(stargazer["login"] for stargazer in await result)

    @_reraise_key_error_exception_as_unexpected_github_response
    async def get_stargazer_repos(self, user_name: str) -> Sequence[str]:
        """Get the repositories that the user have starred."""

        def raise_if_not_ok(status_code: int) -> None:
            if status_code != httpx.codes.OK:
                raise UnexpectedGithubResponseError(f"unexpected {status_code=!r}")

        result = self._github_api_get(
            # https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-repositories-starred-by-a-user
            url=f"https://api.github.com/users/{user_name}/starred",
            final_status_code_handler=raise_if_not_ok,
            params={
                "per_page": MAXIMUM_GET_STARGAZERS_REPOS_PER_PAGE,
                # "sort" ignored
            },
            custom_accept_param=None,  # no need for the starring timestamp
            fetch_all_across_pagination=True,
        )
        return tuple(repo["full_name"] for repo in await result)

    async def _github_api_get(
        self,
        *,
        url: str,
        final_status_code_handler: Callable[[int], None] | None,
        params: dict[str, str | int] | None = None,
        custom_accept_param: str | None = None,
        fetch_all_across_pagination: bool = False,  # TODO: find better name
    ) -> JSON:
        """Make a GET request on the GitHub API using good defaults."""
        logger.debug(f"get github {url=!r} with {params=!r}")
        async with self.__semaphore:
            response = await self.__client.get(
                url=url,
                params=params,
                follow_redirects=True,
                timeout=DEFAULT_TIMEOUT_SECONDS,
                headers={
                    "Accept": (
                        "application/vnd.github+json"
                        if custom_accept_param is None
                        else custom_accept_param
                    ),
                    "Authorization": f"Bearer {self.__token}",
                    "User-Agent": "Lenormju/mergify-stargazer",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        if retry_after_value := response.headers.get(
            "retry-after"
        ):  # FIXME: untested !
            raise RateLimitError(
                f'received a "retry-after" by GitHub: {retry_after_value!r}',
            )
        if response.headers.get("X-RateLimit-Remaining") == "0":
            reset_value = response.headers.get("X-RateLimit-Reset")
            # reset_value is an UTC timestamp of when the rate will be replenished
            raise RateLimitError(
                f'received "X-RateLimit-Remaining"==0 by GitHub: {reset_value=!r}',
            )
            # TODO: don't raise if we are indeed asking the remaining rate (ironic !)
        # logger.debug(f"{response.headers=!r}")
        all_values = response.json()
        if fetch_all_across_pagination and (link_value := response.headers.get("Link")):
            next_url = _extract_next_from_header_link_value(link_value)
            last_url = _extract_last_from_header_link_value(link_value)
            for value in await asyncio.gather(
                *(
                    self._github_api_get(
                        url=other_page_url,
                        final_status_code_handler=None,
                        params=None,  # already included in link url, avoir overriding
                        custom_accept_param=custom_accept_param,
                        fetch_all_across_pagination=False,
                    )
                    for other_page_url in _generate_all_next_pages_to_fetch(
                        next_url=next_url, last_url=last_url
                    )
                )
            ):
                all_values.extend(value)  # assuming it's a list
        if final_status_code_handler is not None:
            final_status_code_handler(response.status_code)
        return all_values


def _extract_next_from_header_link_value(link_value: str) -> str | None:
    # TODO: could use a regex instead ?
    links = link_value.split(",")
    for link in links:
        link_url, link_rel = link.split(";")
        if link_rel.strip() == 'rel="next"':
            return link_url.strip("<> ")  # remove extra spaces and angle brackets
    return None


def _extract_last_from_header_link_value(link_value: str) -> str | None:
    # TODO: refactor this duplicate of `_extract_next_from_header_link_value`
    links = link_value.split(",")
    for link in links:
        link_url, link_rel = link.split(";")
        if link_rel.strip() == 'rel="last"':
            return link_url.strip("<> ")  # remove extra spaces and angle brackets
    return None


def _generate_all_next_pages_to_fetch(
    *, next_url: str | None, last_url: str | None
) -> Sequence[str]:
    link_pattern = re.compile(
        r"""
        (?P<before>.*&page=)
        (?P<page_number>\d+)
        (?P<after>.*?)
        """,
        re.VERBOSE,
    )
    if (next_url is None) or (last_url is None):
        return ()
    next_page_number = int(link_pattern.fullmatch(next_url).group("page_number"))
    last_page_number = int(link_pattern.fullmatch(last_url).group("page_number"))
    return tuple(
        link_pattern.sub(f"\\g<before>{page_number!s}\\g<after>", next_url)
        for page_number in range(next_page_number, last_page_number + 1)
    )
