"""The web API provided for Stargazer. It is based on vanilla FastAPI."""

import logging
import secrets
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from stargazer_core import NeighbourRepository, StargazerCore

logger = logging.getLogger("stargazer.service")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    _setup_custom_logging()
    _init_core()
    yield


app = FastAPI(lifespan=_lifespan)
security = (
    HTTPBasic()
)  # cf https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#http-basic-auth


STARGAZER_CORE: StargazerCore | None = None


AUTHORIZED_LOGIN = "julien"
AUTHORIZED_PASSWORD = "xVE8WyVsOfpn5cEQfgqB"  # randomly generated


@app.get("/repos/{user}/{repo}/starneighbours")
async def get_star_neighbours(
    user: str,
    repo: str,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> Sequence[NeighbourRepository]:
    """If authenticated, compute the repos that are neighbours of the one provided."""
    _raise_if_not_properly_authenticated(credentials)
    return await STARGAZER_CORE.compute_star_neighbours(user_name=user, repo_name=repo)


def _raise_if_not_properly_authenticated(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> None:
    # this function has been copied from :
    # https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#fix-it-with-secretscompare_digest
    # TODO: add a better auth system
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = AUTHORIZED_LOGIN.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes,
        correct_username_bytes,
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = AUTHORIZED_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes,
        correct_password_bytes,
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def _setup_custom_logging() -> None:
    # cf https://stackoverflow.com/a/77007723/11384184
    stargazer_logger = logging.getLogger("stargazer")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    stargazer_logger.addHandler(handler)
    stargazer_logger.setLevel(logging.DEBUG)
    logger.debug("custom logging enabled")
    # TODO: integrate instead with uvicorn loggers ? how to forward ?


def _init_core() -> None:
    global STARGAZER_CORE
    STARGAZER_CORE = StargazerCore()  # will fail if the env var is not defined
