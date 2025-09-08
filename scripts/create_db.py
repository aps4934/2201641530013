import sys
from pathlib import Path
# ensure project root is on sys.path so "src" package can be imported when running script directly
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.models.url_model import Base
from sqlalchemy import create_engine

# create sqlite DB file in project root
engine = create_engine('sqlite:///db.sqlite', echo=False)
Base.metadata.create_all(engine)
print("Database created: db.sqlite")