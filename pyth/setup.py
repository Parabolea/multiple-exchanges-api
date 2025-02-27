import logging
import sys

def setup_logging():
    logging.basicConfig(format='internal - %(asctime)s - %(levelname)s: %(message)s', level=logging.INFO, handlers=[logging.StreamHandler(sys.stderr)])