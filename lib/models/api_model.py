from pydantic import BaseModel, Field

from .transaction_record_model import Transaction


class TransactionAPIRequest(BaseModel):
    """
    Input schema for a single transaction.

    Args:
        transaction (Transaction): The transaction data to be evaluated by the fraud model.
    """

    transaction: Transaction = Field(
        ...,
        description="Transaction data",
        example={
            "time_ind": 678,
            "transac_type": "TRANSFER",
            "amount": 1536733.52,
            "src_acc": "sample-account",
            "src_bal": 1536733.52,
            "src_new_bal": 0.0,
            "dst_acc": "sample-account",
            "dst_bal": 0.0,
            "dst_new_bal": 0.0,
        },
    )


class TransactionAPIResponse(BaseModel):
    """
    Output schema for a single transaction prediction.

    Args:
        transaction (Transaction): The original transaction data.
        predicted_fraud (bool): Flag indicating whether the model predicts this transaction is fraudulent.
    """

    transaction: Transaction = Field(..., description="Transaction data")
    predicted_fraud: bool = Field(..., description="Model-predicted fraud flag")


class TransactionsAPIResponse(BaseModel):
    """
    Wrapper schema for multiple transaction responses.

    Args:
        transactions (dict[int, TransactionAPIResponse]):
            A mapping from transaction ID to its corresponding prediction response.
    """

    transactions: dict[int, TransactionAPIResponse] = Field(
        ..., description="Return transactions and their IDs"
    )
