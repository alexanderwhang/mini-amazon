\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.carts_id_seq',
                         (SELECT MAX(id)+1 FROM Carts),
                         false);

<<<<<<< HEAD
\COPY Saved FROM 'Save.csv' WITH DELIMITER ',' NULL '' CSV
=======
\COPY Saved FROM 'Save.csv' WITH DELIMITER ',' NULL '' CSV
>>>>>>> c0b8a13f27f6800b5bf2dbab72eec3b08de768b4
