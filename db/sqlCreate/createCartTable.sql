--Cart Table (Alex)

drop table if exists Cart;
CREATE TABLE if not exists Cart (
    user_id INT NOT NULL REFERENCES Users (user_id),
	product_id INT NOT NULL REFERENCES Products (product_id),
    seller_id INT NOT NULL REFERENCES Users (user_id),
    quantity INT NOT NULL
);