
from dotenv import load_dotenv
load_dotenv(override=True)
from app import app
import callbacks as _

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
