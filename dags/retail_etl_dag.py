from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
import pandas as pd
import logging

# Define default arguments
default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'retail_sales_etl',
    default_args=default_args,
    description='ETL pipeline for retail sales data',
    schedule_interval='@daily',
    start_date=datetime(2024, 3, 1),
    catchup=False,
    tags=['retail', 'etl'],
    doc_md="""
    # Retail Sales ETL Pipeline
    
    This DAG implements an ETL pipeline that processes retail sales data from two sources:
    1. Online sales data from PostgreSQL
    2. In-store sales data from CSV
    
    The pipeline combines these data sources, performs necessary transformations,
    and loads the aggregated results into a MySQL data warehouse for analysis.
    """ ,
    is_paused_upon_creation=False
)

# Task 1: Extract data from PostgreSQL
def extract_postgres_data(**kwargs):
    """
    Extract ALL sales data from PostgreSQL database.
    Date filtering removed for full refresh.
    """
    # Get execution date from context for logging/naming purposes only
    execution_date = kwargs['ds'] # Keep for filename consistency
    logging.info(f"Extracting ALL PostgreSQL data (run triggered for logical date: {execution_date})")

    # Connect to PostgreSQL using hook
    pg_hook = PostgresHook(postgres_conn_id='postgres_conn')
    conn = pg_hook.get_conn()

    # Query to extract ALL data (removed WHERE clause)
    query = """
    SELECT product_id, quantity, sale_amount, sale_date
    FROM online_sales
    """

    # Execute query and load results into DataFrame
    df = pd.read_sql(query, conn) # Removed params argument
    logging.info(f"Extracted {len(df)} total rows from PostgreSQL")

    # Close connection
    conn.close()

    # Save to a temporary file for the next task (use ds_nodash for uniqueness if needed)
    temp_file_path = f"/opt/airflow/data/postgres_extract_{kwargs['ds_nodash']}.csv"
    df.to_csv(temp_file_path, index=False)

    return temp_file_path

extract_postgres = PythonOperator(
    task_id='extract_online_sales',
    python_callable=extract_postgres_data,
    provide_context=True,
    dag=dag,
)

# Task 2: Extract data from CSV
def extract_csv_data(**kwargs):
    """
    Extract ALL in-store sales data from CSV file.
    Date filtering removed for full refresh.
    """
    # Get execution date from context for logging/naming purposes only
    execution_date = kwargs['ds'] # Keep for filename consistency
    logging.info(f"Extracting ALL CSV data (run triggered for logical date: {execution_date})")

    # CSV path (mounted in docker-compose)
    csv_path = '/opt/airflow/data/instore_sales.csv'

    # Read CSV
    df = pd.read_csv(csv_path)
    logging.info(f"Extracted {len(df)} total rows from CSV")

    # Save to a temporary file for the next task (use ds_nodash for uniqueness if needed)
    temp_file_path = f"/opt/airflow/data/csv_extract_{kwargs['ds_nodash']}.csv"
    df.to_csv(temp_file_path, index=False)

    return temp_file_path

extract_csv = PythonOperator(
    task_id='extract_instore_sales',
    python_callable=extract_csv_data,
    provide_context=True,
    dag=dag,
)

# Task 3: Transform and combine data
def transform_data(**kwargs):
    """
    Combine data from both sources, clean it, and aggregate by product
    """
    # Get execution date from context
    execution_date = kwargs['ds']
    logging.info(f"Transforming data for date: {execution_date}")
    
    # Get file paths from previous tasks using XCom
    ti = kwargs['ti']
    postgres_file = ti.xcom_pull(task_ids='extract_online_sales')
    csv_file = ti.xcom_pull(task_ids='extract_instore_sales')
    
    # Load data from both sources
    postgres_df = pd.read_csv(postgres_file)
    csv_df = pd.read_csv(csv_file)
    
    # Data validation and type conversion
    for df in [postgres_df, csv_df]:
        # Convert product_id to numeric, errors will become NaN
        df['product_id'] = pd.to_numeric(df['product_id'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['sale_amount'] = pd.to_numeric(df['sale_amount'], errors='coerce')
    
    # Combine data sources
    combined_df = pd.concat([postgres_df, csv_df], ignore_index=True)
    logging.info(f"Combined data: {len(combined_df)} rows")
    
    # Data cleansing - remove nulls and invalid entries
    before_cleaning = len(combined_df)
    cleaned_df = combined_df.dropna(subset=['product_id', 'quantity', 'sale_amount'])
    after_cleaning = len(cleaned_df)
    logging.info(f"Removed {before_cleaning - after_cleaning} rows with null values")
    
    # Data aggregation by product_id
    aggregated_df = cleaned_df.groupby('product_id').agg({
        'quantity': 'sum',
        'sale_amount': 'sum'
    }).reset_index()
    
    # Rename columns to match target schema
    aggregated_df.columns = ['product_id', 'total_quantity', 'total_sale_amount']
    logging.info(f"Aggregated data: {len(aggregated_df)} unique products")
    
    # Save transformed data
    transformed_file_path = f"/opt/airflow/data/transformed_sales_{execution_date}.csv"
    aggregated_df.to_csv(transformed_file_path, index=False)
    
    return transformed_file_path

transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

# Task 4: Load data to MySQL
def load_to_mysql(**kwargs):
    """
    Load transformed data into MySQL data warehouse.
    Clears the table before loading for a full refresh.
    """
    # Get execution date from context for logging
    execution_date = kwargs['ds'] # Keep for logging
    logging.info(f"Loading transformed data to MySQL (run triggered for logical date: {execution_date})")

    # Get transformed data file path
    ti = kwargs['ti']
    transformed_file = ti.xcom_pull(task_ids='transform_data')

    # Read the transformed data
    df = pd.read_csv(transformed_file)

    # Connect to MySQL using hook
    mysql_hook = MySqlHook(mysql_conn_id='mysql_conn')
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()

    try:
        # Create database and table if they don't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS retail_data_warehouse")
        cursor.execute("USE retail_data_warehouse")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_aggregated (
            product_id INT PRIMARY KEY,
            total_quantity INT,
            total_sale_amount DECIMAL(10, 2)
        )
        """)

        # <<< ADDED: Clear the table before inserting new data >>>
        logging.info("Truncating sales_aggregated table before loading...")
        cursor.execute("TRUNCATE TABLE sales_aggregated;")
        logging.info("Table truncated.")
        # <<< END ADDED PART >>>

        # Insert or update data using UPSERT pattern
        # (Note: With TRUNCATE, a simple INSERT would also work,
        # but UPSERT is harmless here and handles potential edge cases if TRUNCATE failed)
        logging.info(f"Inserting/Updating {len(df)} aggregated records...")
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO sales_aggregated (product_id, total_quantity, total_sale_amount)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_quantity = VALUES(total_quantity),
            total_sale_amount = VALUES(total_sale_amount)
            """, (
                int(row['product_id']),
                int(row['total_quantity']),
                float(row['total_sale_amount'])
            ))

        # Commit changes
        conn.commit()
        logging.info(f"Successfully loaded {len(df)} records to MySQL")

    except Exception as e:
        # Log error and rollback
        logging.error(f"Error loading data to MySQL: {str(e)}")
        conn.rollback()
        raise

    finally:
        # Close connections
        cursor.close()
        conn.close()

    return f"Loaded {len(df)} total aggregated records."

load_data = PythonOperator(
    task_id='load_data_to_mysql',
    python_callable=load_to_mysql,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
extract_postgres >> transform
extract_csv >> transform >> load_data