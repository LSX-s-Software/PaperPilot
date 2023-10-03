import random
import string


def random_code() -> str:
    return "".join(random.sample(string.digits, 6))
