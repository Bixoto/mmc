from typing import List, Iterable, Optional

from api_session import APISession


class Mattermost(APISession):
    def __init__(self, domain: str, access_token: str, *, team_id: str, team_slug: str):
        super().__init__(
            base_url=f"https://{domain}/api/v4",
        )
        self.headers["Authorization"] = f"Bearer {access_token}"
        self.domain = domain
        self.team_id = team_id
        self.team_slug = team_slug

    def post_link(self, post_id: str):
        return f"https://{self.domain}/{self.team_slug}/pl/{post_id}"

    def get_teams(self):
        return self.get_json_api("/teams")

    def get_channels(self):
        return self.get_json_api("/channels")

    def get_users(self):
        return self.get_json_api("/users")

    def get_bots(self):
        return self.get_json_api("/bots")

    def get_channel_posts(self, channel_id: str):
        before = ""
        per_page = 100
        while True:
            resp = self.get_json_api(f"/channels/{channel_id}/posts?per_page={per_page}&before={before}")

            if not resp["order"]:
                return

            for post_id in resp["order"]:
                yield resp["posts"][post_id]
                before = post_id

    def get_files(self, terms: str):
        return self.post_api(f"/teams/{self.team_id}/files/search", json={"terms": terms, "is_or_search": False}).json()

    def iter_all_files(self, extensions: Optional[Iterable[str]] = None):
        if extensions is None:
            # Didn't find a way to query all files at once
            extensions = [
                "pdf", "zip", "7z", "gz", "bz2", "tar", "gzip", "jpeg", "jpg", "tiff", "gif", "png", "docx", "doc",
                "xls", "xlsx", "webp", "webm", "mp4", "mp3", "avi", "txt", "json", "jsons", "csv", "tsv",
            ]
        for extension in extensions:
            payload = self.get_files(f"ext:{extension}")
            yield from payload["file_infos"].values()

    def get_posts_by_ids(self, ids: List[str]):
        return self.post_api("/posts/ids", json=ids).json()

    def delete_post(self, post_id: str):
        return self.delete_api(f"/posts/{post_id}", throw=True).json()
