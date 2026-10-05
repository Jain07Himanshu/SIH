import os
import yaml

class SynonymManager:
    def __init__(self, config_path: str = "configs/synonyms.yaml"):
        self.config_path = config_path
        self.synonym_map: dict[str, str] = {}
        self.load_synonyms()

    def load_synonyms(self) -> None:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                if "synonyms" in data and isinstance(data["synonyms"], dict):
                    data = data["synonyms"]
                for canonical, synonyms in data.items():
                    can_clean = str(canonical).lower().strip()
                    self.synonym_map[can_clean] = can_clean
                    if isinstance(synonyms, list):
                        for syn in synonyms:
                            self.synonym_map[str(syn).lower().strip()] = can_clean

    def canonicalize(self, term: str) -> str:
        if not term:
            return ""
        norm = term.strip().lower()
        return self.synonym_map.get(norm, norm)
