import random
import string


def get_random_invite_code() -> str:
    """
    获取随机邀请码
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))
