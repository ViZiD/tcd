import sys
import logging
import asyncio

from . import App


def setup_log() -> None:
    """
    Setup root logger of the application.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    e_handler = logging.StreamHandler(sys.stdout)
    e_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    root.addHandler(e_handler)


async def app() -> None:
    try:
        setup_log()
        app = App()
        await app.run()
    except Exception as ex:
        print(f"An error occurred while running application: {ex}")


def main():
    asyncio.run(app())


if __name__ == "__main__":
    main()
