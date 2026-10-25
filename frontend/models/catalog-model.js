export class ApiError extends Error {
  constructor(message,status=0,fields={}) {super(message);this.name='ApiError';this.status=status;this.fields=fields;}
}

/** Acceso a la API con espera limitada; nunca reenvía escrituras automáticamente. */
export class CatalogModel {
  constructor({timeoutMs=12000,fetchImpl=(...args)=>globalThis.fetch(...args)}={}) {this.timeoutMs=timeoutMs;this.fetchImpl=fetchImpl;}
  async request(path,options={}) {
    const controller=new AbortController();const upstream=options.signal;
    const relay=()=>controller.abort();
    if(upstream?.aborted)controller.abort();else upstream?.addEventListener('abort',relay,{once:true});
    let timedOut=false;
    const timer=setTimeout(()=>{timedOut=true;controller.abort();},this.timeoutMs);
    const writing=path==='/reports'&&options.method==='POST';
    try {
      const response=await this.fetchImpl(`/api${path}`,{...options,signal:controller.signal,headers:{'Content-Type':'application/json',...options.headers}});
      let data;
      try {data=await response.json();}
      catch(error) {if(controller.signal.aborted)throw error;throw new ApiError(writing?'No pudimos confirmar el guardado. Revisa el estado antes de reenviar.':'El servidor no devolvió una respuesta válida. Vuelve a intentarlo.');}
      if(!response.ok)throw new ApiError(data.message||'No pudimos completar la operación.',response.status,data.fields||{});
      return data;
    } catch(error) {
      if(timedOut)throw new ApiError(writing?'No pudimos confirmar el resultado a tiempo. Revisa el estado antes de reenviar.':'La consulta tardó demasiado. Puedes volver a intentarlo.',408);
      if(upstream?.aborted)throw new DOMException('Consulta cancelada.','AbortError');
      if(error instanceof ApiError)throw error;
      throw new ApiError(writing?'Se interrumpió la conexión y no pudimos confirmar el resultado. Revisa antes de reenviar.':'No pudimos conectar con el catálogo. Revisa tu conexión y vuelve a intentarlo.');
    } finally {clearTimeout(timer);upstream?.removeEventListener('abort',relay);}
  }
  metadata(source='official',signal){return this.request(`/metadata?source=${encodeURIComponent(source)}`,{signal});}
  search(filters,signal){
    const params=new URLSearchParams();
    for(const [key,value] of Object.entries(filters)) {
      if(Array.isArray(value))value.forEach(v=>params.append(key,v));else if(value)params.set(key,value);
    }
    return this.request(`/functions?${params}`,{signal});
  }
  detail(id,signal){return this.request(`/functions/${encodeURIComponent(id)}`,{signal});}
  estimate(input){return this.request('/estimates',{method:'POST',body:JSON.stringify(input)});}
  report(input){return this.request('/reports',{method:'POST',body:JSON.stringify(input)});}
  chat(input,signal){return this.request('/chat',{method:'POST',body:JSON.stringify(input),signal});}
}
