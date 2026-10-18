/** Modelo MVP: acceso a datos; no modifica el DOM. */
export class CatalogModel {
  async request(path, options={}) {
    const response=await fetch(`/api${path}`,{...options,headers:{'Content-Type':'application/json',...options.headers}});
    let data;
    try { data=await response.json(); } catch { throw new Error('El servidor no devolvió una respuesta válida.'); }
    if(!response.ok) throw new Error(data.message || 'No pudimos completar la operación.');
    return data;
  }
  metadata(){ return this.request('/metadata'); }
  search(filters,signal){
    const params=new URLSearchParams();
    for(const [key,value] of Object.entries(filters)) {
      if(Array.isArray(value)) value.forEach(v=>params.append(key,v));
      else if(value) params.set(key,value);
    }
    return this.request(`/functions?${params}`,{signal});
  }
  detail(id){ return this.request(`/functions/${encodeURIComponent(id)}`); }
  estimate(input){ return this.request('/estimates',{method:'POST',body:JSON.stringify(input)}); }
  report(input){ return this.request('/reports',{method:'POST',body:JSON.stringify(input)}); }
}
