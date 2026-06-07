from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

path_db = DATA_DIR / "bot.db"
path_log = LOG_DIR / "bot.log"
path_all_log = LOG_DIR / "bot_all.log"
