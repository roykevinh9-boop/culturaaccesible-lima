"""Modelo académico reproducible. Los 40 precios son sintéticos, no precios reales."""
from functools import lru_cache
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, f1_score

CATEGORIES = ["Teatro", "Museo", "Danza", "Música", "Exposición"]
DISTRICTS = ["Miraflores", "Cercado de Lima"]
DATA = Path(__file__).parent / "data" / "precios_sinteticos.csv"

def dataset():
    return pd.read_csv(DATA)

def processor():
    return ColumnTransformer([("category", OneHotEncoder(handle_unknown="error"), ["categoria", "distrito"])], remainder="passthrough")

@lru_cache(maxsize=1)
def trained():
    frame = dataset()
    x = frame[["categoria", "distrito", "mes"]]
    y = frame.precio_soles
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=.25,random_state=42)
    regression = make_pipeline(processor(), LinearRegression()).fit(x_train,y_train)
    mae = float(mean_absolute_error(y_test, regression.predict(x_test)))
    classes=(y<=40).astype(int)
    cx_train,cx_test,cy_train,cy_test=train_test_split(x,classes,test_size=.25,random_state=42,stratify=classes)
    classification=make_pipeline(processor(),DecisionTreeClassifier(max_depth=3,random_state=42)).fit(cx_train,cy_train)
    predicted=classification.predict(cx_test)
    metrics={"mae_soles":round(mae,3),"accuracy":round(float(accuracy_score(cy_test,predicted)),3),"f1_hasta_40":round(float(f1_score(cy_test,predicted,zero_division=0)),3),"training":30,"test":10,"records":40,"synthetic":True,"seed":42,"note":"Métricas de esta nueva demostración, no reproducción de los resultados del informe anterior."}
    return regression,classification,metrics

def estimate(category,district,month):
    if category not in CATEGORIES or district not in DISTRICTS:
        raise ValueError("Categoría o distrito sin cobertura.")
    if isinstance(month,bool) or not isinstance(month,int) or not 1<=month<=12:
        raise ValueError("El mes debe ser un entero de 1 a 12.")
    regression,classification,metrics=trained()
    row=pd.DataFrame([{"categoria":category,"distrito":district,"mes":month}])
    price=round(float(regression.predict(row)[0]),2)
    if not math.isfinite(price) or price<0:
        raise ValueError("El modelo no produjo un precio válido.")
    group=bool(classification.predict(row)[0])
    return {"estimated_price":price,"predicted_range":"Hasta S/ 40" if group else "Mayor de S/ 40","models_disagree":group!=(price<=40),"synthetic":True,"currency":"PEN","message":"Demostración con 40 precios ficticios. Estimación orientativa: verifica el precio oficial. No constituye una oferta ni confirma apoyos de accesibilidad.","model":"Regresión lineal + árbol de decisión","metrics":metrics}

if __name__ == "__main__":
    print(json.dumps(trained()[2],ensure_ascii=False,indent=2))
