"""AccesI: clasificación de intención local y respuestas ancladas al catálogo recibido de Java.

No ejecuta SQL ni genera hechos: fechas, importes y apoyos se filtran sobre datos de MySQL.
El estado contiene solamente criterios de búsqueda y vuelve al cliente, sin guardar conversaciones.
"""
import re
import unicodedata
from datetime import date, timedelta
from functools import lru_cache
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
INTENTS={
 'greeting':['hola','buenas','buenos dias','buenas tardes','buenas noches','holaa','que tal','hey','saludos','hola accesi'],
 'thanks':['gracias','muchas gracias','te agradezco','muy amable','perfecto gracias','genial gracias','ok gracias','adios','hasta luego','nos vemos'],
 'help':['ayuda','que puedes hacer','como funciona','para que sirves','que es accesi','eres una inteligencia artificial','que sabes hacer','como te uso','explicame el asistente','como busco'],
 'location':['como llego al teatro','donde queda el museo','direccion del gran teatro nacional','transporte al mali','como ir al recinto','ubicacion del teatro','donde esta el mali','como llegar al museo','ruta al teatro','donde es'],
 'search':['eventos en noviembre','que hay hoy','teatro en octubre','los mas baratos','eventos caros','gratis este fin de semana','con lsp','museos con audiodescripcion','conciertos en diciembre','danza en san borja','el 18 de octubre','menos de 40 soles','quiero entradas','muestrame actividades','y los mas caros','cual es el precio','busca yuyachkani','eventos para silla de ruedas','planes el sabado','conciertos economicos'],
 'unrelated':['receta de cocina','resuelve mi tarea de matematicas','quien gano el partido','escribe un programa','cual es la capital de francia','como reparar mi auto','dame consejos de medicina','como invertir dinero','cuentame un chiste','el clima en madrid']
}

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')

@lru_cache(maxsize=1)
def intent_model():
    samples=[(text,intent) for intent,texts in INTENTS.items() for text in texts]
    model=make_pipeline(TfidfVectorizer(analyzer='char_wb',ngram_range=(2,5),strip_accents='unicode'),LogisticRegression(C=8,max_iter=600,random_state=42))
    model.fit([s[0] for s in samples],[s[1] for s in samples])
    return model

def intent(text):
    model=intent_model();prediction=str(model.predict([text])[0])
    confidence=float(max(model.predict_proba([text])[0]))
    return prediction,round(confidence,3)

