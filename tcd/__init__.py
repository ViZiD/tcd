import logging
import os
import aiofiles
import aiofiles.os

from .crypto import EncryptionKey, CacheDecryptor
from .exceptions import DirNotExist, FileNotExist


class TCD:
    def __init__(self, basepath: str, password: str) -> None:
        """
        Main constructor of the TCD class
        :param basepath: path to telegram cache
        :param password: telegram desktop passlock
        """
        self.__basepath = basepath
        self.__password = password

        self.__key_path = os.path.join(self.__basepath, 'key_datas')

        self.__check_basepath_exist()
        self.__check_keyfile_exist()
        self.__decrypt_key()
        self.__setLogger()

    def __setLogger(self) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

    def __check_basepath_exist(self) -> None:
        if not os.path.exists(self.__basepath):
            raise DirNotExist(f'{self.__basepath} not exist!')

    def __check_keyfile_exist(self) -> None:
        if not os.path.exists(self.__key_path):
            raise FileNotExist(f'Key file not exist! {self.__key_path}')

    def __decrypt_key(self) -> None:
        """
        Get local key from key_datas
        """
        salt, key = EncryptionKey.ReadKeyData(self.__key_path)
        localkey = EncryptionKey.CreateLocalKey(
            bytes(self.__password, encoding='utf8'), salt)
        key = EncryptionKey.DecryptLocal(key, localkey)
        self.__cache = CacheDecryptor(key)

    async def __getdecryptedfile(self, file: str) -> bytes:
        """
        Get decrypted file in bytes
        :param file: path to file
        :exception FileNotExist: Cache file not exist
        :return: decrypted file in bytes
        :rtype: bytes
        """
        if not await aiofiles.os.path.exists(file):
            raise FileNotExist(f'Cache file not exist! {file}')

        decrypted = await self.__cache.Decrypt(file)
        return decrypted

    async def __savefile(self, savepath: str, filename: str, data: bytes) -> None:
        """
        Save decrypted cache to file
        :param savepath: path where to file save
        :param filename: name for decrypted file
        :param data: decrypted file in bytes
        """
        await aiofiles.os.makedirs(savepath, exist_ok=True)

        newfile = os.path.join(savepath, filename)
        async with aiofiles.open(newfile, 'wb') as f:
            await f.write(data)

    async def decryptall(self, savepath: str) -> None:
        """
        Main method for decrypting all user_data folder and save
        :param savepath: directory for saving cache
        """
        user_data = os.path.join(self.__basepath, 'user_data')
        if not os.path.exists(user_data):
            raise DirNotExist(f'User data directory not exist! {user_data}')

        for root, _, files in os.walk(user_data):
            if files:
                subdir = root[len(self.__basepath):].lstrip('/')
                newdir = os.path.join(savepath, subdir)
                for name in files:
                    if name in ['version', 'binlog']:
                        continue
                    cache_path = os.path.join(root, name)
                    data = await self.__getdecryptedfile(cache_path)
                    await self.__savefile(newdir, name, data)
                    self.__logger.info(
                        f'File {name} decrypted, save in {newdir}')
