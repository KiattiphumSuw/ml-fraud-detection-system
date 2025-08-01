from fastapi import Request

from api.controllers import FraudsController


def get_frauds_controller(request: Request) -> FraudsController:
    """
    Dependency injector for the FraudsController.

    Args:
        request (Request): The FastAPI request object, used to access application state.

    Returns:
        FraudsController: The controller instance stored on `app.state`.
    """
    return request.app.state.fraud_controller
