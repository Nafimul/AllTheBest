import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from myapp import create_app

app = create_app(os.getenv("FLASK_ENV", "production"))