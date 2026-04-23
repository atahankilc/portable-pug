import shutil
from pathlib import Path
from typing import BinaryIO


class LocalFileStorage:
    """Filesystem-backed Storage. Writes under `root`, keys are relative paths."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root not in path.parents and path != self.root:
            raise ValueError(f"key escapes storage root: {key!r}")
        return path

    def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            shutil.copyfileobj(data, f)
        return key

    def get_local_path(self, key: str) -> Path:
        return self._resolve(key)

    def get_url(self, key: str, ttl: int = 300) -> str:
        return self._resolve(key).as_uri()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists():
            path.unlink()
