from typing import List

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing_extensions import Annotated

from service.api.exceptions import AuthorizationError, ModelNotFoundError, UserNotFoundError
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
security = HTTPBearer()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={401: {"description": "Unauthorized"}, 404: {"description": "Not Found"}},
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    list_models = request.app.state.list_models
    if model_name not in list_models:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    valid_token = request.app.state.valid_token
    if credentials.credentials != valid_token:
        raise AuthorizationError(error_message="Invalid token")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
