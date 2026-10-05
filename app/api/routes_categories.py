from fastapi import APIRouter, HTTPException, Depends
from app.schemas.category import CategoryRecord, DepartmentRecord
from app.classification.taxonomy import TaxonomyManager

router = APIRouter(prefix="/api/v1", tags=["Taxonomy & Departments"])

_taxonomy = TaxonomyManager()

@router.get("/categories", response_model=list[CategoryRecord])
def get_categories():
    return _taxonomy.get_all_categories()

@router.get("/categories/{category_id}", response_model=CategoryRecord)
def get_category(category_id: str):
    cat = _taxonomy.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found.")
    return cat

@router.get("/departments", response_model=list[DepartmentRecord])
def get_departments():
    return _taxonomy.get_all_departments()
