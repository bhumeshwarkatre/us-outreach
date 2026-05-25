from config.settings import (
    MIN_FOLLOWERS,
    MAX_FOLLOWERS
)


class LeadFilters:

    @staticmethod
    def valid_followers(count):

        return (
            MIN_FOLLOWERS <= count <= MAX_FOLLOWERS
        )

    @staticmethod
    def valid_country(country):

        return country.lower() in [
            "usa",
            "united states",
            "united states of america"
        ]