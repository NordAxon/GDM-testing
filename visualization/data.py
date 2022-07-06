from src.aux_functions import create_connection, close_connection
from pathlib import Path
import pandas as pd
from sqlite3 import Error
import os
from dash import dash_table
from typing import List, Dict


def get_available_experiment_ids() -> List[str]:
    """Gets a list of all available experiments"""
    result_path = Path(__file__).parents[1] / f"test_results"
    ids = []
    for filename in os.listdir(result_path):
        if filename.endswith(".sqlite"):
            ids.append(filename.rstrip(".sqlite"))
    return ids


def get_data(experiment_id: str) -> Dict[str, pd.DataFrame]:
    """Gets output data for chosen experiment id

    Args:
        experiment_id (str): ID of experiment

    Returns:
        Dict[pd.DataFrame]: Dict with tables
    """
    db_path = Path(__file__).parents[1] / f"test_results/{experiment_id}.sqlite"
    conn = create_connection(db_path)
    try:
        configs = pd.read_sql("SELECT * FROM runs", conn)
        tox = pd.read_sql("SELECT * FROM TOX_results", conn)
        vocsz = pd.read_sql("SELECT * FROM VOCSZ_results", conn)
        coher = pd.read_sql("SELECT * FROM COHER_results", conn)
        readind = pd.read_sql("SELECT * FROM READIND_results", conn)
    except Error as e:
        print(e)
    finally:
        close_connection(conn)
    return {
        "configs": configs,
        "tox": tox,
        "vocsz": vocsz,
        "coher": coher,
        "readind": readind,
    }


def get_configs(experiment_id: str) -> pd.DataFrame:
    """Only fetches the configs dataframe

    Args:
        experiment_id (str): ID of experiment

    Returns:
        pd.DataFrame: Dataframe with run-configurations
    """
    db_path = Path(__file__).parents[1] / f"test_results/{experiment_id}.sqlite"
    conn = create_connection(db_path)
    try:
        configs = pd.read_sql("SELECT * FROM runs", conn)
    except Error as e:
        print(e)
    finally:
        close_connection(conn)
    return configs


def format_configs(configs: pd.DataFrame) -> dash_table.DataTable:
    """Formats the configs into a dash_table

    Args:
        configs (pd.DataFrame): Dataframe with run-configurations

    Returns:
        dash_table.DataTable: Formatted data_table
    """
    configs.date_time_generated = configs.date_time_generated.apply(lambda x: x[:19])
    configs.date_time_tested = configs.date_time_tested.apply(lambda x: x[:19])
    return dash_table.DataTable(
        style_header={"fontWeight": "bold", "color": "inherit"},
        style_as_list_view=True,
        fill_width=True,
        style_cell={
            "backgroundColor": "#1e2130",
            "fontFamily": "Open Sans",
            "padding": "0 2rem",
            "color": "darkgray",
            "border": "none",
        },
        css=[
            {"selector": "tr:hover td", "rule": "color: #91dfd2 !important;"},
            {"selector": "td", "rule": "border: none !important;"},
            {
                "selector": ".dash-cell.focused",
                "rule": "background-color: #1e2130 !important;",
            },
            {"selector": "table", "rule": "--accent: #1e2130;"},
            {"selector": "tr", "rule": "background-color: transparent"},
        ],
        data=configs.to_dict("rows"),
        columns=[{"id": c, "name": c} for c in configs.columns],
    )
