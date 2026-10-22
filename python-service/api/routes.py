"""Adaptador HTTP: validación, enrutamiento y traducción de errores."""
from fastapi import APIRouter, HTTPException
from api.schemas import ChatInput, EstimateInput
from application.services import answer_chat, estimate_price
from model import CATEGORIES, DISTRICTS, trained

router = APIRouter()

@router.get('/health')
def health():
    return {'status':'ok', 'synthetic':True, 'categories':CATEGORIES, 'districts':DISTRICTS, 'metrics':trained()[2]}

@router.post('/chat')
def chat(body: ChatInput):
    try:
        return answer_chat(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post('/estimate')
def predict(body: EstimateInput):
    try:
        return estimate_price(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
