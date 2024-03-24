"""
Main module for lolla
"""

import signal
import sys

from .parser import LollaConfig
from .lolla import LollaShell
from .log import LollaLogger
from .storage import LollaStorage

__version__ = "0.1.1"


def main():
    """
    Main function for lolla.
    """

    lolla_config = LollaConfig(app_version=__version__)
    args = lolla_config.parser.parse_args()

    logger = LollaLogger(level=args.log_level)

    def ctrl_c_handler(sig, frame):
        logger.info("Ctrl-C pressed. Use 'exit' or Ctrl-D to exit.")

    signal.signal(signal.SIGINT, ctrl_c_handler)

    storage = LollaStorage(home=args.home)

    LollaShell(app_version=__version__, logger=logger, storage=storage, args=args).cmdloop()


if __name__ == "__main__":
    main()
