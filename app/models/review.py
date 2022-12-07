from flask import current_app as app

# This is the product review class with backend functions to 
# get data from the database or update data in the database
class Review:
    def __init__(self, id, uid, pid, review_time, review_content, review_rating, review_image):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.review_time = review_time
        self.review_content = review_content
        self.review_rating = review_rating
        self.review_image = review_image

    # Function to get user id from the user email
    @staticmethod
    def user_email_to_id(user_email):
        rows = app.db.execute (
            """
            SELECT id
            FROM Users
            WHERE email = :user_email
            """,
            user_email=user_email
        )
        return rows[0][0]

    # Function to get all product reviews mapped to a user id given a user id
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE uid = :uid
            ORDER BY review_time DESC
            ''',
            uid=uid
        )
        return [Review(*row) for row in rows]

    # Function to get all product reviews mapped to a product id given a product id
    @staticmethod
    def get_all_by_pid(pid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE pid = :pid
            ORDER BY review_time DESC
            ''',
            pid=pid
        )
        return [Review(*row) for row in rows]
    
    # Function to get a single product review mapped to a product and user given a review id
    @staticmethod
    def get_all_by_id(review_id):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE id = :review_id
            ''',
            review_id=review_id
        )
        return [Review(*row) for row in rows]
    
    # Function to give the number of reviews given a product id and a user id
    @staticmethod
    def review_exists_check(uid, pid):
        rows = app.db.execute (
            '''
            SELECT COUNT(*)
            FROM Review
            WHERE pid = :pid AND uid = :uid
            ''',
            pid=pid,
            uid=uid
        )
        return rows[0][0] # This is the count (number) of reviews where pid = pid and uid = uid
    
    # Function to give the review given a uid and pid
    @staticmethod
    def get_review(uid, pid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE pid = :pid AND uid = :uid
            ''',
            pid=pid,
            uid=uid
        )
        return rows # This is the first review where pid = pid and uid = uid

    # Function that updates a existing review with new data
    @staticmethod
    def edit_review(product_id, user_id, new_review, new_rating, new_image = ""):
        app.db.execute (
            """
            UPDATE Review
            SET
                review_content = :new_review,
                review_rating = :new_rating,
                review_time = DATE_TRUNC('second', CURRENT_TIMESTAMP::timestamp),
                review_image = :new_image
            WHERE
                uid = :user_id AND pid = :product_id
            """,
            product_id=product_id,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating,
            new_image=new_image
        )
        return
    
    # Function that adds new product review given new data
    @staticmethod
    def add_review(product_id, user_id, new_review, new_rating, new_image = ""):
        app.db.execute (
            """
            INSERT INTO Review (uid, pid, review_time, review_content, review_rating, review_image)
            VALUES (:user_id, :product_id, DATE_TRUNC('second', CURRENT_TIMESTAMP::timestamp), :new_review, :new_rating, :new_image)
            """,
            product_id=product_id,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating,
            new_image=new_image
        )
        return
        
    # Function to delete existing reviews given a review_id
    @staticmethod
    def delete_review(review_id):
        app.db.execute (
            """
            DELETE FROM Review
            WHERE id = :review_id
            """,
            review_id=review_id
        )
        return

    # Function to update the average rating of a single product in the database
    @staticmethod
    def update_product_ratings(product_id = None):
        if (product_id == None):
            return
        else:
            app.db.execute (
                """
                UPDATE Products
                SET
                    avg_rating = (
                        SELECT AVG(review_rating)
                        FROM Review
                        WHERE pid = :product_id
                    )
                WHERE
                    id = :product_id
                """,
                product_id=product_id
            )
        return

    # Count how many reviews given a product_id
    @staticmethod
    def count_num_ratings(product_id = None):
        if (product_id == None):
            return 0
        else:
            row = app.db.execute (
                """
                SELECT COUNT(*)
                FROM Review
                WHERE
                    pid = :product_id
                """,
                product_id=product_id
            )
            return row[0][0] # return the count of reviews for a product id
        return 