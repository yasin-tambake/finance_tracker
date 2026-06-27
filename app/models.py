from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import DECIMAL
from sqlalchemy import Date
from sqlalchemy import text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)

    username = Column(String(30),unique=True,nullable=False)

    name = Column(String(100),nullable=False)

    email = Column(String(100),unique=True,nullable=False)

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    categories = relationship("Category", back_populates="user")
    transactions = relationship("Transaction",back_populates="user"
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    type = Column(String(20), nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer,primary_key=True,index=True)

    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)

    category_id = Column(Integer,ForeignKey("categories.id"),nullable=False)

    amount = Column(DECIMAL(10, 2),nullable=False)

    description = Column(String(255))

    transaction_date = Column(Date,nullable=False)

    user = relationship(
        "User",
        back_populates="transactions"
    )

    category = relationship(
        "Category",
        back_populates="transactions"
    )