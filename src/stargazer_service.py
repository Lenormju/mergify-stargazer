from contextlib import asynccontextmanager
from typing import Sequence
from dataclasses import dataclass
from collections import defaultdict
import logging

from fastapi import FastAPI

from github_api import get_rate_limit_core_remaining, get_stargazers_of_repo, get_stargazer_repos


logger = logging.getLogger("stargazer.service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_custom_logging()
    yield


app = FastAPI(lifespan=lifespan)


@dataclass  # TODO: pydantic
class NeighbourRepository:
    repo: str
    stargazers: Sequence[str]


@app.get("/repos/{user}/{repo}/starneighbours")
def get_star_neighbours(user: str, repo: str) -> Sequence[NeighbourRepository]:
    return compute_star_neighbours(user_name=user, repo_name=repo)


def compute_star_neighbours(user_name: str, repo_name: str) -> Sequence[NeighbourRepository]:
    all_star_neighbours = defaultdict(list)

    repo_stargazers = get_stargazers_of_repo(user_name, repo_name)
    for stargazer_name in repo_stargazers:
        repos_of_stargazer = get_stargazer_repos(stargazer_name)
        for repo_fullname in repos_of_stargazer:
            all_star_neighbours[repo_fullname].append(stargazer_name)

    initial_repo_fullname = f"{user_name}/{repo_name}"
    del all_star_neighbours[initial_repo_fullname]  # we already know they share this one

    sorted_star_neighbours = tuple(
        sorted(
            (
                NeighbourRepository(
                    repo=repo_fullname,
                    stargazers=repo_stargazers,
                )
                for repo_fullname, repo_stargazers in all_star_neighbours.items()
            ),
            # sorting by descending number of stargazers, then by ascending repo fullnames
            # so we have to construct a key that is smart
            key=lambda neighbour:
            (
                -len(neighbour.stargazers),  # from most negative to least negative, so from bigger to smaller
                neighbour.repo,
            ),
            reverse=False,  # revert=False means "ascending order" of the key
        )
    )
    return sorted_star_neighbours


def setup_custom_logging() -> None:
    # cf https://stackoverflow.com/a/77007723/11384184
    stargazer_logger = logging.getLogger("stargazer")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    stargazer_logger.addHandler(handler)
    stargazer_logger.setLevel(logging.DEBUG)
    logger.debug("custom logging enabled")
    # TODO: integrate instead with uvicorn loggers ? how to forward ?


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from pprint import pprint as pp
    print(get_rate_limit_core_remaining())
    pp(compute_star_neighbours("Lenormju", "talk-et-cfp"))
    print(get_rate_limit_core_remaining())
