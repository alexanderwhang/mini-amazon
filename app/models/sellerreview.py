from flask import current_app as app

# This is the seller review class with backend functions to 
# get data from the database or update data in the database
class SellerReview:
    def __init__(self, id, uid, sellerid, review_time, review_content, review_rating):
        self.id = id
        self.uid = uid
        self.sellerid = sellerid
        self.review_time = review_time
        self.review_content = review_content
        self.review_rating = review_rating

    # Function to get all seller reviews mapped to a user id given a user id
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM SellerReview
            WHERE uid = :uid
            ORDER BY review_time DESC
            ''',
            uid=uid
        )
        return [SellerReview(*row) for row in rows]

    # Function to give the number of reviews given a sellerid and a user id
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
    def can_user_review_seller(user_id, sellerid):
        product_ids = app.db.execute (
            """
            SELECT Products.id
            FROM Products
            WHERE user_id = :sellerid
            """,
            user_id = user_id,
            sellerid = sellerid
        )
        # print(product_ids[1][0]) product_ids[index][0] is every product_id that the sellerid sells
        products_this_user_bought = app.db.execute (
            """
            SELECT Purchases.pid
            FROM Purchases
            LEFT OUTER JOIN Orders on Purchases.order_id = Orders.id
            WHERE Orders.user_id = :user_id
            """,
            user_id = user_id,
            sellerid = sellerid
        )
        for product_id_arr in products_this_user_bought:
            for seller_product_id in product_ids:
                if product_id_arr[0] == seller_product_id[0]:
                    return True
        return False

    # Function to get all seller reviews mapped to a sellerid given a sellerid
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

    # Function that updates a existing review with new data
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

    # Function that adds new product review given new data
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

    # Function to delete existing reviews given a user_id and sellerid
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