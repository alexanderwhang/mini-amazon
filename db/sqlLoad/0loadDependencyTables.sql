\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);
                         
\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                    (SELECT MAX(id)+1 FROM Orders),
                    false);    
                    
\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Review FROM 'Review.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.review_id_seq',
                         (SELECT MAX(id)+1 FROM Review),
                         false);