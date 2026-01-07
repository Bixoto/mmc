from typing import List, Iterable, Tuple, Callable, Any, Iterator, TypeVar

from api_session import APISession, JSONDict

__all__ = ["Mattermost", "__version__"]

__version__ = "0.1.2"


def ordered_items(response: JSONDict, items_keys: str) -> List[Tuple[str, JSONDict]]:
    return [
        (item_id, response[items_keys][item_id])
        for item_id in response["order"]
    ]


F = TypeVar("F", bound=Callable[..., Any])


def min_version(_version: str) -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        return fn

    return decorator


class Mattermost(APISession):
    def __init__(self, domain: str, *, access_token: str, https: bool = True, **kwargs: Any):
        protocol = "https" if https else "http"
        self.public_url = f"{protocol}://{domain}"

        super().__init__(base_url=f"{self.public_url}/api/v4", **kwargs)
        self.headers["Authorization"] = f"Bearer {access_token}"
        self.domain = domain

    def get_post_url(self, team_slug: str, post_id: str) -> str:
        """Return a post URL given the team slug and the post ID."""
        return f"{self.public_url}/{team_slug}/pl/{post_id}"

    def _get_paginated_entities(self, endpoint: str, **params: Any) -> Iterator[JSONDict]:
        params = dict(params)
        page = params.get("page", 0)
        while True:
            if entities := self.get_json_api(endpoint,
                                             params={**params, "page": page}):
                yield from entities
                page += 1
            else:
                return

    def get_teams(self) -> Iterator[JSONDict]:
        """Get all teams."""
        teams: Iterator[JSONDict] = self._get_paginated_entities("/teams")
        return teams

    def get_channels(self, **kwargs: Any) -> Iterator[JSONDict]:
        """Get all channels."""
        channels: Iterator[JSONDict] = self._get_paginated_entities("/channels", **kwargs)
        return channels

    def get_users(self, **kwargs: Any) -> Iterator[JSONDict]:
        """Get all users."""
        users: Iterator[JSONDict] = self._get_paginated_entities("/users", **kwargs)
        return users

    @min_version("5.10")
    def get_bots(self, **kwargs: Any) -> Iterator[JSONDict]:
        """Get all bots."""
        bots: Iterator[JSONDict] = self._get_paginated_entities("/bots", **kwargs)
        return bots

    def get_custom_emojis(self, **kwargs: Any) -> Iterator[JSONDict]:
        """Get all custom emojis."""
        custom_emojis: Iterator[JSONDict] = self._get_paginated_entities("/emoji", **kwargs)
        return custom_emojis

    def get_channel_posts(self, channel_id: str, *, per_page: int = 100, before: str = "") -> Iterator[JSONDict]:
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

    @min_version("5.34")
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
        posts: List[JSONDict] = self.post_api("/posts/ids", json=ids).json()
        return posts

    def delete_post(self, post_id: str) -> Any:  # TODO: typing
        """Delete a post."""
        return self.delete_api(f"/posts/{post_id}", throw=True).json()

    # Usage
    # =====

    def get_total_channels_count(self, include_deleted: bool = False, **kwargs: Any) -> int:
        """Return the total channels count, for all teams."""
        kwargs.setdefault("params", {})
        kwargs["params"].update({
            "per_page": 1,
            "include_total_count": "true",
            "include_deleted": "true" if include_deleted else "false",
        })

        payload = self.get_json_api("/channels", **kwargs)
        total_count: int = payload["total_count"]
        return total_count

    @min_version("7.0")
    def get_total_posts_count(self, **kwargs: Any) -> int:
        """Return the total posts count, for all teams."""
        posts_count: int = self.get_json_api("/usage/posts", **kwargs)["count"]
        return posts_count

    @min_version("7.1")
    def get_total_file_storage_usage_bytes(self, **kwargs: Any) -> int:
        """Return the total file storage usage, in bytes."""
        total_bytes: int = self.get_json_api("/usage/storage", **kwargs)["bytes"]
        return total_bytes
