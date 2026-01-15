import logging
import sys

from your_module.adder import add

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to run some code."""
    logger.info(f"1 + 1 = {add(1, 1)}")
    logger.info("Wow! You ran some code!")
    logger.info(f"Python version: {sys.version}")


if __name__ == "__main__":
    main()
