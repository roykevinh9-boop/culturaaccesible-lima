import test from 'node:test';
import assert from 'node:assert/strict';
import {CatalogModel,ApiError} from '../frontend/models/catalog-model.js';

const response=(data,status=200)=>({ok:status<400,status,json:async()=>data});
const pending=(_url,{signal})=>new Promise((resolve,reject)=>{
  const abort=()=>reject(new DOMException('Aborted','AbortError'));
  if(signal.aborted)abort();else signal.addEventListener('abort',abort,{once:true});
});
test('el transporte por defecto conserva el contexto global del navegador',async()=>{
  const original=globalThis.fetch;
  try {
    globalThis.fetch=async function(){assert.equal(this,globalThis);return response({ok:true});};
    assert.deepEqual(await new CatalogModel().metadata(),{ok:true});
  }finally{globalThis.fetch=original;}
});
test('conserva filtros múltiples y codifica búsquedas como datos',async()=>{
  let called;
  const model=new CatalogModel({fetchImpl:async url=>{called=url;return response({total:0});}});
  await model.search({source:'official',q:'arte & música',needs:['lsp','subtitulos']});
  const params=new URL(called,'http://localhost').searchParams;
  assert.equal(params.get('q'),'arte & música');assert.deepEqual(params.getAll('needs'),['lsp','subtitulos']);
});
test('entrega errores de campo del servidor para mostrarlos junto al control',async()=>{
  const model=new CatalogModel({fetchImpl:async()=>response({message:'Revisa los campos.',fields:{comment:'Escribe al menos 10 caracteres.'}},400)});
  await assert.rejects(model.report({}),error=>error instanceof ApiError&&error.status===400&&error.fields.comment.includes('10'));
});
test('una lectura que no responde termina con un mensaje de reintento',async()=>{
  const model=new CatalogModel({timeoutMs:15,fetchImpl:pending});
  await assert.rejects(model.metadata(),error=>error.status===408&&error.message.includes('volver a intentarlo'));
});
test('cancelar una búsqueda obsoleta mantiene AbortError',async()=>{
  const controller=new AbortController();const model=new CatalogModel({fetchImpl:pending});
  const result=model.search({},controller.signal);controller.abort();
  await assert.rejects(result,{name:'AbortError'});
});
test('un fallo de conexión ofrece una instrucción en español',async()=>{
  const model=new CatalogModel({fetchImpl:async()=>{throw new TypeError('Failed to fetch');}});
  await assert.rejects(model.metadata(),error=>error.message.includes('Revisa tu conexión')&&!error.message.includes('Failed to fetch'));
});
test('una escritura interrumpida no se reenvía ni se confirma automáticamente',async()=>{
  let calls=0;const model=new CatalogModel({timeoutMs:15,fetchImpl:(...args)=>{calls++;return pending(...args);}});
  await assert.rejects(model.report({comment:'Comentario de prueba'}),error=>error.message.includes('Revisa el estado antes de reenviar'));
  assert.equal(calls,1);
});
test('una respuesta no JSON no se presenta como resultado válido',async()=>{
  const model=new CatalogModel({fetchImpl:async()=>({ok:true,json:async()=>{throw new SyntaxError('bad');}})});
  await assert.rejects(model.metadata(),error=>error.message.includes('respuesta válida'));
});
test('una respuesta de guardado ilegible no invita a duplicar el reporte',async()=>{
  const model=new CatalogModel({fetchImpl:async()=>({ok:true,json:async()=>{throw new SyntaxError('bad');}})});
  await assert.rejects(model.report({}),error=>error.message.includes('Revisa el estado antes de reenviar'));
});
test('la espera limitada también cubre la lectura del cuerpo de la respuesta',async()=>{
  const model=new CatalogModel({timeoutMs:15,fetchImpl:async(url,options)=>({ok:true,json:()=>pending(url,options)})});
  await assert.rejects(model.metadata(),error=>error.status===408);
});
