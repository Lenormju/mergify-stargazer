from contextlib import asynccontextmanager
import logging
from typing import Sequence

from fastapi import FastAPI

from stargazer_core import NeighbourRepository, compute_star_neighbours


logger = logging.getLogger("stargazer.service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_custom_logging()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/repos/{user}/{repo}/starneighbours")
def get_star_neighbours(user: str, repo: str) -> Sequence[NeighbourRepository]:
    return compute_star_neighbours(user_name=user, repo_name=repo)


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
