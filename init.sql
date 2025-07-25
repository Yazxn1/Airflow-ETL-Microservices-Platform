CREATE TABLE
    IF NOT EXISTS online_sales (
        sale_id SERIAL PRIMARY KEY,
        product_id INT,
        quantity INT,
        sale_amount DECIMAL(10, 2),
        sale_date DATE
    );

INSERT INTO
    online_sales (product_id, quantity, sale_amount, sale_date)
VALUES
    -- March 1st data
    (101, 5, 99.95, '2024-03-01'),
    (102, 3, 74.97, '2024-03-01'),
    (103, 2, 49.98, '2024-03-01'),
    (104, 7, 174.93, '2024-03-01'),
    (105, 1, 29.99, '2024-03-01'),
    (106, 4, 119.96, '2024-03-01'),
    (107, 2, 59.98, '2024-03-01'),
    (108, 6, 149.94, '2024-03-01'),
    (109, 3, 89.97, '2024-03-01'),
    (110, 1, 19.99, '2024-03-01'),
    (111, 5, 124.95, '2024-03-01'),
    (112, 2, 59.98, '2024-03-01'),
    (113, 3, 74.97, '2024-03-01'),
    (114, 4, 99.96, '2024-03-01'),
    (115, 1, 34.99, '2024-03-01'),
    (116, 3, 59.97, '2024-03-01'),
    (117, 2, 44.98, '2024-03-01'),
    -- March 2nd data
    (101, 3, 59.97, '2024-03-02'),
    (102, 2, 49.98, '2024-03-02'),
    (103, 5, 124.95, '2024-03-02'),
    (104, 1, 24.99, '2024-03-02'),
    (105, 4, 119.96, '2024-03-02'),
    (106, 2, 59.98, '2024-03-02'),
    (107, 6, 179.94, '2024-03-02'),
    (108, 3, 74.97, '2024-03-02'),
    (109, 1, 29.99, '2024-03-02'),
    (110, 4, 79.96, '2024-03-02'),
    (111, 2, 49.98, '2024-03-02'),
    (112, 3, 89.97, '2024-03-02'),
    (113, 5, 124.95, '2024-03-02'),
    (114, 1, 24.99, '2024-03-02'),
    (115, 3, 104.97, '2024-03-02'),
    (116, 2, 39.98, '2024-03-02'),
    -- March 3rd data
    (101, 2, 39.98, '2024-03-03'),
    (102, 5, 124.95, '2024-03-03'),
    (103, 3, 74.97, '2024-03-03'),
    (104, 4, 99.96, '2024-03-03'),
    (105, 2, 59.98, '2024-03-03'),
    (106, 3, 89.97, '2024-03-03'),
    (107, 1, 29.99, '2024-03-03'),
    (108, 5, 124.95, '2024-03-03'),
    (109, 2, 59.98, '2024-03-03'),
    (110, 3, 59.97, '2024-03-03'),
    (111, 4, 99.96, '2024-03-03'),
    (112, 1, 29.99, '2024-03-03'),
    (113, 2, 49.98, '2024-03-03'),
    (114, 3, 74.97, '2024-03-03'),
    (115, 4, 139.96, '2024-03-03'),
    (116, 2, 79.98, '2024-03-03'),
    (117, 3, 67.47, '2024-03-03'),
    -- Add some null values for testing data cleansing
    (101, NULL, 39.98, '2024-03-03'),
    (102, 2, NULL, '2024-03-03'),
    (NULL, 3, 74.97, '2024-03-03');