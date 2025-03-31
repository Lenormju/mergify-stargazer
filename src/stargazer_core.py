"""The core of Stargazer : pure algorithm to find stargazers neighbours repos."""

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
    def __init__(self) -> None:
        self.github_api = GithubApi(token=os.environ["GITHUB_API_ACCESS_TOKEN"].strip())  # FIXME: store the secret another way ?


    def compute_star_neighbours(
        self,
        *,
        user_name: str,
        repo_name: str,
    ) -> Sequence[NeighbourRepository]:
        """
        Find all the neighbours repos.

        Two repos are neighbours if they both have been starred by an user (stargazer).
        They are returned ordered, the closest first (most shared stargazers).
        """
        all_star_neighbours = defaultdict(list)

        repo_stargazers = self.github_api.get_stargazers_of_repo(user_name, repo_name)
        i = 1
        for stargazer_name in repo_stargazers:
            print(i)
            i += 1
            repos_of_stargazer = self.github_api.get_stargazer_repos(stargazer_name)  # TODO: parallel
            for repo_fullname in repos_of_stargazer:
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
                        stargazers=repo_stargazers,
                    )
                    for repo_fullname, repo_stargazers in all_star_neighbours.items()
                ),
                # sorting by descending number of stargazers, then by asc. repo fullnames
                # so we have to construct a key that is smart
                key=lambda neighbour: (
                    -len(
                        neighbour.stargazers,
                    ),  # from most negative to least negative, so from bigger to smaller
                    neighbour.repo,
                ),
                reverse=False,  # revert=False means "ascending order" of the key
            ),
        )

    def get_rate(self) -> int:
        return self.github_api.get_rate_limit_core_remaining()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    from pprint import pprint as pp

    core = StargazerCore()
    print(core.github_api.get_rate_limit_core_remaining())  # noqa: T201
    # pp(core.compute_star_neighbours("astariul", "github-hosted-pypi"))  # noqa: T203
    pp(core.compute_star_neighbours("msqd", "harp"))  # noqa: T203
    print(core.github_api.get_rate_limit_core_remaining())  # noqa: T201
