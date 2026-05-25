import sqlite3

from config.settings import DATABASE_PATH


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        with open("database/schema.sql", "r") as file:
            self.cursor.executescript(file.read())
            self.conn.commit()

    def lead_exists(self, email, profile_url):

        query = """
        SELECT id
        FROM leads
        WHERE email = ?
        OR profile_url = ?
        """

        self.cursor.execute(query, (email, profile_url))

        return self.cursor.fetchone() is not None

    def insert_lead(self, data):

        query = """
        INSERT INTO leads (
            creator_name,
            email,
            platform,
            niche,
            followers,
            country,
            profile_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            query,
            (
                data["creator_name"],
                data["email"],
                data["platform"],
                data["niche"],
                data["followers"],
                data["country"],
                data["profile_url"]
            )
        )

        self.conn.commit()