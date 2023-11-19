import hashlib
import urllib.parse


def generate_color(username: str) -> (str, str):
    """
    根据用户名生成颜色

    :param username: 用户名
    :return: 背景色，文本色
    """
    username_hash = int(hashlib.md5(username.lower().encode()).hexdigest(), 16)
    background_color = f"{username_hash & 0xFFFFFF:06X}"

    red, green, blue = (
        int(background_color[1:3], 16),
        int(background_color[3:5], 16),
        int(background_color[5:7], 16),
    )
    brightness = (red * 299 + green * 587 + blue * 114) / 1000
    if brightness > 128:
        text_color = "000000"  # 亮背景，选择黑色文本
    else:
        text_color = "FFFFFF"  # 暗背景，选择白色文本

    return background_color, text_color


def generate_avatar(username: str) -> str:
    """
    根据用户名生成头像

    :param username: 用户名
    :return: 头像地
    """
    background_color, text_color = generate_color(username)
    return (
        f"https://ui-avatars.com/api/?"
        f"background={background_color}&"
        f"color={text_color}&"
        f"name={urllib.parse.quote(username)}"
    )
