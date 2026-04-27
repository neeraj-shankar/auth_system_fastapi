

## Troubleshooting

### Alembic Script location - Not found
- This means Alembic can't find or read its **alembic.ini** config file properly.

#### Fix 1:
- If you skipped alembic init, run it now:
```bash
alembic init alembic
```
#### Fix 2: 
- **alembic.ini** exists but is missing script_location. Then Open alembic.ini and make sure this line exists (not commented out):

```ini
[alembic]
script_location = alembic   # ← this must be here
```

#### Fix 3: Using a custom config file path
- If your ini file has a different name or location, pass it explicitly:

```bash
alembic -c path/to/your_alembic.ini revision --autogenerate -m "create_users_table"
```

### App module cannot be located by Alembic: ModuleNotFoundError: No module named 'app'
- When Alembic runs `env.py`, Python's sys.path doesn't include your project root, so it can't find the app module.

- **Fix** — Add project root to sys.path at the top of alembic/env.py:
```python
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# ↑ adjust the '..' count based on where your env.py lives

from app.config import settings  # now this will work
```


