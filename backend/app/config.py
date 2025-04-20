import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL   = os.getenv("DATABASE_URL", "sqlite:///./test_db.sqlite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")


SCHEMA_INFO = """
Tables and Columns:

Customers(id, name, email, phone, address, join_date)
Products(id, name, description, price, stock, category_id)
Categories(id, name)
Orders(id, customer_id, order_date, status, total)
OrderItems(id, order_id, product_id, quantity, unit_price)
Shipping(id, order_id, method, shipping_date, delivery_date, tracking_number)
Reviews(id, product_id, customer_id, rating, comment, review_date)

Foreign Key Relationships:

- Products.category_id → Categories.id
- Orders.customer_id → Customers.id
- OrderItems.order_id → Orders.id
- OrderItems.product_id → Products.id
- Shipping.order_id → Orders.id
- Reviews.product_id → Products.id
- Reviews.customer_id → Customers.id
"""