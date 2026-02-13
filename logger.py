# coding=utf-8
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        # logging.FileHandler("dash_app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TaskChecker")
