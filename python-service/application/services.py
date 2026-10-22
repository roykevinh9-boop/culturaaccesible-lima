"""Casos de uso; no importan FastAPI ni conocen solicitudes HTTP."""
from assistant import reply
from model import estimate

def answer_chat(body):
    if not body.message.strip():
        raise ValueError('Escribe una consulta.')
    return reply(body.message, body.context.model_dump(mode='json', exclude_none=True, exclude_defaults=True),
                 [item.model_dump(mode='json') for item in body.items], body.today)

def estimate_price(body):
    return estimate(body.categoria, body.distrito, body.mes)
