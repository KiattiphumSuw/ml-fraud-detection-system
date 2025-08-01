from datetime import datetime
from typing import Optional

from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


class TransactionBase(SQLModel):
    """
    Shared fields for both ORM & Pydantic.

    Args:
        time_ind (int): Time index of the transaction.
        transac_type (str): Type of transaction (e.g., PAYMENT, TRANSFER).
        amount (float): Transaction amount.
        src_acc (str): Source account identifier.
        src_bal (float): Source account balance before transaction.
        src_new_bal (float): Source account balance after transaction.
        dst_acc (str): Destination account identifier.
        dst_bal (float): Destination account balance before transaction.
        dst_new_bal (float): Destination account balance after transaction.
    """

    time_ind: int
    transac_type: str
    amount: float
    src_acc: str
    src_bal: float
    src_new_bal: float
    dst_acc: str
    dst_bal: float
    dst_new_bal: float


class TransactionRecord(TransactionBase, table=True):
    """
    ORM model for storing transaction predictions.

    Args:
        id (Optional[int]): Primary key of the record.
        time_ind (int): Time index of the transaction.
        transac_type (str): Type of transaction.
        amount (float): Transaction amount.
        src_acc (str): Source account identifier.
        src_bal (float): Source account balance before transaction.
        src_new_bal (float): Source account balance after transaction.
        dst_acc (str): Destination account identifier.
        dst_bal (float): Destination account balance before transaction.
        dst_new_bal (float): Destination account balance after transaction.
        is_fraud (bool): Flag indicating whether the transaction is fraudulent.
        predicted_at (datetime): Timestamp when the prediction was made.
    """

    __tablename__ = "predicted_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    is_fraud: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": text("FALSE")},
    )
    predicted_at: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("NOW()"),
            nullable=False,
        ),
    )


class Transaction(TransactionBase):
    """
    Pydantic schema for incoming/outgoing payloads.
    (No `table=True`, so it doesn’t create a DB table.)

    Args:
        time_ind (int): Time index of the transaction.
        transac_type (str): Type of transaction (e.g., PAYMENT, TRANSFER).
        amount (float): Transaction amount.
        src_acc (str): Source account identifier.
        src_bal (float): Source account balance before transaction.
        src_new_bal (float): Source account balance after transaction.
        dst_acc (str): Destination account identifier.
        dst_bal (float): Destination account balance before transaction.
        dst_new_bal (float): Destination account balance after transaction.
    """

    pass
