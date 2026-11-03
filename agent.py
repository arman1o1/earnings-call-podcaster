import os
import sys
import pathlib
from dotenv import load_dotenv, find_dotenv

# Automatically load environment variables (.env)
load_dotenv(find_dotenv())

# Ensure current directory is in sys.path
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from agents.root_agent import root_agent

# Standard ADK entry point
agent = root_agent
