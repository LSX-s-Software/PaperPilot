import logging
import os
import shutil
from datetime import datetime, timezone
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, List, Optional, Union
from urllib.parse import urljoin

import oss2
import oss2.exceptions
import oss2.utils
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from oss2.models import GetObjectMetaResult

from .configs import oss_settings
from .exceptions import OssError

logger = logging.getLogger("oss")


@deconstructible
class OssStorage(Storage):
    """
    Aliyun OSS Storage 基本存储
    """

    access_key_id: str
    access_key_secret: str
    end_point: str
    bucket_name: str
    expire_time: int

    auth: oss2.Auth
    service: oss2.Service
    bucket: oss2.Bucket
    bucket_acl: str

    base_dir: str  # 基本路径

    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        end_point: Optional[str] = None,
        bucket_name: Optional[str] = None,
        expire_time: Optional[int] = None,
    ):
        self.access_key_id = access_key_id or oss_settings.ACCESS_KEY_ID
        self.access_key_secret = access_key_secret or oss_settings.ACCESS_KEY_SECRET
        self.end_point = self._normalize_endpoint(end_point or oss_settings.ENDPOINT)
        self.bucket_name = bucket_name or oss_settings.BUCKET_NAME
        self.expire_time = expire_time or oss_settings.URL_EXPIRE_SECOND

        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.service = oss2.Service(self.auth, self.end_point)
        self.bucket = oss2.Bucket(self.auth, self.end_point, self.bucket_name)

        # try to get bucket acl to check bucket exist or not
        try:
            self.bucket_acl = self.bucket.get_bucket_acl().acl
        except oss2.exceptions.NoSuchBucket:
            raise SuspiciousOperation("Bucket '%s' does not exist." % self.bucket_name)

    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            return "http://" + endpoint
        else:
            return endpoint

    def _get_key_name(self, name: str) -> str:
        """
        Get the object key name in OSS, e.g.,
        base_dir: /media/
        :param name: test.txt
        :return: media/test.txt
        """
        # urljoin won't work if name is absolute path
        name = name.lstrip("/")

        base_path = force_str(self.base_dir)
        final_path = urljoin(base_path + "/", name)
        name = os.path.normpath(final_path.lstrip("/"))

        # Add / to the end of path since os.path.normpath will remove it
        if final_path.endswith("/") and not name.endswith("/"):
            name += "/"

        # Store filenames with forward slashes, even on Windows.
        return name.replace("\\", "/")

    def _open(self, name: str, mode: str = "rb") -> "OssFile":
        """
        Open a file for reading from OSS.
        :param name: 文件名
        :param mode: 打开模式
        :return:
        """
        logger.debug("name: %s, mode: %s", name, mode)
        if mode != "rb":
            raise ValueError("OSS files can only be opened in read-only mode")

        target_name = self._get_key_name(name)
        logger.debug("target name: %s", target_name)
        try:
            # Load the key into a temporary file
            tmp_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)  # 10MB
            obj = self.bucket.get_object(target_name)
            logger.info(
                "content length: %d, requestid: %s",
                obj.content_length,
                obj.request_id,
            )
            if obj.content_length is None:
                shutil.copyfileobj(obj, tmp_file)
            else:
                oss2.utils.copyfileobj_and_verify(obj, tmp_file, obj.content_length, request_id=obj.request_id)
            tmp_file.seek(0)
            return OssFile(tmp_file, target_name, self)
        except oss2.exceptions.NoSuchKey:
            raise OssError("%s does not exist" % name)
        except Exception:
            raise OssError("Failed to open %s" % name)

    def _save(self, name: str, content: Union[File, bytes, str]) -> str:
        target_name = self._get_key_name(name)
        logger.debug("target name: %s", target_name)
        logger.debug("content: %s", content)
        self.bucket.put_object(target_name, content)
        return os.path.normpath(name)

    def create_dir(self, dirname: str) -> None:
        """
        创建目录
        :param dirname: 文件夹路径
        :return:
        """
        target_name = self._get_key_name(dirname)
        if not target_name.endswith("/"):
            target_name += "/"

        self.bucket.put_object(target_name, "")

    def exists(self, name: str) -> bool:
        target_name = self._get_key_name(name)
        logger.debug("name: %s, target name: %s", name, target_name)
        return self.bucket.object_exists(target_name)

    def get_file_meta(self, name: str) -> GetObjectMetaResult:
        """
        获取文件信息
        :param name: 文件名
        :return:
        """
        name = self._get_key_name(name)
        return self.bucket.get_object_meta(name)

    def size(self, name: str) -> int:
        file_meta = self.get_file_meta(name)
        return file_meta.content_length

    def modified_time(self, name: str) -> datetime:
        file_meta = self.get_file_meta(name)
        return datetime.fromtimestamp(file_meta.last_modified)

    created_time = accessed_time = modified_time

    def get_modified_time(self, name: str) -> datetime:
        file_meta = self.get_file_meta(name)

        if settings.USE_TZ:
            return datetime.utcfromtimestamp(file_meta.last_modified).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(file_meta.last_modified)

    get_created_time = get_accessed_time = get_modified_time

    def content_type(self, name: str) -> str:
        name = self._get_key_name(name)
        file_info = self.bucket.head_object(name)
        return file_info.content_type

    def listdir(self, name: str) -> (List[str], List[str]):
        if name == ".":
            name = ""
        name = self._get_key_name(name)
        if not name.endswith("/"):
            name += "/"
        logger.debug("name: %s", name)

        files: list[str] = []
        dirs: list[str] = []

        for obj in oss2.ObjectIterator(self.bucket, prefix=name, delimiter="/"):
            if obj.is_prefix():
                dirs.append(obj.key)
            else:
                files.append(obj.key)

        logger.debug("dirs: %s", list(dirs))
        logger.debug("files: %s", files)
        return dirs, files

    def url(self, name: str) -> str:
        """
        获取文件的url(带token)
        :param name: 文件名
        :return: url
        """
        key = self._get_key_name(name)
        url = self.bucket.sign_url("GET", key, expires=self.expire_time)
        if self.bucket_acl != oss2.BUCKET_ACL_PRIVATE:
            idx = url.find("?")
            if idx > 0:
                url = url[:idx].replace("%2F", "/")
        return url

    def delete(self, name: str) -> None:
        """
        删除文件

        :param name:
        :return:
        """
        name = self._get_key_name(name)
        logger.debug("delete name: %s", name)
        self.bucket.delete_object(name)

    def delete_dir(self, dirname: str) -> None:
        """
        删除文件夹

        :param dirname:
        :return:
        """
        name = self._get_key_name(dirname)
        if not name.endswith("/"):
            name += "/"
        logger.debug("delete name: %s", name)
        self.bucket.delete_object(name)

    def get_object_acl(self, name: str) -> str:
        """
        获取文件的访问权限
        :param name: 文件名
        :return:
        """
        name = self._get_key_name(name)
        return self.bucket.get_object_acl(name).acl

    def set_object_acl(self, name: str, acl: str) -> None:
        """
        设置文件的访问权限
        :param name: 文件名
        :param acl: 访问权限
        :return:
        """
        name = self._get_key_name(name)
        self.bucket.put_object_acl(name, acl)


class OssMediaStorage(OssStorage):
    def __init__(self):
        self.base_dir = settings.MEDIA_URL
        logger.debug("locatin: %s", self.base_dir)
        super(OssMediaStorage, self).__init__()


class OssStaticStorage(OssStorage):
    def __init__(self):
        self.base_dir = settings.STATIC_URL
        logger.info("locatin: %s", self.base_dir)
        super(OssStaticStorage, self).__init__()


class OssFile(File):
    """
    A file returned from AliCloud OSS
    """

    def __init__(self, content: SpooledTemporaryFile, name: str, storage: OssStorage):
        super(OssFile, self).__init__(content, name)
        self._storage = storage

    def open(self, mode: str = "rb") -> BinaryIO:
        if self.closed:
            self.file = self._storage.open(self.name, mode).file
        return super(OssFile, self).open(mode)
