import {$,element} from './view.js';

/** Presentador de conversación. Guarda filtros durante la sesión; nunca contraseñas ni historial persistente. */
export class ChatPresenter {
  constructor(model,view){this.model=model;this.view=view;this.context={};this.turn=0;}
  start(){
    for(const id of ['assistant-button','chat-launcher'])$(id).addEventListener('click',()=>{$('assistant-dialog').showModal();$('chat-input').focus();});
    $('close-assistant').addEventListener('click',()=>$('assistant-dialog').close());
    $('chat-reset').addEventListener('click',()=>this.reset());
    $('chat-source').addEventListener('change',()=>this.reset());
    $('chat-form').addEventListener('submit',event=>{event.preventDefault();this.send();});
    $('chat-input').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();if(!$('chat-send').disabled)$('chat-form').requestSubmit();}});
    document.querySelectorAll('[data-chat-prompt]').forEach(button=>button.addEventListener('click',()=>{if($('chat-send').disabled)return;$('chat-input').value=button.dataset.chatPrompt;$('chat-form').requestSubmit();}));
    this.reset(false);
  }
  reset(focus=true){
    this.abort?.abort();this.turn++;this.context={};$('chat-log').replaceChildren();$('chat-send').disabled=false;$('chat-log').setAttribute('aria-busy','false');$('chat-status').textContent='';$('chat-input').value='';
    this.bubble('AccesI','¡Hola! Soy AccesI 👋 Puedes buscar por mes, día, presupuesto y accesibilidad. Prueba «eventos en noviembre» y después «y los más baratos». También respondo a un simple «hola».');
    if($('chat-source').value==='demo')this.bubble('AccesI','Estás en ejemplos ficticios del curso. Sus precios, recintos y apoyos no representan eventos reales.');
    if(focus)$('chat-input').focus();
  }
  bubble(speaker,text,cls=''){
    const box=element('article',`chat-message ${cls}`);box.append(element('strong','chat-speaker',speaker),element('p','',text));$('chat-log').append(box);return box;
  }
  async send(){
    const message=$('chat-input').value.trim();if(!message||$('chat-send').disabled)return;
    const turn=++this.turn;this.abort=new AbortController();
    this.bubble('Tú',message,'user');$('chat-input').value='';$('chat-send').disabled=true;$('chat-status').textContent='AccesI está consultando la cartelera…';$('chat-log').setAttribute('aria-busy','true');this.bottom();
    try{
      const result=await this.model.chat({message,context:this.context,source:$('chat-source').value},this.abort.signal);if(turn!==this.turn)return;
      this.context=result.context||{};const box=this.bubble('AccesI',result.reply);
      for(const item of result.items||[])box.append(this.result(item));
      if(result.items?.length)box.append(element('p','chat-source-note',result.source==='demo'?'Datos ficticios para el curso.':result.catalog_note));
      $('chat-status').textContent='Respuesta lista.';
    }catch(error){if(turn===this.turn&&error.name!=='AbortError'){this.bubble('AccesI',error.message,'error');$('chat-input').value=message;$('chat-status').textContent='No se completó la consulta. Puedes volver a enviarla.';}}
    finally{if(turn===this.turn){$('chat-send').disabled=false;$('chat-log').setAttribute('aria-busy','false');this.bottom();$('chat-input').focus();}}
  }
  result(item){
    const row=element('article','chat-result');
    if(item.image_url){try{const url=new URL(item.image_url);if(url.protocol==='https:'){const img=element('img');img.src=url.href;img.alt=item.image_alt||`Afiche de ${item.title}`;img.loading='lazy';img.addEventListener('error',()=>img.hidden=true,{once:true});row.append(img);}}catch{}}
    else{const mark=element('span','','✦');mark.setAttribute('aria-hidden','true');row.append(mark);}
    const body=element('div');body.append(element('h3','',item.title),element('p','',`${item.date} · ${item.time?item.time.slice(0,5):'Horario por confirmar'} · ${item.district}`),element('p','chat-price',this.view.price(item)));
    const actions=element('div','chat-result-actions');const detail=element('button','','Ver ficha y apoyos');detail.type='button';detail.setAttribute('aria-label',`Ver ficha de ${item.title}, ${item.date}`);detail.addEventListener('click',()=>{$('assistant-dialog').close();this.view.onOpen(item.id,$('assistant-button'));});actions.append(detail);
    const official=this.view.link(item.official_url,'Fuente oficial');if(official&&!item.demo)actions.append(official);body.append(actions);row.append(body);return row;
  }
  bottom(){$('chat-log').scrollTop=$('chat-log').scrollHeight;}
}
