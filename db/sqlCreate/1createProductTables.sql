--Product Tables (Advaita)

DROP TABLE IF EXISTS Products cascade;

CREATE TABLE IF NOT EXISTS Products (
    product_id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    description VARCHAR(4096) UNIQUE,
    category VARCHAR(255) NOT NULL,
    image varbinary(max)
);