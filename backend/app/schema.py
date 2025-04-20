from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class NLQuery(BaseModel):
    query: str

class CustomersInDB(SQLModel, table=True):
    __tablename__ = "Customers"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    phone: Optional[str] = None
    address: Optional[str] = None
    join_date: datetime = Field(default_factory=datetime.utcnow)


class CategoriesInDB(SQLModel, table=True):
    __tablename__ = "Categories"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class ProductsInDB(SQLModel, table=True):
    __tablename__ = "Products"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: Optional[int] = Field(default=None, foreign_key="Categories.id")


class OrdersInDB(SQLModel, table=True):
    __tablename__ = "Orders"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="Customers.id")
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str
    total: float


class OrderItemsInDB(SQLModel, table=True):
    __tablename__ = "OrderItems"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="Orders.id")
    product_id: int = Field(foreign_key="Products.id")
    quantity: int
    unit_price: float


class ShippingInDB(SQLModel, table=True):
    __tablename__ = "Shipping"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="Orders.id")
    method: str
    shipping_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    tracking_number: Optional[str] = None


class ReviewsInDB(SQLModel, table=True):
    __tablename__ = "Reviews"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="Products.id")
    customer_id: int = Field(foreign_key="Customers.id")
    rating: int
    comment: Optional[str] = None
    review_date: datetime = Field(default_factory=datetime.utcnow)
