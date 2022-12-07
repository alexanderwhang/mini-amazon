from flask import current_app as app

class Purchase:
    def __init__(self, order_id, product_name, product_price, quantity, total_price, fulfillment_status, sellerid, time_stamp=None):
        self.order_id = order_id
        self.product_name = product_name #from product
        self.product_price= product_price #from product
        self.quantity = quantity
        self.total_price = total_price #calc'd from product
        self.fulfillment_status = fulfillment_status
        self.sellerid = sellerid # From Products
        self.time_stamp = time_stamp

    #method for getting a user's purchase history. returns a list of Purchase objects
    @staticmethod
    def get_all_purchases_by_user(user_id, datefilter=None,sortby=None,keyword=None):
        interval = "" #finds all historic purchases by default
        keywordSearch = "" #finds all purchases by default
        orderby = "order by time_stamp DESC" #order by time stamp desc by default

        #translating the datefilter type to sql
        if datefilter is not None:
            if datefilter=='month':
                interval = "and time_stamp >= current_date - interval '1 months'"
            elif datefilter=='3month':
                interval = "and time_stamp >= current_date - interval '3 months'"
            elif datefilter=='year':
                interval = "and time_stamp >= current_date - interval '1 years'"

        #translating the sortby type to sql
        if sortby is not None:
            if sortby=='time':
                orderby = "order by time_stamp DESC"
            elif sortby=='fulfillment':
                orderby = """order by CASE
                            WHEN fulfillment_status = 'ordered' then 1
                            WHEN fulfillment_status = 'shipped' then 2 
                            WHEN fulfillment_status = 'delivered' then 3
                            END DESC"""
            elif sortby=='productName':
                orderby = "order by product_name ASC"
            elif sortby=='sellerID':
                orderby = "order by sellerid ASC"
            elif sortby=='price':
                orderby = "order by product_price DESC"
            elif sortby=='totalPrice':
                orderby = "order by total_price DESC"

        #when user has entered a keyword to search, add an additional where clause
        if keyword is not None:
            rows = app.db.execute(f'''
            with userOrders as (
                SELECT id as order_id, time_stamp
                from Orders
                WHERE user_id = :user_id
                {interval}
            )
            select 
                userOrders.order_id as order_id, 
                Products.name as product_name, 
                Products.price as product_price, 
                Purchases.quantity as quantity, 
                Purchases.quantity*Products.price as total_price,
                Purchases.fulfillment_status as fulfillment_status,
                Products.user_id as sellerid,
                userOrders.time_stamp as time_stamp
            from 
                userOrders, 
                Products, 
                Purchases
            where 
                Purchases.order_id = userOrders.order_id
                and Purchases.pid = Products.id
                and (lower(Products.name) like lower(:keyword))

            {orderby}
            ''',
                                user_id=user_id, keyword=f"%{keyword}%")
        else:#when user has not entered a keyword to search, no additional where clause
            rows = app.db.execute(f'''
            with userOrders as (
                SELECT id as order_id, time_stamp
                from Orders
                WHERE user_id = :user_id
                {interval}
            )
            select 
                userOrders.order_id as order_id, 
                Products.name as product_name, 
                Products.price as product_price, 
                Purchases.quantity as quantity, 
                Purchases.quantity*Products.price as total_price,
                Purchases.fulfillment_status as fulfillment_status,
                Products.user_id as sellerid,
                userOrders.time_stamp as time_stamp
            from 
                userOrders, 
                Products, 
                Purchases
            where 
                Purchases.order_id = userOrders.order_id
                and Purchases.pid = Products.id
                {orderby}
            ''',
                                user_id=user_id)
        return [Purchase(*row) for row in rows]

    
    @staticmethod
    def user_email_to_id(user_email):
        rows = app.db.execute(
            """
            SELECT id
            FROM Users
            WHERE email = :user_email
            """,
            user_email=user_email
        )
        return rows[0][0]

    #method for getting all purchases of a given order. returns a list of Purchase objects
    @staticmethod
    def get_all_purchases_by_order(order_id):
        rows = app.db.execute('''
select 
    order_id as order_id, 
    Products.name as product_name, 
    Products.price as product_price, 
    Purchases.quantity as quantity, 
    Purchases.quantity*Products.price as total_price,
    Purchases.fulfillment_status as fulfillment_status,
    Products.user_id as sellerid
from 
    Products, 
    Purchases
where 
    Purchases.order_id = :order_id
    and Purchases.pid = Products.id
''',
                              order_id=order_id)
        return [Purchase(*row) for row in rows]

class OrderPrice:
    def __init__(self, price):
        self.price = price

    @staticmethod
    def getPrice(oid):
        price = app.db.execute('''
SELECT SUM(Products.price * Purchases.quantity)
FROM Products, Purchases
WHERE Purchases.order_id = :oid
AND Purchases.pid = Products.id
''',
                              oid=oid)
        if str(*price[0]) == 'None':
            return "This order contains no items!"
        return price[0][0]
