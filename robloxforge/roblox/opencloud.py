"""A small client for the Roblox Open Cloud API.

Open Cloud lets you manage a live experience programmatically with an API key —
publish place updates, read/write DataStores, broadcast messages to running
servers, and upload assets. This is how RobloxForge can take a generated game
beyond "opens in Studio" toward "live and updating on its own".

Docs: https://create.roblox.com/docs/cloud
Create an API key: https://create.roblox.com/dashboard/credentials

Every method raises :class:`OpenCloudError` on a non-2xx response so callers get
a clear, actionable message instead of a raw HTTP object.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from ..config import OpenCloudConfig

_BASE = "https://apis.roblox.com"


class OpenCloudError(RuntimeError):
    """Raised when an Open Cloud request fails or credentials are missing."""


class OpenCloudClient:
    """Thin wrapper over the Open Cloud REST endpoints used by the pipeline."""

    def __init__(self, config: OpenCloudConfig, *, timeout: float = 60.0) -> None:
        if not config.api_key:
            raise OpenCloudError(
                "No Open Cloud API key. Set ROBLOX_API_KEY (and ROBLOX_UNIVERSE_ID / "
                "ROBLOX_PLACE_ID). Create a key at "
                "https://create.roblox.com/dashboard/credentials"
            )
        self.config = config
        self._http = httpx.Client(
            timeout=timeout, headers={"x-api-key": config.api_key}
        )

    # --------------------------------------------------------------- helpers
    def _check(self, resp: httpx.Response) -> Any:
        if resp.status_code >= 400:
            raise OpenCloudError(
                f"Open Cloud {resp.request.method} {resp.request.url} "
                f"failed ({resp.status_code}): {resp.text[:500]}"
            )
        if resp.headers.get("content-type", "").startswith("application/json"):
            return resp.json()
        return resp.text

    # ----------------------------------------------------------------- place
    def publish_place(
        self,
        place_file: str | Path,
        *,
        universe_id: str | None = None,
        place_id: str | None = None,
        published: bool = True,
    ) -> dict[str, Any]:
        """Upload a ``.rbxl``/``.rbxlx`` as a new version of a place.

        ``published=True`` releases it to players; ``False`` saves a draft.
        Returns the API response (includes the new ``versionNumber``).
        """
        universe_id = universe_id or self.config.universe_id
        place_id = place_id or self.config.place_id
        if not (universe_id and place_id):
            raise OpenCloudError("universe_id and place_id are required to publish.")

        path = Path(place_file)
        data = path.read_bytes()
        content_type = "application/xml" if path.suffix == ".rbxlx" else "application/octet-stream"
        version_type = "Published" if published else "Saved"

        resp = self._http.post(
            f"{_BASE}/universes/v1/{universe_id}/places/{place_id}/versions",
            params={"versionType": version_type},
            content=data,
            headers={"Content-Type": content_type},
        )
        return self._check(resp)

    # ------------------------------------------------------------- datastore
    def set_datastore_entry(
        self, datastore: str, key: str, value: Any, *, universe_id: str | None = None
    ) -> Any:
        """Write a JSON-serialisable ``value`` to a standard DataStore entry."""
        universe_id = universe_id or self.config.universe_id
        if not universe_id:
            raise OpenCloudError("universe_id is required for DataStore access.")
        resp = self._http.post(
            f"{_BASE}/datastores/v1/universes/{universe_id}"
            "/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore, "entryKey": key},
            content=json.dumps(value),
            headers={"Content-Type": "application/json"},
        )
        return self._check(resp)

    def get_datastore_entry(
        self, datastore: str, key: str, *, universe_id: str | None = None
    ) -> Any:
        """Read a standard DataStore entry."""
        universe_id = universe_id or self.config.universe_id
        if not universe_id:
            raise OpenCloudError("universe_id is required for DataStore access.")
        resp = self._http.get(
            f"{_BASE}/datastores/v1/universes/{universe_id}"
            "/standard-datastores/datastore/entries/entry",
            params={"datastoreName": datastore, "entryKey": key},
        )
        return self._check(resp)

    # --------------------------------------------------------------- message
    def publish_message(
        self, topic: str, message: str, *, universe_id: str | None = None
    ) -> None:
        """Broadcast a message to live servers subscribed to ``topic``."""
        universe_id = universe_id or self.config.universe_id
        if not universe_id:
            raise OpenCloudError("universe_id is required for MessagingService.")
        resp = self._http.post(
            f"{_BASE}/messaging-service/v1/universes/{universe_id}/topics/{topic}",
            json={"message": message},
            headers={"Content-Type": "application/json"},
        )
        self._check(resp)

    # ----------------------------------------------------------------- asset
    def upload_asset(
        self,
        file_path: str | Path,
        *,
        asset_type: str,
        display_name: str,
        description: str = "",
    ) -> Any:
        """Upload an image/audio/model asset via the Assets API.

        ``asset_type`` is e.g. ``"Decal"``, ``"Audio"``, ``"Model"``. Returns the
        operation response (asset uploads are asynchronous operations).
        """
        if not self.config.creator_id:
            raise OpenCloudError("ROBLOX_CREATOR_ID is required to upload assets.")
        path = Path(file_path)
        creator = (
            {"groupId": self.config.creator_id}
            if self.config.creator_type.lower() == "group"
            else {"userId": self.config.creator_id}
        )
        request = {
            "assetType": asset_type,
            "displayName": display_name,
            "description": description,
            "creationContext": {"creator": creator},
        }
        files = {
            "request": (None, json.dumps(request), "application/json"),
            "fileContent": (path.name, path.read_bytes(), "application/octet-stream"),
        }
        resp = self._http.post(f"{_BASE}/assets/v1/assets", files=files)
        return self._check(resp)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> OpenCloudClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
