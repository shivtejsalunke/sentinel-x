# Database migrations

The current baseline initializes the SQLite schema idempotently in `app/persistence/database.py` to keep local setup simple. For production or collaborative deployments, replace schema bootstrap with a versioned migration runner and record upgrade/downgrade tests. The `versions/` directory is reserved for migration scripts.
