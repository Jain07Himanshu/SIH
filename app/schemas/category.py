from pydantic import BaseModel, Field

class CategoryRecord(BaseModel):
    id: str
    name: str
    department_id: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    prototypes: list[str] = Field(default_factory=list)

class DepartmentRecord(BaseModel):
    id: str
    name: str
    description: str = ""
    contact_email: str | None = None

class CategoryPrediction(BaseModel):
    category_id: str
    category_name: str
    confidence: float = 0.50
    department_id: str = ""
    department_name: str = ""
    explanation: str = ""

class TaxonomyConfig(BaseModel):
    categories: list[CategoryRecord] = Field(default_factory=list)
    departments: list[DepartmentRecord] = Field(default_factory=list)
