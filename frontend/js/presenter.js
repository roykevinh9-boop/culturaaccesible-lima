import {$,element} from './view.js';

/** Presentador MVP: coordina acciones, modelo y vista; ignora respuestas obsoletas. */
export class CatalogPresenter {
  constructor(model,view){this.model=model;this.view=view;this.requestNumber=0;this.detailNumber=0;this.origin=null;this.metadata=null;}
  async start(){
    this.view.onOpen=(id,button)=>{this.origin=button;location.hash=`funcion=${id}`;};
    $('search-form').addEventListener('submit',event=>{event.preventDefault();clearTimeout(this.timer);this.search();});
    $('search-form').addEventListener('change',event=>{clearTimeout(this.timer);if(event.target.name==='source')this.loadSource();else this.search();});
    $('search').addEventListener('input',()=>{clearTimeout(this.timer);this.timer=setTimeout(()=>this.search(),300);});
    const clear=()=>{clearTimeout(this.timer);const source=this.view.filters().source;$('search-form').reset();document.querySelector(`[name=source][value=${source}]`).checked=true;this.search();$('search').focus();};
    $('clear-filters').addEventListener('click',clear);$('empty-clear').addEventListener('click',clear);
    $('close-detail').addEventListener('click',()=>$('detail-dialog').close());
    $('detail-dialog').addEventListener('close',()=>{this.detailNumber++;if(location.hash.startsWith('#funcion='))history.replaceState(null,'',location.pathname+location.search+'#catalogo');if(this.origin?.isConnected)this.origin.focus();});
    for(const [open,dialog,close] of [['how-button','help-dialog','close-help'],['assistant-button','assistant-dialog','close-assistant'],['access-button','access-dialog','close-access']]){$(open).addEventListener('click',()=>$(dialog).showModal());$(close).addEventListener('click',()=>$(dialog).close());}
    document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',()=>{$('assistant-input').value=button.dataset.prompt;$('assistant-input').focus();}));
    $('assistant-form').addEventListener('submit',event=>{event.preventDefault();this.assist();});
    this.accessibility();
    window.addEventListener('hashchange',()=>this.route());
    try{this.metadata=await this.model.metadata();this.view.metadata(this.metadata);await this.search();await this.route();}
    catch(error){this.view.loading(false);this.view.error(error.message);}
  }
  async loadSource(){const source=this.view.filters().source;this.sourceNumber=(this.sourceNumber||0)+1;const number=this.sourceNumber;this.abort?.abort();this.requestNumber++;this.view.loading(true);try{const meta=await this.model.metadata(source);if(number!==this.sourceNumber)return;this.metadata=meta;this.view.metadata(meta);this.view.setFilters({});await this.search();}catch(error){if(number===this.sourceNumber){this.view.loading(false);this.view.error(error.message);}}}
  accessibility(){const ids=['text-size','high-contrast','underline-links','reduce-motion'];let saved={};try{saved=JSON.parse(localStorage.getItem('cal-access')||'{}');}catch{}for(const id of ids){const input=$(id);if(input.type==='checkbox')input.checked=saved[id]===true;else input.value=['100','112.5','125'].includes(saved[id])?saved[id]:'100';}const apply=()=>{document.documentElement.style.fontSize=$('text-size').value+'%';for(const id of ids.slice(1))document.documentElement.classList.toggle(id,$(id).checked);const value=Object.fromEntries(ids.map(id=>[id,$(id).type==='checkbox'?$(id).checked:$(id).value]));try{localStorage.setItem('cal-access',JSON.stringify(value));}catch{}};ids.forEach(id=>$(id).addEventListener('change',apply));$('reset-access').addEventListener('click',()=>{$('text-size').value='100';ids.slice(1).forEach(id=>$(id).checked=false);apply();});apply();}
  async search(){
    const number=++this.requestNumber;
    this.abort?.abort();this.abort=new AbortController();this.view.loading(true);
    try{const result=await this.model.search(this.view.filters(),this.abort.signal);if(number===this.requestNumber)this.view.results(result);}
    catch(error){if(number===this.requestNumber && error.name!=='AbortError')this.view.error(error.message);}
    finally{if(number===this.requestNumber)this.view.loading(false);}
  }
  async route(){
    const match=location.hash.match(/^#funcion=(\d+)$/);
    if(!match){if($('detail-dialog').open)$('detail-dialog').close();return;}
    const number=++this.detailNumber;
    try{const item=await this.model.detail(match[1]);if(number!==this.detailNumber)return;this.view.detail(item,{estimate:value=>this.model.estimate(value),report:value=>this.model.report(value),share:(id,box)=>this.share(id,box)});if(!$('detail-dialog').open)$('detail-dialog').showModal();}
    catch(error){this.view.toast(error.message);history.replaceState(null,'',location.pathname+location.search+'#catalogo');}
  }
  async share(id,box){
    const url=new URL(location.pathname,location.origin);url.hash=`funcion=${id}`;
    try{await navigator.clipboard.writeText(url.href);this.view.toast('Enlace de la función copiado. Funciona mientras esta aplicación esté disponible.');}
    catch{const label=element('label','','Copia este enlace');const input=element('input','share-field');input.value=url.href;input.readOnly=true;input.setAttribute('aria-label','Enlace de la función para copiar');label.append(input);box.replaceChildren(label);input.focus();input.select();}
  }
  assist(){
    const normalize=text=>text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const input=normalize($('assistant-input').value);
    const filter={q:'',district:'',category:'',date:'all',price:'all',needs:[]};const applied=[];
    if(!this.metadata){$('assistant-message').textContent='El catálogo todavía no está disponible.';return;}
    for(const value of this.metadata.districts)if(input.includes(normalize(value))){filter.district=value;applied.push(value);break;}
    for(const value of this.metadata.categories)if(input.includes(normalize(value))){filter.category=value;applied.push(value);break;}
    const rules={lsp:['lsp','senas'],subtitulos:['subtitulo'],audiodescripcion:['audiodescripcion'],tactil:['tactil'],silla_ruedas:['silla de ruedas'],sin_escalones:['sin escalones'],bano_adaptado:['bano adaptado']};
    for(const [code,words] of Object.entries(rules))if(words.some(word=>input.includes(word))){filter.needs.push(code);applied.push(this.metadata.supports.find(s=>s.code===code)?.label||code);}
    if(/gratis|gratuito|gratuita/.test(input)){filter.price='free';applied.push('Ingreso gratuito');}
    if(input.includes('hoy')){filter.date='today';applied.push('Hoy');}else if(input.includes('fin de semana')){filter.date='weekend';applied.push('Este fin de semana');}
    if(!applied.length){$('assistant-message').textContent='No reconocí filtros concretos. Prueba «Teatro en Miraflores con LSP» o utiliza el buscador por nombre.';return;}
    this.view.setFilters(filter);this.search();$('assistant-dialog').close();$('catalogo').scrollIntoView({behavior:'auto'});this.view.toast(`Filtros sugeridos: ${applied.join(', ')}. Puedes modificarlos.`);
  }
}
