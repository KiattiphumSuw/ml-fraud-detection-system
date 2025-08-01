from typing import List

import yaml
from pydantic import BaseModel, Field


class BasicSettings(BaseModel):
    """
    General settings loaded from a YAML config.

    Args:
        DB_NAME (str): Name of the target database.
        DB_HOST (str): Host address of the database.
        DB_PORT (int): Port number on which the database listens.
        MODEL_WEIGHT_PATH (str): File path to the model weights.
        FEATURE_COLS (List[str]): Columns used for model features.
    """

    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    MODEL_WEIGHT_PATH: str
    FEATURE_COLS: List[str] = Field(..., description="Columns used for model features")


def load_basic_settings(path: str = "config.yaml") -> BasicSettings:
    """
    Load basic settings from a YAML file into a Pydantic model.

    Args:
        path (str): Relative or absolute path to the YAML config file. Defaults to "config.yaml".

    Returns:
        BasicSettings: An instance populated with values from the YAML file.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return BasicSettings(**data)
