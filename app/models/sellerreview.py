from flask import current_app as app

class SellerReview:
    def __init__(self, id, uid, sellerid, review_time, review_content, review_rating):
        self.id = id
        self.uid = uid
        self.sellerid = sellerid
        self.review_time = review_time
        self.review_content = review_content
        self.review_rating = review_rating


    @staticmethod
    def review_exists_check(uid, sellerid):
        rows = app.db.execute (
            '''
            SELECT COUNT(*)
            FROM SellerReview
            WHERE sellerid = :sellerid AND uid = :uid
            ''',
            sellerid=sellerid,
            uid=uid
        )
        return rows[0][0] # This is the count (number) of reviews where sellerid = sellerid and uid = uid

    @staticmethod
    def get_all_seller_reviews(sellerid):
        rows = app.db.execute(
            """
            SELECT * 
            FROM SellerReview
            WHERE sellerid = :sellerid
            """,
            sellerid = sellerid
        )
        return [SellerReview(*row) for row in rows]

    @staticmethod
    def edit_seller_review(user_id, sellerid, new_review, new_rating):
        app.db.execute (
            """
            UPDATE SellerReview
            SET
                review_content = :new_review,
                review_rating = :new_rating,
                review_time = DATE_TRUNC('second', CURRENT_TIMESTAMP::timestamp)
            WHERE
                uid = :user_id AND sellerid = :sellerid
            """,
            sellerid=sellerid,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating
        )
        return

    @staticmethod
    def add_seller_review(user_id, sellerid, new_review, new_rating):
        app.db.execute (
            """
            INSERT INTO SellerReview (uid, sellerid, review_time, review_content, review_rating)
            VALUES (:user_id, :sellerid, DATE_TRUNC('second', CURRENT_TIMESTAMP::timestamp), :new_review, :new_rating)
            """,
            sellerid=sellerid,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating
        )
        return

    @staticmethod
    def delete_seller_review(user_id, sellerid):
        app.db.execute (
            """
            DELETE FROM SellerReview
            WHERE uid = :user_id and sellerid = :sellerid
            """,
            user_id = user_id,
            sellerid = sellerid
        )
        return