# Stargazer

Find GitHub repositories that are star-close.

## Dev setup

[Create a fine-grained personal access token](https://github.com/settings/personal-access-tokens), without any account permissions.
Store the string (starting with `github_pat_`) in your password manager, you can not retrieve it after that.

GitHub recommends using keyvaults that the application gets its token (secret) from.
For now, the application will read the secret from its environment. So use your preferred way to add it :
* create an `.env` file, and `source` it,
* ` export GITHUB_API_ACCESS_TOKEN='github_pat_...'` (with a leading space to not be stored in the shell history),
* IDE support,
* ...

Install the dependencies using [`uv`](https://docs.astral.sh/uv/) : `uv sync --frozen --group dev`.

Run the application : `uv run fastapi run src/stargazer_api.py`.
By default, will run on `127.0.0.1:8000`, without auto-reload.

### Dev workflow

To format the code : `uv run ruff format src`

To lint the code : `uv run ruff check src`

To test the code : `uv run pytest`

## Vocabulary

* Users that star repositories are called stargazers.
* Two repositories are neighbour if they have been starred by the same stargazer.
  The more stargazers in common, the closer they are.

## Project objectives

* logical and maintainable code structure
* efficient use of data structure
* comments, testability and unit tests
* correctness
* insight into potential improvements
* scalability
* evolution of the code

## Ideas for later

* async requests for concurrent fetching
* keyring instead of env file
* uvicorn workers
* https
* Docker container
* CI
* input sanitization (with FastApi `Query` ?)
* nicer logging
* strong/integrated auth
* avoid f-strings in logging messages ?
* use pydantic BaseModel for validation
* use PyGitHub lib
