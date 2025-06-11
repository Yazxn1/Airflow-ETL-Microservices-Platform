-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS retail_data_warehouse;

-- Switch to the database
USE retail_data_warehouse;

-- Create the sales_aggregated table if it doesn't exist
CREATE TABLE
    IF NOT EXISTS sales_aggregated (
        product_id INT PRIMARY KEY,
        total_quantity INT,
        total_sale_amount DECIMAL(10, 2)
    );