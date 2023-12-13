from typing import List
import json

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
    with open('service/data/tfidf_userknn_popular_model_1.json', "r", encoding="utf8") as file:
        TFIDF_USERKNN_POPULAR_RECOS = json.loads(file.read())
    with open('service/data/lightfm_recos_final_2.json', "r", encoding="utf8") as file:
        LIGHTFM_RECOS = json.loads(file.read())
    POPULAR_RECOS = [202457, 193123, 132865, 122119, 91167, 74803, 68581, 55043, 45367, 40372]
    if model_name == 'dummy_model':
        reco = list(range(k_recs))
    elif model_name == 'tfidf_userknn_popular_model':
        reco = TFIDF_USERKNN_POPULAR_RECOS.get(str(user_id), POPULAR_RECOS)
    elif model_name == 'lightfm_model':
        reco = LIGHTFM_RECOS.get(str(user_id), POPULAR_RECOS)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
