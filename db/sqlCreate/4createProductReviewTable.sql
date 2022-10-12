-- Product Feedback (Aaric)
CREATE TABLE ProductReviews (
    user_id INT NOT NULL,
	product_id INT NOT NULL,
	rating INT NOT NULL CONSTRAINT rating_limit CHECK (rating BETWEEN 1 AND 5),
	review VARCHAR NOT NULL,
	FOREIGN KEY (user_id) REFERENCES User(user_id),
	FOREIGN KEY (user_id) REFERENCES Purchases(product_id)
);