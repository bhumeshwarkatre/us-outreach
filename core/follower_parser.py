import re


class FollowerParser:

    @staticmethod
    def parse(value: str):

        value = value.strip().upper()

        number = re.findall(r"[\d\.]+", value)

        if not number:
            return 0

        number = float(number[0])

        if "K" in value:
            number *= 1000

        elif "M" in value:
            number *= 1000000

        return int(number)