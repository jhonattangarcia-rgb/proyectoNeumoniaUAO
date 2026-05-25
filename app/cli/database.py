"""Database helpers for CLI workflows."""

from __future__ import annotations
from pathlib import Path
from typing import Set

import pandas as pd

from .utils import ensure_folder

DATABASE_COLUMNS = ["cedula", "label", "probability", "fecha"]

def load_database(database_path: Path) -> pd.DataFrame:
    """Load the Excel database and normalize expected columns.

    Args:
        database_path: Path to the Excel database file.

    Returns:
        A pandas DataFrame containing the registered records.
    """
    if database_path.exists():
        df = pd.read_excel(database_path, engine="openpyxl")
        for column in DATABASE_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        return df[DATABASE_COLUMNS]

    return pd.DataFrame(columns=DATABASE_COLUMNS)


def save_database(database_path: Path, df: pd.DataFrame) -> None:
    """Save the DataFrame to the Excel database path.

    Args:
        database_path: Path to the Excel database file.
        df: DataFrame with records to write.
    """
    ensure_folder(database_path.parent)
    df.to_excel(database_path, index=False, engine="openpyxl")


def get_recent_cedulas(existing_data: pd.DataFrame, delta_days: int) -> Set[str]:
    """Get a set of recently processed patient IDs.

    Args:
        existing_data: Existing database records.
        delta_days: Days threshold for recent processing.

    Returns:
        A set of patient IDs that appear in the recent interval.
    """
    if existing_data.empty:
        return set()
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=delta_days)
    recent_rows = existing_data.loc[existing_data["fecha"] >= cutoff]
    return set(recent_rows["cedula"].astype(str).tolist())
