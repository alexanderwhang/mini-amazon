--User Tables (Albert)
drop table if exists Purchases;
drop table if exists Sellers;



CREATE TABLE if not exists Purchases (
    order_id INT NOT NULL REFERENCES Orders(order_id),
    pid INT NOT NULL REFERENCES Products(product_id),
    quantity INT NOT NULL CHECK(quantity >= 0),
    fulfillment_status VARCHAR not null check(fulfillment_status in ('ordered', 'shipped', 'delivered')) 
);

CREATE TABLE if not exists Sellers (
    user_id INT NOT NULL REFERENCES Users(user_id)
);
