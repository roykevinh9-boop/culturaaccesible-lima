from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from model import CATEGORIES, DISTRICTS, estimate, trained

app=FastAPI(title="CulturaAccesible Lima: precios orientativos",version="1.0.0",description="Demostración académica con datos sintéticos.")

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
