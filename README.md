# Stargazer

Find GitHub repositories that are star-close.

## Dev setup

[Create a fine-grained personal access token](https://github.com/settings/personal-access-tokens), without any account permissions.
Store the string starting with `github_pat_` in your password manager, you can not retrieve it after that.

GitHub recommends using keyvaults that the application gets its token (secret) from.
For now, the application will read the secret from its environment. So use your preferred way to add it :
* create an `.env` file, and `source` it,
* ` export GITHUB_API_ACCESS_TOKEN='github_pat_...'` (with a leading space to not be stored in the shell history),
* IDE support,
* ...

Install the dependencies using [`uv`](https://docs.astral.sh/uv/) : `uv sync --frozen --group dev`.

Run the application : `uv run src/stargazer_service.py`.

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

* async requests ?
* keyring instead of env file ?
