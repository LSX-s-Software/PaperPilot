from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from paperpilot_common.utils.types import SimpleValue

    SettingValue = Union[None, SimpleValue, List["SettingValue"], Dict[str, "SettingValue"]]
    SettingDict = Dict[str, SettingValue]


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


class PackageSettings:
    """
    Copy of DRF APISettings class with support for importing settings that
    are dicts with value as a string representing the path to the class
    to be imported.
    """

    setting_name: Optional[str] = None
    DEFAULTS: Optional["SettingDict"] = None
    IMPORT_STRINGS: Optional[List[str]] = None

    defaults: "SettingDict"
    import_strings: List[str]

    _cached_attrs: Set[str]
    _user_settings: "SettingDict"

    def __init__(
        self,
        defaults: Optional["SettingDict"] = None,
        import_strings: Optional[List[str]] = None,
    ):
        if self.setting_name is None:
            raise NotImplementedError("setting_name must be set")
        if self.DEFAULTS is None:
            raise NotImplementedError("DEFAULTS must be set")
        if self.IMPORT_STRINGS is None:
            raise NotImplementedError("IMPORT_STRINGS must be set")

        self.defaults = defaults or self.DEFAULTS
        self.import_strings = import_strings or self.IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self) -> "SettingDict":
        if not hasattr(self, "_user_settings"):
            assert self.setting_name is not None
            self._user_settings = getattr(settings, self.setting_name, {})
        return self._user_settings

    def __getattr__(self, attr: str) -> "SettingValue":
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            if isinstance(val, dict):
                val = {k: import_from_string(v, attr) for k, v in val.items()}
            else:
                val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self) -> None:
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

    def reload_package_settings(self, *args, **kwargs) -> None:
        setting = kwargs["setting"]
        if setting == self.setting_name:
            self.reload()
