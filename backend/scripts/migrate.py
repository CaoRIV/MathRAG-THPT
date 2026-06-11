from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from alembic import command
from app.core.config import get_settings

BASELINE_TABLES = {
    "documents",
    "chunks",
    "formulas",
    "conversations",
    "messages",
    "quizzes",
    "retrieval_logs",
}


def main() -> None:
    settings = get_settings()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", settings.database_url)

    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())
        current_revision = MigrationContext.configure(connection).get_current_revision()

    if current_revision is None and BASELINE_TABLES.issubset(tables):
        revision = "0002" if "users" in tables else "0001"
        print(
            "Detected a legacy MathRAG database; "
            f"stamping baseline revision {revision}."
        )
        command.stamp(config, revision)
    elif current_revision is None and tables - {"alembic_version"}:
        unknown = ", ".join(sorted(tables - BASELINE_TABLES - {"alembic_version"}))
        raise RuntimeError(
            "Database contains an unrecognized partial schema. "
            f"Unexpected tables: {unknown or 'none'}."
        )

    command.upgrade(config, "head")
    print("Database migration completed.")


if __name__ == "__main__":
    main()
