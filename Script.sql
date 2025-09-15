CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER NULL REFERENCES category(id) ON DELETE cascade -- Для подкатегорий
);

CREATE INDEX idx_category_parent_id ON category(parent_id);

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0), -- Количество
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0), -- Цена
    category_id INTEGER NOT NULL REFERENCES category(id) -- Категория товара
);

CREATE INDEX idx_product_category_id ON product(category_id);

CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL
);

CREATE TABLE "order" (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES client(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_client_id ON "order"(client_id);

CREATE INDEX idx_order_created_at ON "order"(created_at);

CREATE TABLE order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES "order"(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (order_id, product_id) -- Проверка на уникальность, чтобы избежать дублирования товаров в заказе
);

CREATE INDEX idx_order_item_order_id ON order_item(order_id);

CREATE INDEX idx_order_item_product_id ON order_item(product_id);

SELECT 
    c.name AS "Наименование клиента",
    SUM(oi.quantity * p.price) AS "Сумма"  -- Берем цену из product!
FROM client c
INNER JOIN "order" o ON o.client_id = c.id
INNER JOIN order_item oi ON oi.order_id = o.id
INNER JOIN product p ON p.id = oi.product_id  -- Добавляем JOIN к product
GROUP BY c.id, c.name;

SELECT 
    parent.name AS "Категория",
    COUNT(child.id) AS "Количество прямых потомков"
FROM category parent
LEFT JOIN category child ON child.parent_id = parent.id
GROUP BY parent.id, parent.name;

CREATE VIEW top_5_products_last_month AS
SELECT 
    p.name AS "Наименование товара",
    root_cat.root_category_name AS "Категория 1-го уровня",
    SUM(oi.quantity) AS "Общее количество проданных штук"
FROM order_item oi
INNER JOIN "order" o ON o.id = oi.order_id
INNER JOIN product p ON p.id = oi.product_id
-- Нахождения корневой категории каждого товара
INNER JOIN (
    WITH RECURSIVE category_path AS (
        SELECT id, parent_id, name, name AS root_name
        FROM category
        WHERE parent_id IS NULL
        UNION ALL
        SELECT c.id, c.parent_id, c.name, cp.root_name
        FROM category c
        INNER JOIN category_path cp ON c.parent_id = cp.id
    )
    SELECT id, root_name AS root_category_name FROM category_path
) root_cat ON p.category_id = root_cat.id
WHERE o.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') -- Рамки для предыдущего месяца
  AND o.created_at < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.id, p.name, root_cat.root_category_name
ORDER BY "Общее количество проданных штук" DESC
LIMIT 5;

SELECT * FROM top_5_products_last_month;
SELECT * FROM order_item;

INSERT INTO category (name, parent_id) VALUES
('Электроника', NULL),
('Одежда', NULL),
('Смартфоны', 1),
('Ноутбуки', 1),
('Мужская одежда', 2);

-- Добавляем товары
INSERT INTO product (name, quantity, price, category_id) VALUES
('iPhone 15 Pro', 10, 99999.99, 3),
('Samsung Galaxy S23', 15, 79999.99, 3),
('MacBook Pro', 5, 149999.99, 4),
('Футболка хлопковая', 100, 1999.99, 5),
('Джинсы', 50, 3999.99, 5);

-- Добавляем клиентов
INSERT INTO client (name, address) VALUES
('Иван Иванов', 'Москва, ул. Примерная, д. 1'),
('Петр Петров', 'Санкт-Петербург, Невский пр., д. 100');

INSERT INTO "order" (client_id, created_at) VALUES 
(1, '2025-08-24 00:00:00'),
(2, '2025-08-25 00:00:00');


INSERT INTO order_item  (order_id, product_id, quantity) VALUES
(1, 1, 2),
(2, 3, 1),
(2, 4, 3);

drop view top_5_products_last_month;
drop table order_item;
drop table "order";
drop table client;
drop table product;
drop table category;