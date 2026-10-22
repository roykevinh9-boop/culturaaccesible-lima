"""Punto de composición de FastAPI. Inicio: uvicorn main:app."""
from fastapi import FastAPI
from api.routes import router

app = FastAPI(title='CulturaAccesible Lima: precios orientativos', version='1.4.0',
              description='Demostración académica con datos sintéticos.')
app.include_router(router)