def reply(message,context,items,today):
    text=norm(message).strip();state=dict(context)
    predicted,confidence=intent(text)
    def response(answer,results=None,total=0):
        return dict(reply=answer,items=results or [],total=total,context=state,intent=predicted,
                    engine='AccesI-local-tfidf-logistic-v1',confidence=confidence)
    greeting=r'(hola+|buenas(?: tardes| noches)?|buenos dias|hey|saludos|que tal)[!¡?. ,]*'
    if re.fullmatch(greeting,text):
        return response('¡Hola! Soy AccesI 👋 Te ayudo a encontrar actividades culturales de Lima por mes, día, precio y accesibilidad. Prueba «eventos baratos en noviembre» o «teatro el 18 de octubre». ¿Qué te gustaría hacer?')
    if re.fullmatch(r'(muchas )?gracias[!¡. ,]*|ok gracias|adios|hasta luego',text):
        return response('¡Con gusto! Cuando quieras, dime otra fecha, presupuesto o apoyo que necesites para tu visita.')
    if predicted=='help' and confidence>.3:
        return response('Puedo buscar la cartelera por mes o día, ordenar de barato a caro o al revés, aplicar un presupuesto y revisar apoyos como LSP o ingreso sin escalones. Recuerdo los filtros durante esta conversación: después de «eventos en noviembre», puedes decir «y los más baratos». Los resultados tienen ficha y fuente oficial. Uso IA local para reconocer intenciones y reglas para consultar los datos; no soy un modelo generativo.')
    if re.search(r'\b(sin filtros|empezar de nuevo|reinicia|otra busqueda|todos los eventos|todas las actividades)\b',text) or text in ['todos','todas']:state={}

    # Las fechas explícitas reemplazan el periodo previo. Un día aislado hereda mes y año.
    found_month=next((i+1 for i,m in enumerate(MONTHS) if re.search(r'\b'+m+r'\b',text)),None)
    if not found_month and re.search(r'este mes|proximo mes|mes siguiente',text):
        month=today.month+(1 if 'proximo mes' in text or 'mes siguiente' in text else 0)
        state.update(month=(month-1)%12+1,year=today.year+(month>12))
        for k in ['day','date_from','date_to']:state.pop(k,None)
    year_match=re.search(r'\b(20\d{2})\b',text)
    if found_month:
        state.update(month=found_month,year=int(year_match[1]) if year_match else today.year)
        for k in ['day','date_from','date_to']:state.pop(k,None)
    elif year_match:state['year']=int(year_match[1])
    numeric=re.search(r'\b(\d{1,2})[/-](\d{1,2})(?:[/-](20\d{2}))?\b',text)
    day_match=re.search(r'\b(?:el|dia)\s+(\d{1,2})(?!\d)',text)
    if numeric:
        state.update(day=int(numeric[1]),month=int(numeric[2]),year=int(numeric[3] or today.year))
        state.pop('date_from',None);state.pop('date_to',None)
    elif day_match:
        state.update(day=int(day_match[1]),month=state.get('month',today.month),year=state.get('year',today.year))
        state.pop('date_from',None);state.pop('date_to',None)
    if 'hoy' in text or 'manana' in text or 'fin de semana' in text:
        for k in ['day','month','year']:state.pop(k,None)
        start=today+timedelta(days=1 if 'manana' in text else 0)
        end=start
        if 'fin de semana' in text:
            start=today if today.weekday()==6 else today+timedelta(days=(5-today.weekday())%7)
            end=start if today.weekday()==6 else start+timedelta(days=1)
        state.update(date_from=start.isoformat(),date_to=end.isoformat())
    elif not day_match and not numeric and not found_month:
        weekday=next((i for i,name in enumerate(['lunes','martes','miercoles','jueves','viernes','sabado','domingo']) if re.search(r'\b'+name+r'\b',text)),None)
        if weekday is not None:
            selected=today+timedelta(days=(weekday-today.weekday())%7)
            for k in ['day','month','year']:state.pop(k,None)
            state.update(date_from=selected.isoformat(),date_to=selected.isoformat())
    try:
        if state.get('day'):date(state.get('year',today.year),state.get('month',today.month),state['day'])
    except ValueError:
        state.pop('day',None)
        if not 1<=state.get('month',1)<=12:state.pop('month',None)
        return response('Esa fecha no existe. Indica una fecha válida, por ejemplo «18 de octubre de 2026».')

    categories={'teatro':'Teatro','concierto':'Música','musica':'Música','danza':'Danza','ballet':'Danza','museo':'Museo','exposicion':'Exposición','charla':'Charla','visita':'Visita'}
    for word,value in categories.items():
        if re.search(r'\b'+word+r's?\b',text):state['category']=value;break
    for district in ['Miraflores','Cercado de Lima','San Borja','Barranco']:
        if norm(district) in text:state['district']=district;break
    if 'mali' in text:state['venue']='Museo de Arte de Lima'
    if 'gran teatro nacional' in text or re.search(r'\bgtn\b',text):state['venue']='Gran Teatro Nacional'
    if any(w in text for w in ['cualquier distrito','todos los distritos']):state.pop('district',None)
    if any(w in text for w in ['cualquier categoria','todas las disciplinas','cualquier tipo']):state.pop('category',None)
    # «Gran Teatro Nacional» no implica que la disciplina tenga que ser Teatro.
    if ('gran teatro nacional' in text or 'como llego al teatro' in text) and not re.search(r'\bteatro\b.*\ben\b',text):state.pop('category',None)
    support_rules={'lsp':['lsp','lengua de senas'],'subtitulos':['subtitulo','subtitulado'],'audiodescripcion':['audiodescripcion'],'tactil':['tactil'],'silla_ruedas':['silla de ruedas'],'sin_escalones':['sin escalones'],'bano_adaptado':['bano adaptado']}
    needs=[code for code,words in support_rules.items() if any(w in text for w in words)]
    if needs:state['needs']=needs
    if 'sin apoyos' in text or 'sin requisitos' in text:state.pop('needs',None)
    if re.search(r'\b(gratis|gratuito|gratuita|gratuitos|libre)\b',text):state.update(price='free');state.pop('min_price',None);state.pop('max_price',None)
    if re.search(r'barat|economic|menor precio|menos cost|mas accesibles en precio',text):state.update(sort='asc');state.pop('price',None)
    if re.search(r'\bcar[oa]s?\b|mayor precio|mas cost|mas costosos',text):state.update(sort='desc');state.pop('price',None)
    if 'cualquier precio' in text or 'sin presupuesto' in text:
        for k in ['price','min_price','max_price','sort']:state.pop(k,None)
    amount=r'(?:s/\s*)?(\d+(?:[.,]\d{1,2})?)'
    maximum=re.search(r'(?:hasta|maximo(?: de)?|menos de|no mas de|presupuesto(?: de)?)\s*'+amount,text)
    minimum=re.search(r'(?:desde|minimo(?: de)?|mas de)\s*'+amount,text)
    if maximum:state['max_price']=float(maximum[1].replace(',','.'));state.pop('price',None)
    if minimum:state['min_price']=float(minimum[1].replace(',','.'));state.pop('price',None)
    if state.get('max_price',float('inf'))<state.get('min_price',0):
        state.pop('min_price',None);return response('El mínimo supera el presupuesto máximo. Dime un rango válido, por ejemplo «desde 15 hasta 40 soles».')
    # Nombres de artistas o eventos: solo se aceptan fragmentos presentes en el catálogo.
    if any(w in text for w in ['yuyachkani','noche mali','tania libertad','amanda portales','cecilia bracamonte','camino de nora','sesiones gtn']):
        state['q']=next(w for w in ['yuyachkani','noche mali','tania libertad','amanda portales','cecilia bracamonte','camino de nora','sesiones gtn'] if w in text)
    if 'otros eventos' in text:state.pop('q',None)
    if predicted=='location' and confidence>.3:
        selected=[f for f in items if not state.get('venue') or f['venue']==state['venue']]
        if not state.get('venue'):
            return response('¿A qué recinto quieres ir: MALI o Gran Teatro Nacional? Puedo mostrar su dirección registrada y la página oficial. La continuidad de una ruta accesible debe confirmarse con el recinto.')
        if selected:
            venue=selected[0]
            return response(f"{venue['venue']} · {venue['district']}. Dirección registrada: {venue.get('address') or 'Consulta la fuente oficial'}. Revisa la ubicación y el acceso en el enlace oficial; no tengo información de tráfico ni de ascensores en tiempo real.",selected[:1],1)
    if predicted=='unrelated' and confidence>.4:
        return response('Puedo ayudarte con eventos culturales de Lima y sus condiciones de accesibilidad. Prueba «eventos en noviembre», «los más baratos» o «con LSP».')
    if not state and not re.search(r'evento|activid|plan|entrad|cartelera|que hay|muestra|busca|todo',text):
        return response('Dime un mes, un día, un presupuesto o un apoyo para buscar. Por ejemplo: «noviembre», «el 18 de octubre», «hasta 40 soles» o «con audiodescripción».')

    matched=[]
    for f in items:
        d=date.fromisoformat(f['date'])
        if state.get('year') and d.year!=state['year']:continue
        if state.get('month') and d.month!=state['month']:continue
        if state.get('day') and d.day!=state['day']:continue
        if state.get('date_from') and not state['date_from']<=f['date']<=state['date_to']:continue
        if state.get('district') and norm(f['district'])!=norm(state['district']):continue
        if state.get('category') and norm(f['category'])!=norm(state['category']):continue
        if state.get('venue') and f['venue']!=state['venue']:continue
        if state.get('q') and state['q'] not in norm(f['title']):continue
        if any(not any(c['code']==code and c['state']=='DISPONIBLE' for c in f['conditions']) for code in state.get('needs',[])):continue
        matched.append(f)
    missing=sum(f['official_price'] is None for f in matched)
    if any(k in state for k in ['min_price','max_price','sort','price']):
        matched=[f for f in matched if f['official_price'] is not None]
    if state.get('price')=='free':matched=[f for f in matched if f['official_price']==0]
    if 'min_price' in state:matched=[f for f in matched if f['official_price']>=state['min_price']]
    if 'max_price' in state:matched=[f for f in matched if f['official_price']<=state['max_price']]
    if state.get('sort'):
        matched.sort(key=lambda f:(float(f['official_price'])*(-1 if state['sort']=='desc' else 1),f['date'],f['id']))
    else:matched.sort(key=lambda f:(f['date'],f.get('time') or '',f['id']))
    labels=[]
    if state.get('month'):labels.append(f"{state.get('day','')} {MONTHS[state['month']-1]} de {state.get('year',today.year)}".strip())
    if state.get('date_from'):labels.append(state['date_from']+(' a '+state['date_to'] if state['date_from']!=state['date_to'] else ''))
    labels += [str(state[k]) for k in ['category','district','venue'] if state.get(k)]
    if 'max_price' in state:labels.append(f"hasta S/ {state['max_price']:.2f}")
    if 'min_price' in state:labels.append(f"desde S/ {state['min_price']:.2f}")
    if state.get('needs'):labels.append('apoyos indispensables: '+', '.join(state['needs']))
    label=' · '.join(labels) or 'toda la cartelera'
    if not matched:
        answer=f'No encontré funciones para {label} en la cartelera guardada. Puedes cambiar la fecha, ampliar el presupuesto o iniciar otra búsqueda. Esto no demuestra que no existan eventos fuera de este catálogo.'
        if state.get('needs'):answer+=' No confirmé un apoyo solo por estar disponible en el recinto; LSP, subtítulos, audiodescripción y apoyo táctil requieren evidencia para la función.'
    else:
        answer=f'Encontré {len(matched)} '+('función' if len(matched)==1 else 'funciones')+f' para {label}. Te muestro '+str(min(3,len(matched)))+'.'
        if state.get('sort'):answer+=' Ordené las tarifas mínimas publicadas de '+('mayor a menor' if state['sort']=='desc' else 'menor a mayor')+' precio.'
        answer+=' Abre la ficha para revisar los apoyos, su alcance y la fuente oficial.'
    if missing and any(k in state for k in ['min_price','max_price','sort','price']):answer+=f' Excluí {missing} funciones sin precio publicado; precio desconocido no significa gratuito.'
    if 'max_price' in state or state.get('sort'):answer+=' «Desde» indica una tarifa de partida y no garantiza el precio de todas las localidades.'
    return response(answer,matched[:3],len(matched))
