from typing import Sequence
from dataclasses import dataclass

from github_api import get_rate_limit_core_remaining, get_stargazers_of_repo, get_stargazer_repos


@dataclass
class NeighbourRepository:
    repo: str
    stargazers: Sequence[str]


def get_star_neighbours(user_name: str, repo_name: str) -> Sequence[NeighbourRepository]:
    ...


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    from pprint import pprint as pp

    print(get_rate_limit_core_remaining())
    pp(get_stargazers_of_repo("msqd", "harp"))
    pp(get_stargazer_repos("Lenormju"))
    print(get_rate_limit_core_remaining())
