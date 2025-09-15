import requests
import json

BASE_URL = "http://localhost:8000"


def test_add_item(order_id, product_id, quantity):
    url = f"{BASE_URL}/orders/{order_id}/items"
    data = {"product_id": product_id, "quantity": quantity}

    try:
        response = requests.post(url, json=data)
        print(f"Заказ {order_id}, Товар {product_id}, Количество {quantity}:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 50)


# Тестовые сценарии
test_cases = [
    (1, 1, 2),  # Успешное добавление
    (1, 2, 1),  # Добавление другого товара
    (1, 1, 1),  # Увеличение количества
    (1, 1, 100),  # Ошибка недостаточно товара
    (1, 999, 1),  # Ошибка несуществующий товар
    (999, 1, 1),  # Ошибка несуществующий заказ
]

for order_id, product_id, quantity in test_cases:
    test_add_item(order_id, product_id, quantity)