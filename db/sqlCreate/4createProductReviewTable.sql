-- Product Feedback (Aaric)
CREATE TABLE ProductReviews (
    user_id INT NOT NULL REFERENCES Users (user_id),
	product_id INT NOT NULL REFERENCES Purchases (product_id),
	rating INT NOT NULL CONSTRAINT rating_limit CHECK (rating BETWEEN 1 AND 5),
	review VARCHAR NOT NULL
);