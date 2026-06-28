from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
from datetime import date
from typing import List

class UserCreate(BaseModel):
    
    username: str = Field(
        min_length=3,
        max_length=30
    )
    name: str
    email: EmailStr
    password: str = Field(
        min_length=8
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Please enter a valid email address")
        return value


class UserResponse(BaseModel):

    id: int
    username: str
    name: str
    email: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str
    name: str
    email: str

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CategoryCreate(BaseModel):
    name: str
    type: Literal["Income", "Expense"]


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):

    category_id: int
    amount: float
    description: str
    transaction_date: date


class TransactionUpdate(BaseModel):

    category_id: int
    amount: float
    description: str
    transaction_date: date

class TransactionCategory(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True
        
class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    transaction_date: date

    category: TransactionCategory

    class Config:
        from_attributes = True

class MonthlySummaryResponse(BaseModel):
    month: str
    total_income: float
    total_expense: float
    balance: float

class CategorySummaryResponse(BaseModel):
    category_id: int
    category_name: str
    total_amount: float

class RecentTransactionResponse(BaseModel):
    id: int
    category: str
    type: str
    amount: float
    description: str
    transaction_date: date

class TransactionListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    transactions: List[TransactionResponse]

class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float

    total_transactions: int

    average_income: float
    average_expense: float

    highest_income: float
    highest_expense: float

    income_this_month: float
    expense_this_month: float

    transactions_this_month: int
    transactions_today: int