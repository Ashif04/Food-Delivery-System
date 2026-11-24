# Database migrations

Alembic uses the application's SQLAlchemy `Base` metadata and the database URL
from `app.db.session`, which loads settings through `app.core.config`. Keep
database credentials in the ignored `.env` file; do not put them in
`alembic.ini` or migration files.

Run commands from the `backend` directory with its virtual environment:

```powershell
.\venv\Scripts\python.exe -m alembic <command>
```

## Baseline the existing database

The existing database already has the schema represented by the 34 application
tables. `baseline_0001` is deliberately empty: it does not create, alter, or
drop application tables. Do not generate or apply an initial migration that
recreates those tables.

Before stamping, compare the live schema to model metadata with this
read-only preview. An unversioned database cannot use `alembic revision
--autogenerate` yet because Alembic requires the database to be at the current
revision. This preview does not require a stamped revision and does not write
to the database:

```powershell
@'
from alembic.autogenerate import produce_migrations, render_python_code
from alembic.migration import MigrationContext
from app.db.base_class import Base
from app.db.session import engine
import app.models

with engine.connect() as connection:
    context = MigrationContext.configure(
        connection, opts={"target_metadata": Base.metadata}
    )
    migration = produce_migrations(context, Base.metadata)
    if migration.upgrade_ops.is_empty():
        print("No schema changes detected.")
    else:
        print(render_python_code(migration.upgrade_ops))
        print("--- downgrade preview ---")
        print(render_python_code(migration.downgrade_ops))
'@ | .\venv\Scripts\python.exe -
```

Only stamp after the preview reports no changes (or after any differences have
been investigated and resolved). Never apply a generated preview as the
baseline.

Once the preview is empty and the target database is confirmed, record the
baseline without running schema migrations:

```powershell
.\venv\Scripts\python.exe -m alembic stamp baseline_0001
.\venv\Scripts\python.exe -m alembic current
```

`stamp` records the revision in Alembic's `alembic_version` tracking table; it
does not run `upgrade()` and does not change the existing application tables or
their data. This baseline stamp is a one-time bookkeeping step, not a schema
migration. Setup does not run it automatically.

## Future migration workflow

After changing models, generate a migration and inspect the generated Python
file before applying it:

```powershell
.\venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe the change"
```

Review both `upgrade()` and `downgrade()` for correctness, unintended operations,
and data-safety. Then apply only after approval:

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
```

Check the current revision and migration history:

```powershell
.\venv\Scripts\python.exe -m alembic current
.\venv\Scripts\python.exe -m alembic history --verbose
```

To roll back one revision only when its reviewed `downgrade()` is safe and a
recovery plan is in place:

```powershell
.\venv\Scripts\python.exe -m alembic downgrade -1
```
