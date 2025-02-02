import psycopg2
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
    print(f"Loaded .env file: {env_file}")
else:
    print("No .env file found. Using system environment variables or defaults.")

# Get database details from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def create_database():
    try:
        # Connect to PostgreSQL (default database)
        connection = psycopg2.connect(
            dbname="postgres",  
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # auto-commit mode
        connection.autocommit = True  

        cursor = connection.cursor()

        # Check if the database already exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        # Close connection
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error creating database: {e}")

def create_table():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # SQL query to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS xkcd_comics (
            comic_id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            img_url VARCHAR(500) NOT NULL,
            alt_text TEXT,
            date_published DATE NOT NULL
        );
        """
        cursor.execute(create_table_query)
        connection.commit()

        print("XKCD Comics table created successfully.")

        # Close connection
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    
    # Create the database
    create_database() 

    # Create the table 
    create_table()  
