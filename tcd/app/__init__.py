import logging
import argparse

from tcd import TCD
from ..exceptions import MissingArgumentError, DirNotExist, FileNotExist


class App:
    def __init__(self) -> None:
        """
        Main constructor of the App class
        """
        self.__setLogger()
        self.__parser_create()
        self.__parse_arguments()

    def __setLogger(self) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

    def __parser_create(self) -> None:
        self.__parser = argparse.ArgumentParser()
        self.__parser_add_arguments()

    def __parser_add_arguments(self) -> None:
        self.__parser.add_argument(
            '--tdata', '-d', help='Path to Telegram Desktop cache folder', type=str, required=True, metavar='/path/to/tdata')
        self.__parser.add_argument(
            '--savedir', '-s', help='Path where decrypted cache will be saved', type=str, required=True, metavar='/path/to/save')
        self.__parser.add_argument(
            '--password', '-p', help='Passlock for Telegram Desktop', default='', type=str, metavar='passlock')

    def __parse_arguments(self) -> None:
        self.__arguments = self.__parser.parse_args()

    def __check_arguments(self) -> None:
        if not (self.__arguments.tdata or self.__arguments.savedir):
            raise MissingArgumentError(
                'Missing arguments!\n')

    async def run(self) -> None:
        try:
            self.__check_arguments()
            tcd = TCD(self.__arguments.tdata, self.__arguments.password)
            await tcd.decryptall(self.__arguments.savedir)
        except (DirNotExist, FileNotExist) as notexist:
            self.__logger.error(notexist)
        except MissingArgumentError as missing:
            self.__logger.error(missing)
            self.__parser.print_help()
        except (Exception, BaseException) as e:
            raise e
