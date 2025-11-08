import psycopg2
import os

def get_connection():

    try:
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD= os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,  # e.g., "localhost" if running locally
            port=DB_PORT    # e.g., "5432" (default PostgreSQL port)
        )
        return conn
    except OSError as e:
        raise OSError(f"Error at getting the database credentials {e}")

    except psycopg2.Error as e:
        raise psycopg2.Error(f"Error connecting to PostgreSQL: {e}")