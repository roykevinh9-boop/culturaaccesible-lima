import {$,element} from '../views/catalog-view.js';
import {ChatController} from './chat-controller.js';
import {SupportBarView} from '../views/support-bar-view.js';
import {SupportPreferences} from '../models/support-preferences.js';
import {bindDialogKeyboard} from './dialog-controller.js';

/** Coordina búsqueda, contexto, recuperación de errores y navegación por teclado. */
export class CatalogController {
  constructor(model,view){this.model=model;this.view=view;this.requestNumber=0;this.detailNumber=0;this.origin=null;this.metadata=null;}
  async start(){
    document.querySelectorAll('dialog').forEach(bindDialogKeyboard);
    let storage;try{storage=window.sessionStorage;}catch{}
    this.supportPreferences=new SupportPreferences(storage);this.supportBar=new SupportBarView();
    this.view.onOpen=(id,button)=>{this.origin=button;location.hash=`funcion=${id}`;};
    $('search-form').addEventListener('submit',event=>{event.preventDefault();clearTimeout(this.timer);this.search();});
    $('search-form').addEventListener('change',event=>{
      clearTimeout(this.timer);
      if(event.target.name==='source'){this.undoFilters=null;this.view.undoAvailable(false);this.loadSource();}else this.search();
    });
    $('search').addEventListener('input',()=>{clearTimeout(this.timer);this.timer=setTimeout(()=>this.search(),300);});
    for(const id of ['clear-filters','empty-clear'])$(id).addEventListener('click',()=>this.clear());
    $('undo-filters').addEventListener('click',()=>{
      if(!this.undoFilters)return;
      this.view.setFilters(this.undoFilters);this.undoFilters=null;this.view.undoAvailable(false);this.search();$('search').focus();
    });
    $('retry-catalog').addEventListener('click',()=>this.metadata?this.search():this.loadSource());
    $('close-detail').addEventListener('click',()=>$('detail-dialog').close());
    $('detail-dialog').addEventListener('close',()=>{
      this.detailNumber++;this.detailAbort?.abort();
      if(location.hash.startsWith('#funcion='))history.replaceState(null,'',location.pathname+location.search+'#catalogo');
      if(this.origin?.isConnected)this.origin.focus();else $('search').focus();
    });
    for(const [open,dialog,close] of [['how-button','help-dialog','close-help'],['access-button','access-dialog','close-access']]){
      $(open).addEventListener('click',()=>$(dialog).showModal());$(close).addEventListener('click',()=>$(dialog).close());
    }
    this.chat=new ChatController(this.model,this.view);this.chat.start();this.accessibility();
    window.addEventListener('hashchange',()=>this.route());await this.loadSource();await this.route();
  }
  clear(){
    clearTimeout(this.timer);const previous=this.view.filters();
    if(previous.q||previous.district||previous.category||previous.needs.length||previous.date!=='all'||previous.price!=='all'){
      this.undoFilters=structuredClone(previous);this.view.undoAvailable(true);
    }
    this.view.setFilters({source:previous.source});this.search();$('search').focus();
  }
  setupSupportBar(filters){
    const codes=this.metadata.supports.map(s=>s.code);
    this.view.setFilters({...filters,needs:this.supportPreferences.load(codes)});
    this.supportBar.render(this.metadata.supports,code=>{
      for(const input of $('support-filters').querySelectorAll('input')){if(!code)input.checked=false;else if(input.value===code)input.checked=!input.checked;}
      clearTimeout(this.timer);this.search();
    });
    this.supportBar.selected(this.view.filters().needs);
  }
  async loadSource(){
    const filters=this.view.filters();const number=this.sourceNumber=(this.sourceNumber||0)+1;
    this.metadata=null;this.abort?.abort();this.metadataAbort?.abort();this.metadataAbort=new AbortController();
    this.requestNumber++;this.view.loading(true);
    try{
      const meta=await this.model.metadata(filters.source,this.metadataAbort.signal);
      if(number!==this.sourceNumber)return;
      this.metadata=meta;this.view.metadata(meta);this.setupSupportBar(filters);await this.search();
    }catch(error){if(number===this.sourceNumber&&error.name!=='AbortError'){this.view.loading(false);this.view.error(error.message);}}
  }
  accessibility(){
    const ids=['text-size','high-contrast','underline-links','reduce-motion'];let saved={};
    try{saved=JSON.parse(localStorage.getItem('cal-access')||'{}');}catch{}
    for(const id of ids){const input=$(id);if(input.type==='checkbox')input.checked=saved[id]===true;else input.value=['100','112.5','125'].includes(saved[id])?saved[id]:'100';}
    const apply=()=>{
      document.documentElement.style.fontSize=$('text-size').value+'%';
      for(const id of ids.slice(1))document.documentElement.classList.toggle(id,$(id).checked);
      try{localStorage.setItem('cal-access',JSON.stringify(Object.fromEntries(ids.map(id=>[id,$(id).type==='checkbox'?$(id).checked:$(id).value]))));}catch{}
    };
    ids.forEach(id=>$(id).addEventListener('change',apply));
    $('reset-access').addEventListener('click',()=>{$('text-size').value='100';ids.slice(1).forEach(id=>$(id).checked=false);apply();});apply();
  }
  async search(){
    if(!this.metadata)return this.loadSource();
    const filters=this.view.filters();this.supportPreferences.save(filters.needs);this.supportBar.selected(filters.needs);
    this.view.activeFilters(filters,(key,value)=>{
      const next=this.view.filters();
      if(key==='needs')next.needs=next.needs.filter(code=>code!==value);else next[key]=['date','price'].includes(key)?'all':'';
      this.view.setFilters(next);this.search();
    });
    const number=++this.requestNumber;this.abort?.abort();this.abort=new AbortController();this.view.loading(true);
    try{const result=await this.model.search(filters,this.abort.signal);if(number===this.requestNumber)this.view.results(result);}
    catch(error){if(number===this.requestNumber&&error.name!=='AbortError')this.view.error(error.message);}
    finally{if(number===this.requestNumber)this.view.loading(false);}
  }
  async route(){
    const number=++this.detailNumber;this.detailAbort?.abort();
    const match=location.hash.match(/^#funcion=(\d+)$/);
    if(!match){if($('detail-dialog').open)$('detail-dialog').close();return;}
    this.detailAbort=new AbortController();this.view.toast('Abriendo la ficha…');
    try{
      const item=await this.model.detail(match[1],this.detailAbort.signal);if(number!==this.detailNumber)return;
      this.view.detail(item,{estimate:value=>this.model.estimate(value),report:value=>this.model.report(value),share:(id,box)=>this.share(id,box)});
      if(!$('detail-dialog').open)$('detail-dialog').showModal();$('detail-title').focus();$('toast').hidden=true;
    }catch(error){
      if(number!==this.detailNumber||error.name==='AbortError')return;
      this.view.toast(error.message+' Vuelve a abrir la ficha para reintentar.');history.replaceState(null,'',location.pathname+location.search+'#catalogo');
    }
  }
  async share(id,box){
    const url=new URL(location.pathname,location.origin);url.hash=`funcion=${id}`;
    try{await navigator.clipboard.writeText(url.href);this.view.toast('Enlace de la función copiado. Funciona mientras esta aplicación esté disponible.');}
    catch{const label=element('label','','Copia este enlace');const input=element('input','share-field');input.value=url.href;input.readOnly=true;input.setAttribute('aria-label','Enlace de la función para copiar');label.append(input);box.replaceChildren(label);input.focus();input.select();}
  }
}
