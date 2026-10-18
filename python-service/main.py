from fastapi import FastAPI, HTTPException
from typing import Literal
from datetime import date
from assistant import reply
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator
from model import CATEGORIES, DISTRICTS, estimate, trained

app=FastAPI(title="CulturaAccesible Lima: precios orientativos",version="1.0.0",description="Demostración académica con datos sintéticos.")

class ChatContext(BaseModel):
    model_config=ConfigDict(extra='forbid')
    month: StrictInt|None=Field(default=None,ge=1,le=12)
    day: StrictInt|None=Field(default=None,ge=1,le=31)
    year: StrictInt|None=Field(default=None,ge=2000,le=2099)
    date_from: date|None=None
    date_to: date|None=None
    category: str|None=Field(default=None,max_length=60)
    district: str|None=Field(default=None,max_length=80)
    venue: str|None=Field(default=None,max_length=160)
    q: str|None=Field(default=None,max_length=150)
    price: Literal['free']|None=None
    sort: Literal['asc','desc']|None=None
    min_price: float|None=Field(default=None,ge=0,le=100000,allow_inf_nan=False)
    max_price: float|None=Field(default=None,ge=0,le=100000,allow_inf_nan=False)
    needs: list[Literal['lsp','subtitulos','audiodescripcion','tactil','silla_ruedas','sin_escalones','bano_adaptado']]=Field(default_factory=list,max_length=7)
    @model_validator(mode='after')
    def complete_range(self):
        if bool(self.date_from)!=bool(self.date_to):raise ValueError('Indica ambas fechas del periodo.')
        if self.date_from and self.date_from>self.date_to:raise ValueError('El periodo no es válido.')
        return self

class ChatEvent(BaseModel):
    model_config=ConfigDict(extra='allow')
    id: StrictInt
    title: str
    date: date
    time: str|None=None
    category: str
    district: str
    venue: str
    address: str|None=None
    official_price: float|None=Field(default=None,ge=0,allow_inf_nan=False)
    conditions: list[dict]

class ChatInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    message: str=Field(min_length=1,max_length=600)
    context: ChatContext=Field(default_factory=ChatContext)
    items: list[ChatEvent]=Field(max_length=500)
    today: date

@app.post('/chat')
def chat(body:ChatInput):
    if not body.message.strip():raise HTTPException(status_code=422,detail='Escribe una consulta.')
    return reply(body.message,body.context.model_dump(mode='json',exclude_none=True,exclude_defaults=True),[f.model_dump(mode='json') for f in body.items],body.today)

class EstimateInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    categoria: str = Field(min_length=1,max_length=50)
    distrito: str = Field(min_length=1,max_length=60)
    mes: StrictInt = Field(ge=1,le=12)

@app.get("/health")
def health():
    return {"status":"ok","synthetic":True,"categories":CATEGORIES,"districts":DISTRICTS,"metrics":trained()[2]}

@app.post("/estimate")
def predict(body:EstimateInput):
    try:
        return estimate(body.categoria,body.distrito,body.mes)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
