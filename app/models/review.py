from flask import current_app as app


class Review:
    """
    This is just a TEMPLATE for Review, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, review_time, review_content, review_rating, review_image):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.review_time = review_time
        self.review_content = review_content
        self.review_rating = review_rating
        self.review_image = review_image

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