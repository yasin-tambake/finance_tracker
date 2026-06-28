from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from math import ceil

from app.database import get_db
from app.models import Transaction, Category, User
from app.schemas import (
    TransactionCreate,
    TransactionListResponse,
    TransactionUpdate,
    TransactionResponse
)
from app.auth import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = db.query(Category).filter(
        Category.id == transaction.category_id,
        Category.user_id == current_user.id or Category.user_id == None
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    if transaction.transaction_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Transaction date cannot be in the future"
        )

    new_transaction = Transaction(
        user_id=current_user.id,
        category_id=category.id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date
    )


    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    search: str | None = None,
    category: str | None = None,
    type: str | None = None,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    sort: str = "date_desc",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = (
        db.query(Transaction)
        .join(Category)
        .filter(Transaction.user_id == current_user.id)
    )

    if search:
        query = query.filter(
            Transaction.description.ilike(f"%{search}%")
        )

    if category:
        query = query.filter(
            func.lower(Category.name) == category.lower()
        )

    if type:
        query = query.filter(
            func.lower(Category.type) == type.lower()
        )

    if from_date:
        query = query.filter(
            Transaction.transaction_date >= from_date
        )

    if to_date:
        query = query.filter(
            Transaction.transaction_date <= to_date
        )

    if sort == "amount_asc":
        query = query.order_by(Transaction.amount.asc())

    elif sort == "amount_desc":
        query = query.order_by(Transaction.amount.desc())

    elif sort == "date_asc":
        query = query.order_by(Transaction.transaction_date.asc())

    else:
        query = query.order_by(Transaction.transaction_date.desc())

    total = query.count()

    pages = ceil(total / limit) if total else 1

    transactions = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "transactions": transactions
    }


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


@router.put("/{transaction_id}",
            response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    category = db.query(Category).filter(
        Category.id == transaction_data.category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    transaction.category_id = (
        transaction_data.category_id
    )

    transaction.amount = (
        transaction_data.amount
    )

    transaction.description = (
        transaction_data.description
    )

    transaction.transaction_date = (
        transaction_data.transaction_date
    )

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }