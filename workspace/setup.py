import sys
import os
from dotenv import load_dotenv
from logging import getLogger, INFO, FileHandler, Formatter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
load_dotenv()

transaction_logger = getLogger("Transaction")
transaction_logger.setLevel(INFO)
transaction_log_handler = FileHandler(filename=os.environ.get("TRANSACTION_LOG_FILENAME"))
transaction_log_handler.setFormatter(Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
transaction_logger.addHandler(transaction_log_handler)

action_logger = getLogger("Action")
action_logger.setLevel(INFO)
action_log_handler = FileHandler(filename=os.environ.get("ACTION_LOG_FILENAME"))
action_log_handler.setFormatter(Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
action_logger.addHandler(action_log_handler)