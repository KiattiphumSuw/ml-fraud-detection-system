from typing import Dict, List

import pandas as pd

from lib.common import logger
from lib.models import (
    Transaction,
    TransactionAPIRequest,
    TransactionAPIResponse,
    TransactionRecord,
    TransactionsAPIResponse,
)
from lib.repositories import FraudRepository


class FraudsService:
    """
    Service layer for handling fraud detection workflow:
      - Transform incoming transactions into model-ready format
      - Execute ML predictions
      - Persist prediction results
      - Format responses for API

    Args:
        repository (FraudRepository): Repository for database operations.
        model: AI/ML model instance implementing .predict() interface.
        feature_cols (List[str]): Ordered list of feature column names for prediction.
    """

    def __init__(self, repository: FraudRepository, model, feature_cols: List[str]):
        """
        Initialize the FraudsService with dependencies.

        Args:
            repository (FraudRepository): Repository for DB interactions.
            model: Trained ML model with a .predict() method.
            feature_cols (List[str]): Feature column names used for model input.
        """
        self.repo = repository
        self.model = model
        self.feature_cols = feature_cols
        logger.info(
            "FraudsService initialized",
            extra={
                "repository": str(repository),
                "model": getattr(model, "__class__", type(model)).__name__,
                "feature_cols": feature_cols,
            },
        )

    def predict(self, request: TransactionAPIRequest) -> TransactionAPIResponse:
        """
        Run a fraud prediction on a single transaction and persist the result.

        Args:
            request (TransactionAPIRequest): Pydantic request containing transaction data.

        Returns:
            TransactionAPIResponse: Pydantic response with original transaction and fraud flag.
        """
        txn: Transaction = request.transaction
        logger.info(
            "Predict called",
            extra={
                "transaction_id": txn.dict().get("time_ind"),
                "input_payload": txn.dict(),
            },
        )

        # 1) Prepare DataFrame
        df = pd.DataFrame([txn.dict()], columns=self.feature_cols)
        logger.debug(
            "Constructed DataFrame for prediction",
            extra={"df_head": df.head(1).to_dict(orient="records")},
        )

        # 2) Execute model
        prediction_array = self.model.predict(df)
        predicted = bool(prediction_array[0])
        logger.info(
            "Model prediction complete",
            extra={
                "prediction_array": (
                    prediction_array.tolist()
                    if hasattr(prediction_array, "tolist")
                    else list(prediction_array)
                ),
                "predicted_label": predicted,
            },
        )

        # 3) Persist prediction
        db_rec = TransactionRecord(**txn.dict(), is_fraud=predicted)
        self.repo.add(db_rec)
        logger.info(
            "Prediction saved to database",
            extra={"record_id": getattr(db_rec, "id", None), "is_fraud": predicted},
        )

        # 4) Build response
        response = TransactionAPIResponse(
            transaction=txn,
            predicted_fraud=predicted,
        )
        logger.info(
            "Returning prediction response",
            extra={"response_payload": response.dict()},
        )
        return response

    def get_frauds(self) -> TransactionsAPIResponse:
        """
        Retrieve all persisted fraud predictions, newest first.

        Returns:
            TransactionsAPIResponse: Pydantic wrapper containing a dict of ID to responses.
        """
        logger.info("Fetching all fraud records")
        db_rows = self.repo.list_all()
        logger.info(
            "Fetched records",
            extra={"count": len(db_rows)},
        )

        result: Dict[int, TransactionAPIResponse] = {}
        for rec in db_rows:
            txn = Transaction.from_orm(rec)
            response_obj = TransactionAPIResponse(
                transaction=txn,
                predicted_fraud=rec.is_fraud,
            )
            result[rec.id] = response_obj
            logger.debug(
                "Mapped DB record to response",
                extra={
                    "record_id": rec.id,
                    "transaction": txn.dict(),
                    "predicted_fraud": rec.is_fraud,
                },
            )

        final_response = TransactionsAPIResponse(transactions=result)
        logger.info(
            "Returning all fraud transactions response",
            extra={"response_count": len(final_response.transactions)},
        )
        return final_response
