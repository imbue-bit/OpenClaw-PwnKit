import os
from typing import Dict, List, Optional

class VirtualOS:
    def __init__(self, target_id: str):
        self.target_id = target_id
        self.cwd: str = "/"
        self.env: Dict[str, str] = {}
        self.vfs_cache: Dict[str, List[str]] = {} # path -> list of files
        self.is_initialized: bool = False

    def update_cwd(self, new_cwd: str):
        self.cwd = new_cwd

    def update_env(self, env_vars: Dict[str, str]):
        self.env.update(env_vars)

    def cache_directory(self, path: str, contents: List[str]):
        self.vfs_cache[path] = contents

    def get_cached_dir(self, path: str) -> Optional[List[str]]:
        return self.vfs_cache.get(path)

    def resolve_path(self, target_path: str) -> str:
        """解析绝对或相对路径"""
        if target_path.startswith("/"):
            return os.path.normpath(target_path)
        else:
            return os.path.normpath(os.path.join(self.cwd, target_path))