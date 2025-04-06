#!/bin/bash
set -e

# Fix import issues
sed -i 's/from database import get_db, init_db, create_initial_data/from src.web.api.database import get_db, init_db, create_initial_data/' /app/src/web/api/main.py
sed -i 's/from routers import auth, containers, images, backup, monitoring, chat, websocket/from src.web.api.routers import auth, containers, images, backup, monitoring, chat, websocket/' /app/src/web/api/main.py
sed -i 's/from models import Base/from src.web.api.models import Base/' /app/src/web/api/database.py
sed -i 's/from models import __all__/from src.web.api.models import __all__/' /app/src/web/api/database.py
sed -i 's/from models import User, Role, Permission/from src.web.api.models import User, Role, Permission/' /app/src/web/api/database.py

# Set environment variables
export PYTHONPATH=/app

# Run the server directly
cd /app
python -m src.web.api.main
