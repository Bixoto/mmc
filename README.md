# mmc

**mmc** is a **m**inimal **M**attermost **c**lient for Python. It calls the v4 API endpoints and is meant for basic
uses.

## Install

    pip install mmc

Requirement: Python 3.8+.

## Usage

```python
from mmc import Mattermost

m = Mattermost(
    "chat.example.com",
    access_token="...",
    team_id="...",
    team_slug="my-team",
)

print("Teams:")
for team in m.get_teams():
    print(f"* {team['display_name']}")

print("Users:")
for user in m.get_users():
    print(f"* {user['username']}")

for post in m.get_channel_posts(channel_id="..."):
    print(post["message"])

```
