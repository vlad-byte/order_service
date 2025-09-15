from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"))
    children = relationship("Category", backref="parent", remote_side=[id])


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category")
    order_items = relationship("OrderItem", back_populates="product")


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String, nullable=False)
    orders = relationship("Order", back_populates="client")


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    __table_args__ = (CheckConstraint('quantity > 0', name='check_quantity_positive'),)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")