drop table if exists Fulfillment cascade;
CREATE TABLE if not exists Fulfillment (
    user_id INT REFERENCES Users(user_id),
    order_id INT REFERENCES Orders(order_id),
    fulfillment_status VARCHAR not null check(fulfillment_status in ('ordered', 'shipped', 'delivered')) 
);