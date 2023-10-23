import asyncio

from src.core import Core


def main():
    core = Core()
    asyncio.run(core.run())


if __name__ == "__main__":
    main()
