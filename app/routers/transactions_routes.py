from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, Category, User
from app.schemas import (
    TransactionCreate,
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


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    return transactions


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