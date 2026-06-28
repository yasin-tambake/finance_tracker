from sqlalchemy import func, or_

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category, User, Transaction
from app.schemas import CategoryCreate, CategoryResponse
from app.auth import get_current_user
router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("Logged in user:", current_user.id)
    print("Category:", category.name)

    existing = db.query(Category).filter(
        func.lower(Category.name) == category.name.lower(),
        func.lower(Category.type) == category.type.lower(),
        Category.user_id == current_user.id
    ).first()

    print("Existing:", existing)

    if existing:
        print("Existing user_id:", existing.user_id)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category.name,
        type=category.type,
        user_id=current_user.id

    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.get("/",response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    categories = db.query(Category).filter(
        or_(
            Category.user_id == None,
            Category.user_id == current_user.id
        )
    ).all()

    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.name = category_data.name
    category.type = category_data.type

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    transaction_exists = db.query(Transaction).filter(
        Transaction.category_id == category.id
    ).first()

    if transaction_exists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category because transactions exist."
        )
    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }

@router.get(
    "/type/{category_type}",
    response_model=list[CategoryResponse]
)
def get_categories_by_type(
    category_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category_type = category_type.strip().capitalize()
    if category_type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid category type"
        )

    categories = db.query(Category).filter(
        func.lower(Category.type) == category_type.lower(),
        or_(
            Category.user_id == None,
            Category.user_id == current_user.id
        )
    ).all()

    return categories
