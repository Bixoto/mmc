from typing import List, Iterable, Tuple

from api_session import APISession, JSONDict

__all__ = ["Mattermost", "__version__"]

__version__ = "0.1.0"

def ordered_items(response: JSONDict, items_keys: str) -> List[Tuple[str, JSONDict]]:
    return [
        (item_id, response[items_keys][item_id])
        for item_id in response["order"]
    ]


class Mattermost(APISession):
    def __init__(self, domain: str, *, access_token: str, https=True, **kwargs):
        protocol = "https" if https else "http"
        self.public_url = f"{protocol}://{domain}"

        super().__init__(base_url=f"{self.public_url}/api/v4", **kwargs)
        self.headers["Authorization"] = f"Bearer {access_token}"
        self.domain = domain

    def get_post_url(self, team_slug: str, post_id: str):
        """Return a post URL given the team slug and the post ID."""
        return f"{self.public_url}/{team_slug}/pl/{post_id}"

    def _get_paginated_entities(self, endpoint: str, **params):
        params = dict(params)
        page = params.get("page", 0)
        while True:
            if entities := self.get_json_api(endpoint,
                                             params={**params, "page": page}):
                yield from entities
                page += 1
            else:
                return

    def get_teams(self) -> Iterable[JSONDict]:
        """Get all teams."""
        return self._get_paginated_entities("/teams")

    def get_channels(self, **kwargs) -> Iterable[JSONDict]:
        """Get all channels."""
        return self._get_paginated_entities("/channels", **kwargs)

    def get_users(self, **kwargs) -> Iterable[JSONDict]:
        """Get all users."""
        return self._get_paginated_entities("/users", **kwargs)

    def get_bots(self, **kwargs) -> Iterable[JSONDict]:
        """Get all bots."""
        return self._get_paginated_entities("/bots", **kwargs)

    def get_channel_posts(self, channel_id: str, *, per_page=100, before="") -> Iterable[JSONDict]:
        """Get all posts from a channel."""
        while True:
            resp = self.get_json_api(f"/channels/{channel_id}/posts",
                                     params={"per_page": per_page, "before": before})
            if posts := ordered_items(resp, "posts"):
                for post_id, post in posts:
                    yield post
                    before = post_id
            else:
                return

    def get_team_files(self, team_id: str, terms: str) -> Iterable[JSONDict]:
        """Get files matching search terms."""
        resp = self.post_api(f"/teams/{team_id}/files/search", json={
            "terms": terms,
            "is_or_search": False,
        }).json()
        return [
            file for _, file in ordered_items(resp, "file_infos")
        ]

    def get_posts_by_ids(self, ids: List[str]) -> Iterable[JSONDict]:
        """Get posts by their IDs."""
        return self.post_api("/posts/ids", json=ids).json()

    def delete_post(self, post_id: str):
        """Delete a post."""
        return self.delete_api(f"/posts/{post_id}", throw=True).json()
