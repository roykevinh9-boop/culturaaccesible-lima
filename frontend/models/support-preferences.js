/** Preferencias funcionales de esta pestaña; sin cuenta ni almacenamiento remoto. */
export class SupportPreferences {
  constructor(storage){this.storage=storage;this.key='cal-supports';}
  load(validCodes){
    try {const value=JSON.parse(this.storage?.getItem(this.key)||'[]');return Array.isArray(value)?[...new Set(value.filter(code=>validCodes.includes(code)))]:[];}
    catch {return [];}
  }
  save(codes){try{this.storage?.setItem(this.key,JSON.stringify(codes));}catch{/* El filtro funciona aunque el navegador bloquee el almacenamiento. */}}
}
