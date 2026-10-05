import os
import yaml
from app.schemas.category import CategoryRecord, DepartmentRecord, TaxonomyConfig

class TaxonomyManager:
    def __init__(self, config_path: str = "configs/taxonomy.yaml"):
        self.config_path = config_path
        self.categories: dict[str, CategoryRecord] = {}
        self.departments: dict[str, DepartmentRecord] = {}
        self.category_prototypes: list[tuple[str, str]] = []
        self.load_taxonomy()

    def load_taxonomy(self) -> None:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                for dept_data in data.get("departments", []):
                    dept = DepartmentRecord(**dept_data)
                    self.departments[dept.id] = dept

                for cat_data in data.get("categories", []):
                    cat = CategoryRecord(**cat_data)
                    self.categories[cat.id] = cat
                    for proto in cat.prototypes:
                        self.category_prototypes.append((cat.id, proto))

    def get_category(self, category_id: str) -> CategoryRecord | None:
        return self.categories.get(category_id)

    def get_department(self, department_id: str) -> DepartmentRecord | None:
        return self.departments.get(department_id)

    def get_all_categories(self) -> list[CategoryRecord]:
        return list(self.categories.values())

    def get_all_departments(self) -> list[DepartmentRecord]:
        return list(self.departments.values())
