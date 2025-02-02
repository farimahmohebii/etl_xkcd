import requests
import time
from datetime import date, datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

# Configure logging
logger = logging.getLogger("airflow.task")
logger.setLevel(logging.INFO)

#This function polls the XKCD API every `poll_interval` seconds from 00:00 to 23:59 UTC.
#param "poll_interval": Time interval between polls (in seconds, default 10 minutes)
def poll_for_new_comics(poll_interval=600):
    while True:
        now = datetime.utcnow()

        # Stop polling at 23:59 UTC
        if now.hour == 23 and now.minute >= 50:
            logger.info("Polling window ended. Stopping at 23:59 UTC.")
            break

        response = requests.get("https://xkcd.com/info.0.json")
        response.raise_for_status()
        data = response.json()

        latest_comic_id = data["num"]
        last_comic_id = get_last_comic_id_in_db()

        if last_comic_id is None or latest_comic_id > last_comic_id:
            logger.info(f"New comics found! Latest XKCD ID: {latest_comic_id} | Last DB ID: {last_comic_id}")
            fetch_and_insert_comics(latest_comic_id, last_comic_id + 1 if last_comic_id else max(latest_comic_id - 49, 1))

        logger.info(f"No new comic yet. Checking again in {poll_interval // 60} minutes...")
        time.sleep(poll_interval)  # Wait for the next polling cycle

#This function retrieves the last comic ID stored in the database.
def get_last_comic_id_in_db():
    pg_hook = PostgresHook(postgres_conn_id="xkcd_db")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(comic_id) FROM xkcd_comics;")
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return result[0] if result[0] else None

#This function fetchs and inserts missing XKCD comics from `start_id` to `end_id`.
def fetch_and_insert_comics(start_id, end_id):
    pg_hook = PostgresHook(postgres_conn_id="xkcd_db")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    # Fetch from latest to oldest
    for comic_id in range(start_id, end_id - 1, -1):  
        try:
            response = requests.get(f"https://xkcd.com/{comic_id}/info.0.json")
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

            logger.info(f"Comic '{title}' (ID: {comic_id}) inserted successfully.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch comic ID {comic_id}. Error: {e}")
        except Exception as e:
            logger.error(f"Error inserting comic ID {comic_id} into the database. Error: {e}")

    cursor.close()
    connection.close()

#Main function to process XKCD comics:
#- Poll for new comics from 00:00 to 23:59 UTC.
#- Insert all missing comics when found.
def process_xkcd_comics():
    logger.info("Starting all-day polling for XKCD comics.")
    poll_for_new_comics()
process_xkcd_comics()
