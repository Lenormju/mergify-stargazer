from contextlib import asynccontextmanager
import logging
from typing import Sequence, Annotated
import secrets

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from stargazer_core import NeighbourRepository, compute_star_neighbours


logger = logging.getLogger("stargazer.service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_custom_logging()
    yield


app = FastAPI(lifespan=lifespan)
security = HTTPBasic()  # cf https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#http-basic-auth


@app.get("/repos/{user}/{repo}/starneighbours")
def get_star_neighbours(
        user: str,
        repo: str,
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        ) -> Sequence[NeighbourRepository]:
    _raise_if_not_properly_authenticated(credentials)
    return compute_star_neighbours(user_name=user, repo_name=repo)


def _raise_if_not_properly_authenticated(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
    # this function has been copied from :
    # https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#fix-it-with-secretscompare_digest
    # TODO: add a better auth system
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"julien"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"xVE8WyVsOfpn5cEQfgqB"  # randomly generated
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


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
