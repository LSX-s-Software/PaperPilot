from typing import Dict, List, Union

SimpleValue = Union[str, int, bool, float]

JSONValue = Union[None, SimpleValue, List["JSONVal"], Dict[str, "JSONVal"]]  # noqa: F821
