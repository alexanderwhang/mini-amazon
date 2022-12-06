--User Tables (Albert)
drop table if exists Purchases;

CREATE TABLE if not exists Purchases (
    order_id INT NOT NULL REFERENCES Orders(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL CHECK(quantity >= 0),
    fulfillment_status VARCHAR not null check(fulfillment_status in ('ordered', 'shipped', 'delivered')) 
);

