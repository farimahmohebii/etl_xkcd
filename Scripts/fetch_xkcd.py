from prefect import flow, task
import requests
import psycopg2
import logging
from datetime import date
import prefect
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
    print(f"Loaded .env file: {env_file}")
else:
    print("No .env file found. Using system environment variables or defaults.")

# Configure logging to capture both to stdout (for Prefect UI) and to a file
logger = logging.getLogger("prefect")

# Create handlers
file_handler = logging.FileHandler("fetch_xkcd.log")

# This captures logs for Prefect UI
console_handler = logging.StreamHandler() 

# Set logging level for both handlers
file_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to both handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Ensure global logging uses the logger
logging.basicConfig(level=logging.INFO)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# This function fetchs the latest XKCD comic from the API.
@task(retries=3, retry_delay_seconds=10)
def fetch_latest_comic():
    logger.info("Fetching latest XKCD comic...")
    try:
        response = requests.get("https://xkcd.com/info.0.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Fetched comic ID: {data['num']} - {data['title']}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch XKCD comic: {e}")
        raise

#This function retrieves the last stored XKCD comic ID from the database.
@task
def get_last_comic_id_in_db():
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(comic_id) FROM xkcd_comics;")
                result = cursor.fetchone()
                return result[0] if result and result[0] else None
    except Exception as e:
        logger.error(f"Error retrieving last comic ID from DB: {e}")
        return None

#This function fetchs and inserts missing XKCD comics from `start_id` to `end_id`.
@task
def fetch_and_insert_comics(start_id, end_id):
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                for comic_id in range(start_id, end_id - 1, -1):
                    try:
                        response = requests.get(f"https://xkcd.com/{comic_id}/info.0.json", timeout=10)
                        response.raise_for_status()
                        data = response.json()

                        # Extract comic details
                        title = data["title"]
                        img_url = data["img"]
                        alt_text = data["alt"]
                        date_published = date(int(data["year"]), int(data["month"]), int(data["day"]))

                        # Insert the comic into the database
                        insert_query = """
                        INSERT INTO xkcd_comics (comic_id, title, img_url, alt_text, date_published)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (comic_id) DO NOTHING;
                        """
                        cursor.execute(insert_query, (comic_id, title, img_url, alt_text, date_published))
                        connection.commit()

                        logger.info(f"Inserted comic '{title}' (ID: {comic_id}) into database.")
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Failed to fetch comic ID {comic_id}. Error: {e}")
                    except Exception as e:
                        logger.error(f"Error inserting comic ID {comic_id} into DB: {e}")
    except Exception as e:
        logger.error(f"Database connection error: {e}")

#Prefect flow to:
#1. Check the latest XKCD comic.
#2. Fetch and insert all missing comics.
@flow(name="process-xkcd-comics")
def process_xkcd_comics():
    latest_comic = fetch_latest_comic()
    last_comic_id = get_last_comic_id_in_db()

    if last_comic_id is None or latest_comic["num"] > last_comic_id:
        start_id = latest_comic["num"]
        end_id = last_comic_id + 1 if last_comic_id else max(start_id - 49, 1)
        fetch_and_insert_comics(start_id, end_id)
    else:
        logger.info(f"No new XKCD comics to update. Latest in DB: {last_comic_id}")

if __name__ == "__main__":
    process_xkcd_comics()  
