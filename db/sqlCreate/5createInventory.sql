drop table if exists Inventory cascade;
CREATE TABLE if not exists Inventory (
    user_id INT REFERENCES Users(user_id),
    product_id INT REFERENCES Products(product_id),
    quantity INT NOT NULL
);