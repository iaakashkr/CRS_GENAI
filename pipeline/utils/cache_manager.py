import pickle
import os
import time

class CacheManager:
    def __init__(self, cache_dir="cache"):
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_dir = cache_dir

    def get_cache_path(self, name):
        return os.path.join(self.cache_dir, f"{name}.pkl")

    def load(self, name):
        path = self.get_cache_path(name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        return None

    def save(self, name, obj):
        with open(self.get_cache_path(name), "wb") as f:
            pickle.dump(obj, f)
