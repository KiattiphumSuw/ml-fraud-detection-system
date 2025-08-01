from typing import Tuple

from fastapi import Request, status

from api.services.frauds_service import FraudsService
from lib.common import logger
from lib.models import (
    TransactionAPIRequest,
    TransactionAPIResponse,
    TransactionsAPIResponse,
)


class FraudsController:
    """
    HTTP controller for fraud-related endpoints.

    Args:
        service (FraudsService): Service layer handling fraud prediction logic.
    """

    def __init__(self, service: FraudsService):
        self.service = service
        logger.info(
            "FraudsController initialized",
            extra={"service": getattr(service, "__class__", type(service)).__name__},
        )

    async def predict(
        self,
        request: TransactionAPIRequest,
        http_request: Request,
    ) -> Tuple[TransactionAPIResponse, int]:
        """
        Handle POST /predict.

        Args:
            request (TransactionAPIRequest): Pydantic model carrying the transaction to predict.
            http_request (Request): FastAPI request object, for logging client info.

        Returns:
            Tuple[TransactionAPIResponse, int]:
                - TransactionAPIResponse: The prediction result and original transaction.
                - int: HTTP status code (200).
        """
        # Log incoming request
        txn_payload = request.transaction.dict()
        logger.info(
            "Incoming predict request",
            extra={
                "client": http_request.client.host,
                "path": str(http_request.url),
                "payload": txn_payload,
            },
        )

        # Delegate to service
        response = self.service.predict(request)

        # Log outgoing response
        logger.info(
            "Predict response",
            extra={
                "client": http_request.client.host,
                "status": status.HTTP_200_OK,
                "response": response.dict(),
            },
        )
        return response, status.HTTP_200_OK

    async def get_frauds(
        self, http_request: Request
    ) -> Tuple[TransactionsAPIResponse, int]:
        """
        Handle GET /frauds.

        Args:
            http_request (Request): FastAPI request object, for logging client info.

        Returns:
            Tuple[TransactionsAPIResponse, int]:
                - TransactionsAPIResponse: Mapping of record IDs to prediction responses.
                - int: HTTP status code (200).
        """
        # Log invocation
        logger.info(
            "Incoming get_frauds request",
            extra={
                "client": http_request.client.host,
                "path": str(http_request.url),
            },
        )

        # Delegate to service
        response = self.service.get_frauds()

        # Log result count
        count = len(response.transactions)
        logger.info(
            "Return all previously transactions predicted",
            extra={
                "client": http_request.client.host,
                "status": status.HTTP_200_OK,
                "fraud_count": count,
            },
        )
        return response, status.HTTP_200_OK
