import base64
import hashlib
import hmac
import json
import time
import zlib

from server.business.im import config


def base64_encode_url(data):
    """base url encode 实现"""
    base64_data = base64.b64encode(data)
    base64_data_str = bytes.decode(base64_data)
    base64_data_str = base64_data_str.replace("+", "*")
    base64_data_str = base64_data_str.replace("/", "-")
    base64_data_str = base64_data_str.replace("=", "_")
    return base64_data_str


def base64_decode_url(base64_data):
    """base url decode 实现"""
    base64_data_str = bytes.decode(base64_data)
    base64_data_str = base64_data_str.replace("*", "+")
    base64_data_str = base64_data_str.replace("-", "/")
    base64_data_str = base64_data_str.replace("_", "=")
    raw_data = base64.b64decode(base64_data_str)
    return raw_data


class TLSSigAPIv2:
    __sdkappid = config.app_id
    __version = "2.0"
    __key = config.secret_key

    # 用于生成实时音视频(TRTC)业务进房权限加密串,具体用途用法参考TRTC文档：https://cloud.tencent.com/document/product/647/32240
    # TRTC业务进房权限加密串需使用用户定义的userbuf
    # @brief 生成 userbuf
    # @param account 用户名
    # @param dwSdkappid sdkappid
    # @param dwAuthID  数字房间号
    # @param dwExpTime 过期时间：该权限加密串的过期时间，实际过期时间：当前时间+dwExpTime
    # @param dwPrivilegeMap 用户权限，255表示所有权限
    # @param dwAccountType 用户类型,默认为0
    # @param roomStr 字符串房间号,数字房间号非0时存在
    # @return userbuf  {string}  返回的userbuf
    # /

    # It is used to generate real-time audio and video (TRTC) business access rights encryption string. For specific usage, please refer to the TRTC document：https://cloud.tencent.com/document/product/647/32240
    # User-defined userbuf is used for the encrypted string of TRTC service entry permission
    # @brief generate userbuf
    # @param account username
    # @param dwSdkappid sdkappid
    # @param dwAuthID  digital room number
    # @param dwExpTime Expiration time: The expiration time of the encrypted string of this permission. Expiration time = now+dwExpTime
    # @param dwPrivilegeMap User permissions, 255 means all permissions
    # @param dwAccountType User type, default is 0
    # @param roomStr String room number
    # @return userbuf string  returned userbuf
    # /

    def _gen_userbuf(
        self,
        account,
        dwAuthID,
        dwExpTime,
        dwPrivilegeMap,
        dwAccountType,
        roomStr,
    ):
        userBuf = b""

        if len(roomStr) > 0:
            userBuf += bytearray([1])
        else:
            userBuf += bytearray([0])

        userBuf += bytearray(
            [
                ((len(account) & 0xFF00) >> 8),
                (len(account) & 0x00FF),
            ]
        )
        userBuf += bytearray(map(ord, account))

        # dwSdkAppid
        userBuf += bytearray(
            [
                ((self.__sdkappid & 0xFF000000) >> 24),
                ((self.__sdkappid & 0x00FF0000) >> 16),
                ((self.__sdkappid & 0x0000FF00) >> 8),
                (self.__sdkappid & 0x000000FF),
            ]
        )

        # dwAuthId
        userBuf += bytearray(
            [
                ((dwAuthID & 0xFF000000) >> 24),
                ((dwAuthID & 0x00FF0000) >> 16),
                ((dwAuthID & 0x0000FF00) >> 8),
                (dwAuthID & 0x000000FF),
            ]
        )

        #  dwExpTime = now + 300;
        expire = dwExpTime + int(time.time())
        userBuf += bytearray(
            [
                ((expire & 0xFF000000) >> 24),
                ((expire & 0x00FF0000) >> 16),
                ((expire & 0x0000FF00) >> 8),
                (expire & 0x000000FF),
            ]
        )

        # dwPrivilegeMap
        userBuf += bytearray(
            [
                ((dwPrivilegeMap & 0xFF000000) >> 24),
                ((dwPrivilegeMap & 0x00FF0000) >> 16),
                ((dwPrivilegeMap & 0x0000FF00) >> 8),
                (dwPrivilegeMap & 0x000000FF),
            ]
        )

        # dwAccountType
        userBuf += bytearray(
            [
                ((dwAccountType & 0xFF000000) >> 24),
                ((dwAccountType & 0x00FF0000) >> 16),
                ((dwAccountType & 0x0000FF00) >> 8),
                (dwAccountType & 0x000000FF),
            ]
        )
        if len(roomStr) > 0:
            userBuf += bytearray(
                [
                    ((len(roomStr) & 0xFF00) >> 8),
                    (len(roomStr) & 0x00FF),
                ]
            )
            userBuf += bytearray(map(ord, roomStr))
        return userBuf

    def __hmacsha256(self, identifier, curr_time, expire, base64_userbuf=None):
        """通过固定串进行 hmac 然后 base64 得的 sig 字段的值"""
        raw_content_to_be_signed = (
            "TLS.identifier:"
            + str(identifier)
            + "\n"
            + "TLS.sdkappid:"
            + str(self.__sdkappid)
            + "\n"
            + "TLS.time:"
            + str(curr_time)
            + "\n"
            + "TLS.expire:"
            + str(expire)
            + "\n"
        )
        if base64_userbuf is not None:
            raw_content_to_be_signed += "TLS.userbuf:" + base64_userbuf + "\n"
        return base64.b64encode(
            hmac.new(
                self.__key.encode("utf-8"),
                raw_content_to_be_signed.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        )

    def __gen_sig(self, identifier, expire=180 * 86400, userbuf=None):
        """用户可以采用默认的有效期生成 sig"""
        curr_time = int(time.time())
        m = dict()
        m["TLS.ver"] = self.__version
        m["TLS.identifier"] = str(identifier)
        m["TLS.sdkappid"] = int(self.__sdkappid)
        m["TLS.expire"] = int(expire)
        m["TLS.time"] = int(curr_time)
        base64_userbuf = None
        if userbuf is not None:
            base64_userbuf = bytes.decode(base64.b64encode(userbuf))
            m["TLS.userbuf"] = base64_userbuf

        m["TLS.sig"] = bytes.decode(
            self.__hmacsha256(identifier, curr_time, expire, base64_userbuf)
        )

        raw_sig = json.dumps(m)
        sig_cmpressed = zlib.compress(raw_sig.encode("utf-8"))
        base64_sig = base64_encode_url(sig_cmpressed)
        return base64_sig

    ##
    # 【功能说明】用于签发 TRTC 和 IM 服务中必须要使用的 UserSig 鉴权票据
    #
    # 【参数说明】
    # userid - 用户id，限制长度为32字节，只允许包含大小写英文字母（a-zA-Z）、数字（0-9）及下划线和连词符。
    # expire - UserSig 票据的过期时间，单位是秒，比如 86400 代表生成的 UserSig 票据在一天后就无法再使用了。
    # /

    # Function: Used to issue UserSig that is required by the TRTC and IM services.

    #  Parameter description:
    #  userid - User ID. The value can be up to 32 bytes in length and contain letters (a-z and A-Z), digits (0-9), underscores (_), and hyphens (-).
    #  expire - UserSig expiration time, in seconds. For example, 86400 indicates that the generated UserSig will expire one day after being generated.

    def genUserSig(self, userid, expire=86400):
        """用户可以采用默认的有效期生成 sig"""
        return self.__gen_sig(userid, expire, None)

    ##
    # 【功能说明】
    # 用于签发 TRTC 进房参数中可选的 PrivateMapKey 权限票据。
    # PrivateMapKey  需要跟 UserSig 一起使用，但比 UserSig 有更强的权限控制能力：
    # - UserSig 只能控制某个 UserID 有无使用 TRTC 服务的权限，只要 UserSig 正确，其对应的 UserID 可以进出任意房间。
    # - PrivateMapKey 则是将 UserID 的权限控制的更加严格，包括能不能进入某个房间，能不能在该房间里上行音视频等等。
    # 如果要开启 PrivateMapKey 严格权限位校验，需要在【实时音视频控制台】=>【应用管理】=>【应用信息】中“启动权限密钥”。
    #
    # 【参数说明】
    # userid - 用户id，限制长度为32字节，只允许包含大小写英文字母（a-zA-Z）、数字（0-9）及下划线和连词符。
    # expire - PrivateMapKey 票据的过期时间，单位是秒，比如 86400 生成的 PrivateMapKey 票据在一天后就无法再使用了。
    # roomid - 房间号，用于指定该 userid 可以进入的房间号
    # privilegeMap - 权限位，使用了一个字节中的 8 个比特位，分别代表八个具体的功能权限：
    #  - 第 1 位：0000 0001 = 1，创建房间的权限
    #  - 第 2 位：0000 0010 = 2，加入房间的权限
    #  - 第 3 位：0000 0100 = 4，发送语音的权限
    #  - 第 4 位：0000 1000 = 8，接收语音的权限
    #  - 第 5 位：0001 0000 = 16，发送视频的权限
    #  - 第 6 位：0010 0000 = 32，接收视频的权限
    #  - 第 7 位：0100 0000 = 64，发送辅路（也就是屏幕分享）视频的权限
    #  - 第 8 位：1000 0000 = 200，接收辅路（也就是屏幕分享）视频的权限
    #  - privilegeMap == 1111 1111 == 255 代表该 userid 在该 roomid 房间内的所有功能权限。
    #  - privilegeMap == 0010 1010 == 42  代表该 userid 拥有加入房间和接收音视频数据的权限，但不具备其他权限。
    # /

    # Function:
    # Used to issue PrivateMapKey that is optional for room entry.
    # PrivateMapKey must be used together with UserSig but with more powerful permission control capabilities.
    #  - UserSig can only control whether a UserID has permission to use the TRTC service. As long as the UserSig is correct, the user with the corresponding UserID can enter or leave any room.
    #  - PrivateMapKey specifies more stringent permissions for a UserID, including whether the UserID can be used to enter a specific room and perform audio/video upstreaming in the room.
    # To enable stringent PrivateMapKey permission bit verification, you need to enable permission key in TRTC console > Application Management > Application Info.
    #      *
    # Parameter description:
    # userid - User ID. The value can be up to 32 bytes in length and contain letters (a-z and A-Z), digits (0-9), underscores (_), and hyphens (-).
    # roomid - ID of the room to which the specified UserID can enter.
    # expire - PrivateMapKey expiration time, in seconds. For example, 86400 indicates that the generated PrivateMapKey will expire one day after being generated.
    # privilegeMap - Permission bits. Eight bits in the same byte are used as the permission switches of eight specific features:
    #  - Bit 1: 0000 0001 = 1, permission for room creation
    #  - Bit 2: 0000 0010 = 2, permission for room entry
    #  - Bit 3: 0000 0100 = 4, permission for audio sending
    #  - Bit 4: 0000 1000 = 8, permission for audio receiving
    #  - Bit 5: 0001 0000 = 16, permission for video sending
    #  - Bit 6: 0010 0000 = 32, permission for video receiving
    #  - Bit 7: 0100 0000 = 64, permission for substream video sending (screen sharing)
    #  - Bit 8: 1000 0000 = 200, permission for substream video receiving (screen sharing)
    #  - privilegeMap == 1111 1111 == 255: Indicates that the UserID has all feature permissions of the room specified by roomid.
    #  - privilegeMap == 0010 1010 == 42: Indicates that the UserID has only the permissions to enter the room and receive audio/video data.

    def genPrivateMapKey(self, userid, expire, roomid, privilegeMap):
        """带 userbuf 生成签名"""
        userbuf = self._gen_userbuf(userid, roomid, expire, privilegeMap, 0, "")
        print(userbuf)
        return self.__gen_sig(userid, expire, userbuf)

    ##
    # 【功能说明】
    # 用于签发 TRTC 进房参数中可选的 PrivateMapKey 权限票据。
    # PrivateMapKey  需要跟 UserSig 一起使用，但比 UserSig 有更强的权限控制能力：
    # - UserSig 只能控制某个 UserID 有无使用 TRTC 服务的权限，只要 UserSig 正确，其对应的 UserID 可以进出任意房间。
    # - PrivateMapKey 则是将 UserID 的权限控制的更加严格，包括能不能进入某个房间，能不能在该房间里上行音视频等等。
    # 如果要开启 PrivateMapKey 严格权限位校验，需要在【实时音视频控制台】=>【应用管理】=>【应用信息】中“启动权限密钥”。
    #
    # 【参数说明】
    # userid - 用户id，限制长度为32字节，只允许包含大小写英文字母（a-zA-Z）、数字（0-9）及下划线和连词符。
    # expire - PrivateMapKey 票据的过期时间，单位是秒，比如 86400 生成的 PrivateMapKey 票据在一天后就无法再使用了。
    # roomstr - 字符串房间号，用于指定该 userid 可以进入的房间号
    # privilegeMap - 权限位，使用了一个字节中的 8 个比特位，分别代表八个具体的功能权限：
    #  - 第 1 位：0000 0001 = 1，创建房间的权限
    #  - 第 2 位：0000 0010 = 2，加入房间的权限
    #  - 第 3 位：0000 0100 = 4，发送语音的权限
    #  - 第 4 位：0000 1000 = 8，接收语音的权限
    #  - 第 5 位：0001 0000 = 16，发送视频的权限
    #  - 第 6 位：0010 0000 = 32，接收视频的权限
    #  - 第 7 位：0100 0000 = 64，发送辅路（也就是屏幕分享）视频的权限
    #  - 第 8 位：1000 0000 = 200，接收辅路（也就是屏幕分享）视频的权限
    #  - privilegeMap == 1111 1111 == 255 代表该 userid 在该 roomid 房间内的所有功能权限。
    #  - privilegeMap == 0010 1010 == 42  代表该 userid 拥有加入房间和接收音视频数据的权限，但不具备其他权限。
    # /

    # Function:
    #  Used to issue PrivateMapKey that is optional for room entry.
    #  PrivateMapKey must be used together with UserSig but with more powerful permission control capabilities.
    #   - UserSig can only control whether a UserID has permission to use the TRTC service. As long as the UserSig is correct, the user with the corresponding UserID can enter or leave any room.
    #   - PrivateMapKey specifies more stringent permissions for a UserID, including whether the UserID can be used to enter a specific room and perform audio/video upstreaming in the room.
    #  To enable stringent PrivateMapKey permission bit verification, you need to enable permission key in TRTC console > Application Management > Application Info.
    #  *
    #  Parameter description:
    #  @param userid - User ID. The value can be up to 32 bytes in length and contain letters (a-z and A-Z), digits (0-9), underscores (_), and hyphens (-).
    #  @param roomstr - ID of the room to which the specified UserID can enter.
    #  @param expire - PrivateMapKey expiration time, in seconds. For example, 86400 indicates that the generated PrivateMapKey will expire one day after being generated.
    #  @param privilegeMap - Permission bits. Eight bits in the same byte are used as the permission switches of eight specific features:
    #   - Bit 1: 0000 0001 = 1, permission for room creation
    #   - Bit 2: 0000 0010 = 2, permission for room entry
    #   - Bit 3: 0000 0100 = 4, permission for audio sending
    #   - Bit 4: 0000 1000 = 8, permission for audio receiving
    #   - Bit 5: 0001 0000 = 16, permission for video sending
    #   - Bit 6: 0010 0000 = 32, permission for video receiving
    #   - Bit 7: 0100 0000 = 64, permission for substream video sending (screen sharing)
    #   - Bit 8: 1000 0000 = 200, permission for substream video receiving (screen sharing)
    #   - privilegeMap == 1111 1111 == 255: Indicates that the UserID has all feature permissions of the room specified by roomid.
    #   - privilegeMap == 0010 1010 == 42: Indicates that the UserID has only the permissions to enter the room and receive audio/video data.
    def genPrivateMapKeyWithStringRoomID(
        self, userid, expire, roomstr, privilegeMap
    ):
        """带 userbuf 生成签名"""
        userbuf = self._gen_userbuf(userid, 0, expire, privilegeMap, 0, roomstr)
        print(userbuf)
        return self.__gen_sig(userid, expire, userbuf)


auth = TLSSigAPIv2()

__all__ = ["auth"]
