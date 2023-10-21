import datetime
import random
import time
from typing import AnyStr, Tuple
from urllib.request import urlopen

from django.core.cache import cache
from django.db.models import TextChoices


class OssDirectToken:
    access_key_id: str
    host: str
    policy: str
    signature: str
    callback: str

    def __init__(self, access_key_id: str, host: str, policy: str, signature: str, callback: str):
        self.access_key_id = access_key_id
        self.host = host
        self.policy = policy
        self.signature = signature
        self.callback = callback

    def to_protobuf(self):
        from paperpilot_common.protobuf.common.util_pb2 import OssToken

        return OssToken(
            access_key_id=self.access_key_id,
            host=self.host,
            policy=self.policy,
            signature=self.signature,
            callback_body=self.callback,
        )


class ConditionCompare(TextChoices):
    EQ = "eq"
    START_WITH = "starts-with"
    IN = "in"
    NOT_IN = "not-in"


class Condition:
    value: str | list[str]
    compare: ConditionCompare

    def __init__(self, value: str | list[str], compare: ConditionCompare = None):
        if compare:  # 传入比较类型
            self.value = value
            self.compare = compare
        else:  # 未传入比较类型
            if isinstance(value, list):  # 如果是列表
                self.value = value
                self.compare = ConditionCompare.IN  # 默认为in
            else:  # 如果是字符串
                if value.endswith("*"):  # 如果是以*结尾
                    self.value = value[:-1]
                    self.compare = ConditionCompare.START_WITH  # 默认为starts-with
                else:  # 普通字符串
                    self.value = value
                    self.compare = ConditionCompare.EQ  # 默认为eq

    def parse(self, key: str) -> list[str | list[str]]:
        return [self.compare.value, f"${key}", self.value]


def escape_special_characters(input_str: str) -> str:
    escaped_str = input_str

    # 使用转义字符替换特殊字符
    escaped_str = escaped_str.replace("\\", "\\\\")  # 反斜杠
    escaped_str = escaped_str.replace("/", "\\/")  # 斜杠
    escaped_str = escaped_str.replace('"', '\\"')  # 双引号
    escaped_str = escaped_str.replace("$", "\\$")  # 美元符
    escaped_str = escaped_str.replace("\b", "\\b")  # 空格
    escaped_str = escaped_str.replace("\f", "\\f")  # 换页
    escaped_str = escaped_str.replace("\n", "\\n")  # 换行
    escaped_str = escaped_str.replace("\r", "\\r")  # 回车
    escaped_str = escaped_str.replace("\t", "\\t")  # 水平制表符

    return escaped_str


def handle_condition(conditions: list[list], key: str, value: str | list[str] | Condition | None) -> None:
    """
    处理条件
    """
    if not value:
        return

    if isinstance(value, str) or isinstance(value, list):
        condition = Condition(value)
    else:
        condition = value

    conditions.append(condition.parse(key))


def parse_size(size: str | int) -> int:
    """
    解析大小

    :param size: 大小
    :return: 字节数
    """
    if isinstance(size, int):
        return size

    size = size.strip().lower()
    multipliers = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4, "p": 1024**5}

    if size[-1] == "b":
        size = size[:-1]

    if size == "":
        return 0

    try:
        if size.isdigit():
            return int(size)
        for unit, multiplier in multipliers.items():
            if size.endswith(unit):
                num = float(size[:-1])
                return int(num * multiplier)
        raise ValueError("Invalid size format")
    except ValueError:
        raise ValueError("Invalid size format")


def get_iso_8601(expire: float) -> str:
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += "Z"
    return gmt


def split_file_name(file_name: str) -> Tuple[str, str]:
    """
    获取文件名与扩展名

    :param file_name: 文件全名

    :return: 文件名，扩展名
    """
    if "." in file_name:  # 文件存在扩展名
        ext = file_name.split(".")[-1]  # 文件扩展名
        name = ".".join(file_name.split(".")[0:-1])
    else:
        ext = ""
        name = file_name

    return name, ext


def get_random_name(file_name: str) -> str:
    """
    获取随机文件名

    :param file_name: 原文件名

    :return:
    """
    name, ext = split_file_name(file_name)

    new_name = time.strftime("%Y%m%d%H%M%S")  # 定义文件名，年月日时分秒随机数
    new_name = new_name + "_%04d" % random.randint(0, 10000) + (("." + ext) if ext != "" else "")

    return new_name
