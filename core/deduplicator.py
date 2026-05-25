class Deduplicator:

    def __init__(self, database):

        self.db = database

    def is_duplicate(
        self,
        email,
        profile_url
    ):

        return self.db.lead_exists(
            email,
            profile_url
        )