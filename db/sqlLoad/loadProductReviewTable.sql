\COPY Review FROM 'Review.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.review_id_seq',
                         (SELECT MAX(id)+1 FROM Review),
                         false);