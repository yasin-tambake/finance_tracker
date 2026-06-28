from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models import Transaction, Category, User
from app.schemas import DashboardSummary, MonthlySummaryResponse, RecentTransactionResponse, CategorySummaryResponse
from app.auth import get_current_user
from datetime import date

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/monthly",response_model=list[MonthlySummaryResponse])
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    monthly_summary = (
        db.query(
            func.date_format(
                Transaction.transaction_date,
                "%Y-%m"
            ).label("month"),

            func.coalesce(
                func.sum(
                    case(
                        (Category.type == "income", Transaction.amount),
                        else_=0
                    )
                ),
                0
            ).label("total_income"),

            func.coalesce(
                func.sum(
                    case(
                        (Category.type == "expense", Transaction.amount),
                        else_=0
                    )
                ),
                0
            ).label("total_expense"),

            func.coalesce(
                func.sum(
                    case(
                        (Category.type == "income", Transaction.amount),
                        else_=-Transaction.amount
                    )
                ),
                0
            ).label("balance")
        )
        .join(Category)
        .filter(
            Transaction.user_id == current_user.id
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    return monthly_summary

@router.get(
    "/recent",
    response_model=list[RecentTransactionResponse]
)
def get_recent_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    transactions = (
        db.query(
            Transaction.id,
            Category.name.label("category"),
            Category.type.label("type"),
            Transaction.amount,
            Transaction.description,
            Transaction.transaction_date
        )
        .join(Category)
        .filter(
            Transaction.user_id == current_user.id
        )
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc()
        )
        .limit(5)
        .all()
    )

    return transactions

@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    today = date.today()

    current_month = today.month
    current_year = today.year

    transactions = (
        db.query(Transaction)
        .join(Category)
        .filter(Transaction.user_id == current_user.id)
    )

    total_income = (
        transactions
        .filter(Category.type == "income")
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    total_expense = (
        transactions
        .filter(Category.type == "expense")
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    total_transactions = (
        transactions.count()
    )

    average_income = (
        transactions
        .filter(Category.type == "income")
        .with_entities(func.coalesce(func.avg(Transaction.amount), 0))
        .scalar()
    )

    average_expense = (
        transactions
        .filter(Category.type == "expense")
        .with_entities(func.coalesce(func.avg(Transaction.amount), 0))
        .scalar()
    )

    highest_income = (
        transactions
        .filter(Category.type == "income")
        .with_entities(func.coalesce(func.max(Transaction.amount), 0))
        .scalar()
    )

    highest_expense = (
        transactions
        .filter(Category.type == "expense")
        .with_entities(func.coalesce(func.max(Transaction.amount), 0))
        .scalar()
    )

    income_this_month = (
        transactions
        .filter(
            Category.type == "income",
            func.month(Transaction.transaction_date) == current_month,
            func.year(Transaction.transaction_date) == current_year
        )
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    expense_this_month = (
        transactions
        .filter(
            Category.type == "expense",
            func.month(Transaction.transaction_date) == current_month,
            func.year(Transaction.transaction_date) == current_year
        )
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )

    transactions_this_month = (
        transactions
        .filter(
            func.month(Transaction.transaction_date) == current_month,
            func.year(Transaction.transaction_date) == current_year
        )
        .count()
    )

    transactions_today = (
        transactions
        .filter(Transaction.transaction_date == today)
        .count()
    )

    return DashboardSummary(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,

        total_transactions=total_transactions,

        average_income=average_income,
        average_expense=average_expense,

        highest_income=highest_income,
        highest_expense=highest_expense,

        income_this_month=income_this_month,
        expense_this_month=expense_this_month,

        transactions_this_month=transactions_this_month,
        transactions_today=transactions_today
    )

@router.get("/monthly", response_model=list[MonthlySummaryResponse])
def monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    results = (
        db.query(
            func.date_format(
                Transaction.transaction_date,
                "%Y-%m"
            ).label("month"),

            func.sum(
                case(
                    (Category.type == "income", Transaction.amount),
                    else_=0
                )
            ).label("total_income"),

            func.sum(
                case(
                    (Category.type == "expense", Transaction.amount),
                    else_=0
                )
            ).label("total_expense")
        )
        .join(Category)
        .filter(Transaction.user_id == current_user.id)
        .group_by(
            func.date_format(
                Transaction.transaction_date,
                "%Y-%m"
            )
        )
        .order_by(
            func.date_format(
                Transaction.transaction_date,
                "%Y-%m"
            )
        )
        .all()
    )

    return [
        {
            "month": r.month,
            "total_income": float(r.total_income or 0),
            "total_expense": float(r.total_expense or 0),
            "balance": float((r.total_income or 0) - (r.total_expense or 0))
        }
        for r in results
    ]

@router.get(
    "/category-summary",
    response_model=list[CategorySummaryResponse]
)
def category_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    results = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.sum(Transaction.amount).label("total_amount")
        )
        .join(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return results