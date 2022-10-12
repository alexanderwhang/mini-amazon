\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(user_id)+1 FROM Users),
                         false);
                         
\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                    (SELECT MAX(order_id)+1 FROM Orders),
                    false);    
                    
\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
