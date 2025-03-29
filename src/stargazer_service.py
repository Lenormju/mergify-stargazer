from typing import Sequence
from dataclasses import dataclass
from collections import defaultdict

from github_api import get_rate_limit_core_remaining, get_stargazers_of_repo, get_stargazer_repos


@dataclass
class NeighbourRepository:
    repo: str
    stargazers: Sequence[str]


def get_star_neighbours(user_name: str, repo_name: str) -> Sequence[NeighbourRepository]:
    all_star_neighbours = defaultdict(list)

    repo_stargazers = get_stargazers_of_repo(user_name, repo_name)
    for stargazer_name in repo_stargazers:
        repos_of_stargazer = get_stargazer_repos(stargazer_name)
        for repo_fullname in repos_of_stargazer:
            all_star_neighbours[repo_fullname].append(stargazer_name)

    initial_repo_fullname = f"{user_name}/{repo_name}"
    del all_star_neighbours[initial_repo_fullname]  # we already know they share this one

    return tuple(
        NeighbourRepository(
            repo=repo_fullname,
            stargazers=repo_stargazers,
        )
        for repo_fullname, repo_stargazers in all_star_neighbours.items()
    )


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from pprint import pprint as pp
    print(get_rate_limit_core_remaining())
    pp(get_star_neighbours("msqd", "harp"))
    print(get_rate_limit_core_remaining())
