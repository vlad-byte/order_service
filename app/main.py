import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from contextlib import asynccontextmanager
from . import models, schemas, database
from .database import get_db


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_tables()
    print("Таблицы созданы")
    yield
    print("Ошибка создания таблиц")

app = FastAPI(
    title="Order Service API",
    description="REST API для управления заказами",
    version="1.0.0",
    lifespan=lifespan
)


@app.post(
    "/orders/{order_id}/items",
    response_model=schemas.OrderItemResponse,
    responses={
        404: {"model": schemas.ErrorResponse, "description": "Заказ или товар не найден"},
        400: {"model": schemas.ErrorResponse, "description": "Недостаточно товара на складе"},
        500: {"model": schemas.ErrorResponse, "description": "Ошибка базы данных"}
    }
)
def add_item_to_order(
        order_id: int,
        request: schemas.AddItemRequest,
        db: Annotated[Session, Depends(get_db)]
):
    # 1. Находим заказ и проверяем его существование
    db_order = db.get(models.Order, order_id)
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )

    # 2. Находим товар и проверяем его существование и наличие
    db_product = db.get(models.Product, request.product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {request.product_id} не найден"
        )

    if db_product.quantity < request.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно товара на складе. Доступно: {db_product.quantity}, запрошено: {request.quantity}"
        )

    # 3. Ищем существующую позицию в заказе
    existing_item = next(
        (item for item in db_order.items if item.product_id == request.product_id),
        None
    )

    # 4. Если товар уже есть в заказе то увеличиваем количество
    if existing_item:
        existing_item.quantity += request.quantity
        order_item = existing_item
    else:
        # 5. Если нет тто создаем новую позицию
        order_item = models.OrderItem(
            order_id=order_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        db.add(order_item)

    # 6. Резервируем товар на складе
    db_product.quantity -= request.quantity

    # 7. Сохраняем изменения
    try:
        db.commit()
        db.refresh(order_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )

    return order_item