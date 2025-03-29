"""The core of Stargazer : pure algorithm to find stargazers neighbours repos."""

import logging
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from github_api import (
    get_rate_limit_core_remaining,
    get_stargazer_repos,
    get_stargazers_of_repo,
)

logger = logging.getLogger("stargazer.core")


@dataclass  # TODO: pydantic
class NeighbourRepository:
    """A repo fullname with its list of neighbours repos that share stargazers."""

    repo: str
    stargazers: Sequence[str]


def compute_star_neighbours(
    user_name: str,
    repo_name: str,
) -> Sequence[NeighbourRepository]:
    """
    Find all the neighbours repos.

    Two repos are neighbours if they both have been starred by an user (stargazer).
    They are returned ordered, the closest first (most shared stargazers).
    """
    all_star_neighbours = defaultdict(list)

    repo_stargazers = get_stargazers_of_repo(user_name, repo_name)
    for stargazer_name in repo_stargazers:
        repos_of_stargazer = get_stargazer_repos(stargazer_name)  # TODO: parallel
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


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    from pprint import pprint as pp

    print(get_rate_limit_core_remaining())  # noqa: T201
    pp(compute_star_neighbours("Lenormju", "talk-et-cfp"))  # noqa: T203
    print(get_rate_limit_core_remaining())  # noqa: T201
