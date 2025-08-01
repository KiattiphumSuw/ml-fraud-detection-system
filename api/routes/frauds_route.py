from fastapi import APIRouter, Depends, Request, Response, status

from api.controllers import FraudsController
from api.dependencies import get_frauds_controller
from lib.models import (
    TransactionAPIRequest,
    TransactionAPIResponse,
    TransactionsAPIResponse,
)

router = APIRouter(tags=["MODEL_SERVING"])


@router.post(
    "/predict",
    status_code=status.HTTP_200_OK,
    summary="Predict fraud on a transaction",
    description="""
Accepts a single transaction payload and returns a model-predicted fraud flag.

Workflow:
1. Validates that the request body matches the TransactionAPIRequest schema.
2. Controller invokes the ML model to predict fraud.
3. Prediction is persisted in the database.
4. Returns the original transaction plus the `predicted_fraud` flag.
""",
    response_description="A JSON object containing the original transaction and the fraud prediction flag.",
    responses={
        200: {
            "description": "Prediction successful",
            "content": {
                "application/json": {
                    "example": {
                        "transaction": {
                            "time_ind": 42,
                            "transac_type": "TRANSFER",
                            "amount": 1234.56,
                            "src_acc": "acc123",
                            "src_bal": 5000.0,
                            "src_new_bal": 3765.44,
                            "dst_acc": "acc456",
                            "dst_bal": 1000.0,
                            "dst_new_bal": 2234.56,
                        },
                        "predicted_fraud": False,
                    }
                }
            },
        },
        400: {
            "description": "Bad request — invalid transaction payload",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation error: field 'amount' is required"
                    }
                }
            },
        },
        422: {
            "description": "Unprocessable entity — type mismatch or malformed JSON",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "transaction", "amount"],
                                "msg": "value is not a valid float",
                                "type": "type_error.float",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error — unexpected failure during prediction or persistence",
            "content": {
                "application/json": {
                    "example": {"detail": "Unexpected error: database connection lost"}
                }
            },
        },
    },
    response_model=TransactionAPIResponse,
)
async def predict_fraudulent_transaction(
    http_request: Request,
    request: TransactionAPIRequest,
    response: Response,
    controller: FraudsController = Depends(get_frauds_controller),
):
    result, status_code = await controller.predict(request, http_request)
    response.status_code = status_code
    return result


@router.get(
    "/frauds",
    status_code=status.HTTP_200_OK,
    summary="List all predicted frauds",
    description="""
Retrieves all past fraud predictions, ordered newest first.

Workflow:
1. Controller fetches all persisted TransactionRecord entries.
2. Maps each record to TransactionAPIResponse.
3. Returns a mapping of record IDs to their prediction responses.
""",
    response_description="A JSON object mapping record IDs to their transaction data and fraud flags.",
    responses={
        200: {
            "description": "Fetch successful",
            "content": {
                "application/json": {
                    "example": {
                        "transactions": {
                            "101": {
                                "transaction": {
                                    "time_ind": 10,
                                    "transac_type": "PAYMENT",
                                    "amount": 250.0,
                                    "src_acc": "acc001",
                                    "src_bal": 1000.0,
                                    "src_new_bal": 750.0,
                                    "dst_acc": "acc002",
                                    "dst_bal": 500.0,
                                    "dst_new_bal": 750.0,
                                },
                                "predicted_fraud": False,
                            },
                            "102": {
                                "transaction": {
                                    "time_ind": 11,
                                    "transac_type": "CASH_OUT",
                                    "amount": 5000.0,
                                    "src_acc": "acc003",
                                    "src_bal": 8000.0,
                                    "src_new_bal": 3000.0,
                                    "dst_acc": "acc004",
                                    "dst_bal": 100.0,
                                    "dst_new_bal": 5100.0,
                                },
                                "predicted_fraud": True,
                            },
                        }
                    }
                }
            },
        },
        500: {
            "description": "Internal server error — unable to retrieve records",
            "content": {
                "application/json": {
                    "example": {"detail": "Unexpected error: failed to query database"}
                }
            },
        },
    },
    response_model=TransactionsAPIResponse,
)
async def get_fraudulent_transactions(
    http_request: Request,
    response: Response,
    controller: FraudsController = Depends(get_frauds_controller),
):
    result, status_code = await controller.get_frauds(http_request)
    response.status_code = status_code
    return result
