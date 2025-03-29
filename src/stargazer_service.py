import os

import requests


# see https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28
# rate limit, cf https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28
# - primary :
#   - if unauthenticated : 60 calls per hour
#   - if authenticated : 5000 calls per hour (when not being a GitHub App)
# - secondary :
#   - 100 max concurrent requests
#   - 900 calls per minute on a single endpoint
#   - ... and others
# https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api?apiVersion=2022-11-28
# if rate limited :
# - check for "retry-after" response header
# - check for "x-ratelimit-remaining" response header being 0, then "x-ratelimit-reset"
# - wait exponential time
# - avoid being banned by making the calls anyway
# redirections : 301, 302, 307
# condition requests (time/change-based)
# https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
# - check for "link" header : rel="next"
# - "per_page" query parameter


token = os.getenv("GITHUB_API_ACCESS_TOKEN").strip()  # FIXME: store the secret another way


DEFAULT_TIMEOUT_SECONDS = 10


response = requests.get(
    # https://docs.github.com/en/rest/rate-limit/rate-limit
    url=f"https://api.github.com/rate_limit",
    allow_redirects=True,
    timeout=DEFAULT_TIMEOUT_SECONDS,
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Lenormju/mergify-stargazer",
        "X-GitHub-Api-Version": "2022-11-28",
    },
)
response.raise_for_status()
print(response.json())


owner_name = "msqd"
repo_name = "harp"


DEFAULT_TIMEOUT_SECONDS = 10


response = requests.get(
    # https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers
    url=f"https://api.github.com/repos/{owner_name}/{repo_name}/stargazers",
    params={
        "per_page": 100,
    },
    allow_redirects=True,
    timeout=DEFAULT_TIMEOUT_SECONDS,
    headers={
        "Accept": "application/vnd.github+json",  # no need for the starring timestamp
        "Authorization": f"Bearer {token}",
        "User-Agent": "Lenormju/mergify-stargazer",
        "X-GitHub-Api-Version": "2022-11-28",
    },
)
if response.status_code == requests.codes.unprocessable:
    raise ValueError(f"received {response.status_code=!r}")  # FIXME: better error
elif response.status_code == requests.codes.ok:
    response_data = response.json()
    stargazers = tuple(stargazer["login"] for stargazer in response_data)
    print(stargazers)
else:
    print(response.text)  # FIXME debug
    raise ValueError(f"unexpected {response.status_code=!r}")  # FIXME: better error
