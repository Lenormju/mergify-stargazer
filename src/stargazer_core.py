"""The core of Stargazer : pure algorithm to find stargazers neighbours repos."""

import asyncio
import logging
import os
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from github_api import GithubApi

logger = logging.getLogger("stargazer.core")


@dataclass  # TODO: pydantic
class NeighbourRepository:
    """A repo fullname with its list of neighbours repos that share stargazers."""

    repo: str
    stargazers: Sequence[str]


class StargazerCore:
    """The Stargazer core class. It mostly computes star-neighbours' repos."""

    def __init__(self) -> None:
        """Create a new StargazerCore instance. Its token value is read from env."""
        self.github_api = GithubApi(
            token=os.environ["GITHUB_API_ACCESS_TOKEN"].strip()
        )  # FIXME: store the secret another way ?

    async def compute_star_neighbours(
        self,
        user_name: str,
        repo_name: str,
    ) -> Sequence[NeighbourRepository]:
        """
        Find all the neighbours repos.

        Two repos are neighbours if they both have been starred by an user (stargazer).
        They are returned ordered, the closest first (most shared stargazers).
        """
        all_star_neighbours = defaultdict(list)

        async def github_api_get_stargazers_repo_plus_return_stargazer_name(
            stargazer_name: str,
        ) -> tuple[str, Sequence[str]]:  # TODO: refactor
            return stargazer_name, await self.github_api.get_stargazer_repos(
                stargazer_name
            )

        repo_stargazers = await self.github_api.get_stargazers_of_repo(
            user_name, repo_name
        )
        for stargazer_name, stargazer_repos in await asyncio.gather(
            *(
                github_api_get_stargazers_repo_plus_return_stargazer_name(
                    stargazer_name
                )
                for stargazer_name in repo_stargazers
            )
        ):
            for repo_fullname in stargazer_repos:
                all_star_neighbours[repo_fullname].append(stargazer_name)

        initial_repo_fullname = f"{user_name}/{repo_name}"
        del all_star_neighbours[
            initial_repo_fullname
        ]  # we already know they share this one

        return tuple(
            sorted(
                (
                    NeighbourRepository(
                        repo=repo_fullname,
                        stargazers=sorted(repo_stargazers),
                    )
                    for repo_fullname, repo_stargazers in all_star_neighbours.items()
                ),
                # sort by descending number of stargazers, then by asc. repo fullnames
                # so we have to construct a key that is smart
                key=lambda neighbour: (
                    # from most negative to least negative, so from bigger to smaller
                    -len(neighbour.stargazers),
                    neighbour.repo,
                ),
                reverse=False,  # revert=False means "ascending order" of the key
            ),
        )

    async def get_rate(self) -> int:
        """Get the remaining number of requests for the hour."""
        return self.github_api.get_rate_limit_core_remaining()


if __name__ == "__main__":

    async def main():  # noqa: D103, ANN201
        import logging

        logging.basicConfig(level=logging.DEBUG)

        core = StargazerCore()

        print(await core.github_api.get_rate_limit_core_remaining())  # noqa: T201
        # pp(await core.compute_star_neighbours("astariul", "github-hosted-pypi"))  # noqa: ERA001, E501
        # pp(await core.compute_star_neighbours("msqd", "harp"))  # noqa: ERA001
        # pp(await core.compute_star_neighbours("meetup-python-grenoble", "meetup-python-grenoble.github.io"))  # noqa: ERA001, E501
        # pp(await core.compute_star_neighbours("Lenormju", "talk-et-cfp"))  # noqa: ERA001, E501
        print(await core.github_api.get_rate_limit_core_remaining())  # noqa: T201

    asyncio.run(main())
