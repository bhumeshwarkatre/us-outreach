import json
import random


class QueryGenerator:

    def __init__(self):

        # =========================
        # LOAD CONFIG FILES
        # =========================

        with open(
            "config/niches.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.niches = json.load(f)

        with open(
            "config/cities.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.cities = json.load(f)

        with open(
            "config/platforms.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.platforms = json.load(f)

        # optional
        try:

            with open(
                "config/modifiers.json",
                "r",
                encoding="utf-8"
            ) as f:

                self.modifiers = json.load(f)

        except:
            self.modifiers = []

        # optional
        try:

            with open(
                "config/filters.json",
                "r",
                encoding="utf-8"
            ) as f:

                self.filters = json.load(f)

        except:
            self.filters = []

        # =========================
        # EMAIL SEARCH OPERATORS
        # =========================

        self.email_operators = (
            '("@gmail.com" OR '
            '"@yahoo.com" OR '
            '"@hotmail.com")'
        )

        # =========================
        # FOLLOWER RANGE TARGET
        # =========================

        self.follower_operators = (
            '("15k" OR '
            '"20k" OR '
            '"30k" OR '
            '"50k" OR '
            '"75k" OR '
            '"100k")'
        )

        # =========================
        # CLEAN URL FILTERS
        # =========================

        self.exclude_operators = (
            '-inurl:/p/ '
            '-inurl:/reel/ '
            '-inurl:/tv/'
        )

    # =========================
    # PICK PLATFORM
    # =========================

    def _pick_platform(self):

        return random.choice(
            self.platforms
        )

    # =========================
    # PICK NICHE
    # =========================

    def _pick_niche_data(self):

        niche_name = random.choice(
            list(self.niches.keys())
        )

        keyword = random.choice(
            self.niches[niche_name]
        )

        return niche_name, keyword

    # =========================
    # PICK CITY
    # =========================

    def _pick_city(self):

        if not self.cities:
            return None

        return random.choice(
            self.cities
        )

    # =========================
    # PICK MODIFIER
    # =========================

    def _pick_modifier(self):

        if not self.modifiers:
            return None

        # if dict
        if isinstance(
            self.modifiers,
            dict
        ):

            values = []

            for item in self.modifiers.values():

                if isinstance(item, list):

                    values.extend(item)

            modifiers_list = values

        # if list
        elif isinstance(
            self.modifiers,
            list
        ):

            modifiers_list = self.modifiers

        else:

            return None

        modifiers_list = [

            x for x in modifiers_list

            if isinstance(x, str)
            and x.strip()
        ]

        if not modifiers_list:
            return None

        return random.choice(
            modifiers_list
        )

    # =========================
    # PICK FILTERS
    # =========================

    def _pick_filters(self):

        # =====================
        # EMPTY
        # =====================

        if not self.filters:
            return []

        # =====================
        # IF JSON IS DICT
        # =====================

        if isinstance(
            self.filters,
            dict
        ):

            values = []

            for item in self.filters.values():

                if isinstance(item, list):

                    values.extend(item)

            filters_list = values

        # =====================
        # IF JSON IS LIST
        # =====================

        elif isinstance(
            self.filters,
            list
        ):

            filters_list = self.filters

        else:

            return []

        # =====================
        # CLEAN VALUES
        # =====================

        filters_list = [

            x for x in filters_list

            if isinstance(x, str)
            and x.strip()
        ]

        if not filters_list:
            return []

        # =====================
        # RANDOM SAMPLE
        # =====================

        count = random.randint(
            0,
            min(2, len(filters_list))
        )

        return random.sample(
            filters_list,
            count
        )

    # =========================
    # CLEAN QUERY
    # =========================

    def _clean_query(self, query):

        while "  " in query:

            query = query.replace(
                "  ",
                " "
            )

        return query.strip()

    # =========================
    # QUERY GENERATOR
    # =========================

    def generate_query(self):

        # =====================
        # CORE DATA
        # =====================

        platform = self._pick_platform()

        niche_name, keyword = (
            self._pick_niche_data()
        )

        city = self._pick_city()

        modifier = self._pick_modifier()

        filters = self._pick_filters()

        # =====================
        # BUILD QUERY
        # =====================

        query_parts = [

            f"site:{platform}.com",

            f'"{keyword}"'
        ]

        # =====================
        # CITY
        # =====================

        if city:

            query_parts.append(
                f'"{city}"'
            )

        # =====================
        # MODIFIER
        # =====================

        if modifier:

            query_parts.append(
                f'"{modifier}"'
            )

        # =====================
        # FILTERS
        # =====================

        for item in filters:

            if item:

                query_parts.append(
                    f'"{item}"'
                )

        # =====================
        # EMAIL OPERATORS
        # =====================

        query_parts.append(
            self.email_operators
        )

        # =====================
        # FOLLOWER TARGET
        # =====================

        query_parts.append(
            self.follower_operators
        )

        # =====================
        # URL FILTERS
        # =====================

        query_parts.append(
            self.exclude_operators
        )

        # =====================
        # FINAL QUERY
        # =====================

        query = " ".join(
            query_parts
        )

        query = self._clean_query(
            query
        )

        # =====================
        # OUTPUT
        # =====================

        return {

            "query": query,

            "platform": platform,

            "niche": niche_name,

            "keyword": keyword,

            "city": city,

            "modifier": modifier,

            "filters": filters,

            "meta": {

                "has_city":
                    city is not None,

                "has_modifier":
                    modifier is not None,

                "filter_count":
                    len(filters),

                "query_type":
                    "instagram_email_hunting_v3",

                "source":
                    "query_generator"
            }
        }
