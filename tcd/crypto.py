import os
import typing
import hashlib

import tgcrypto
import aiofiles
from PyQt5.QtCore import QDataStream, QByteArray, QFile, QIODevice

from .constants import TDF_MAGIC, TDEF_MAGIC
from .exceptions import KeyDataBadDecryptedSize, KeyDataBadChecksum, KeyFileInvalidChecksum, KeyFileNotFound, KeyFileInvalidMagic, CacheFileInvaildMagic, LocalKeyInvalidChecksum


class EncryptionKey:
    """
    Static class with method for working key_datas file
    """

    @staticmethod
    def __mtp_kdf_v1(key, msgKey) -> typing.Tuple[bytes, bytes]:
        # https://core.telegram.org/mtproto/description_v1#defining-aes-key-and-initialization-vector
        sha1_a = hashlib.sha1(msgKey[:16] + key[8:8 + 32]).digest()
        sha1_b = hashlib.sha1(
            key[8 + 32: 8 + 32 + 16]
            + msgKey[:16]
            + key[8 + 48: 8 + 48 + 16]).digest()

        sha1_c = hashlib.sha1(
            key[8 + 64: 8 + 64 + 32] + msgKey[:16]).digest()
        sha1_d = hashlib.sha1(
            msgKey[:16] + key[8 + 96: 8 + 96 + 32]).digest()

        aesKey = sha1_a[:8] + sha1_b[8: 8 + 12] + sha1_c[4: 4 + 12]
        aesIv = sha1_a[8: 8 + 12] + sha1_b[:8] + \
            sha1_c[16: 16 + 4] + sha1_d[:8]

        return aesKey, aesIv

    @staticmethod
    def __aesDecryptLocal(src: bytes, key: bytes, key128: bytes) -> bytes:
        aesKey, aesIV = EncryptionKey.__mtp_kdf_v1(key, key128)
        dst = tgcrypto.ige256_decrypt(src, aesKey, aesIV)
        return dst

    @staticmethod
    def DecryptLocal(encrypted: bytes, key: bytes) -> bytes:
        encryptedSize = len(encrypted)
        if (encryptedSize <= 16) or (encryptedSize & 0x0F):
            raise KeyDataBadDecryptedSize(
                f"Bad encrypted part size: {encryptedSize}")

        encryptedKey = encrypted[:16]
        decrypted = EncryptionKey.__aesDecryptLocal(
            encrypted[16:], key, encryptedKey)
        checkHash = hashlib.sha1(decrypted).digest()[:16]
        if checkHash != encryptedKey:
            raise KeyDataBadChecksum(
                "Bad decrypt key, key not decrypted, maybe incorrect password!")

        dataLen = int.from_bytes(decrypted[:4], 'little')
        return decrypted[4:dataLen]

    @staticmethod
    def CreateLocalKey(passcode: bytes, salt: bytes) -> bytes:
        hashKey = hashlib.sha512(salt)
        hashKey.update(passcode)
        hashKey.update(salt)

        iterCount = 100000 if passcode else 1
        localKey = hashlib.pbkdf2_hmac(
            'sha512', hashKey.digest(), salt, iterCount, 256)

        return localKey

    @staticmethod
    def ReadKeyData(keypath: str) -> typing.Tuple[bytes, bytes]:
        filename = os.path.basename(keypath)
        file = QFile(keypath)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise KeyFileNotFound(f"Could not open {filename}")

        magic = file.read(4)
        if magic != TDF_MAGIC:
            file.close()
            raise KeyFileInvalidMagic(
                f"Invalid magic {magic} in file {filename}")

        version = int.from_bytes(file.read(4), "little")

        qdata = QByteArray(file.read(file.size()))
        dataSize = qdata.size() - 16

        check_md5 = qdata.data()[:dataSize]
        check_md5 += int(dataSize).to_bytes(4, "little")
        check_md5 += int(version).to_bytes(4, "little")
        check_md5 += magic
        check_md5 = hashlib.md5(check_md5)

        md5 = qdata.data()[dataSize:]

        if check_md5.hexdigest() != md5.hex():
            file.close()
            raise KeyFileInvalidChecksum(
                f"Invalid checksum {check_md5.hexdigest()} in file {filename}")

        qstream = QDataStream(qdata)

        salt = qstream.readBytes()
        key_encrypted = qstream.readBytes()

        return salt, key_encrypted


class CacheDecryptor:
    def __init__(self, key: bytes) -> None:
        self.__key = key

    @staticmethod
    def __ctr256_decrypt(src: bytes, key: bytes, iv: bytes) -> bytes:
        return tgcrypto.ctr256_decrypt(src, key, iv, bytes(1))

    async def Decrypt(self, filepath) -> bytes:
        filename = os.path.basename(filepath)
        async with aiofiles.open(filepath, 'rb') as f:
            magic = await f.read(4)
            if magic != TDEF_MAGIC:
                raise CacheFileInvaildMagic(
                    f"Invalid magic {magic} in file {filename}")

            salt = await f.read(64)

            real_key = hashlib.sha256(
                self.__key[:len(self.__key)//2] + salt[:32]).digest()
            iv = hashlib.sha256(
                self.__key[len(self.__key)//2:] + salt[32:]).digest()[:16]

            # don't ask...
            encrypted = await f.read(16 + 32)
            decrypted = self.__ctr256_decrypt(encrypted, real_key, iv)

            checksum = hashlib.sha256(
                self.__key + salt + decrypted[:16]).digest()

            if checksum != decrypted[16:]:
                raise LocalKeyInvalidChecksum('Wrong key!')

            encrypted_data = await f.read()
            decrypted_data = self.__ctr256_decrypt(
                encrypted_data, real_key, iv)

            return decrypted_data
