import test from 'node:test';
import assert from 'node:assert/strict';
import {SupportPreferences} from '../frontend/models/support-preferences.js';

const codes=['lsp','subtitulos','silla_ruedas'];
const storage=()=>{const values=new Map();return {getItem:key=>values.get(key),setItem:(key,value)=>values.set(key,value)};};
test('recupera apoyos al crear otra instancia tras una recarga',()=>{const s=storage();new SupportPreferences(s).save(['lsp','subtitulos']);assert.deepEqual(new SupportPreferences(s).load(codes),['lsp','subtitulos']);});
test('limpiar no recupera preferencias anteriores',()=>{const s=storage();const prefs=new SupportPreferences(s);prefs.save(['lsp']);prefs.save([]);assert.deepEqual(prefs.load(codes),[]);});
test('descarta apoyos que no existen en el catálogo nuevo',()=>{const s=storage();const prefs=new SupportPreferences(s);prefs.save(['lsp','inexistente']);assert.deepEqual(prefs.load(['subtitulos']),[]);});
test('JSON corrupto permite continuar sin filtros',()=>{const s=storage();s.setItem('cal-supports','{');assert.deepEqual(new SupportPreferences(s).load(codes),[]);});
test('almacenamiento bloqueado no impide buscar',()=>{const s={getItem(){throw Error('bloqueado');},setItem(){throw Error('bloqueado');}};const prefs=new SupportPreferences(s);assert.doesNotThrow(()=>prefs.save(['lsp']));assert.deepEqual(prefs.load(codes),[]);});
test('elimina duplicados y entradas de tipos incorrectos',()=>{const s=storage();const prefs=new SupportPreferences(s);prefs.save(['lsp','lsp',{},null]);assert.deepEqual(prefs.load(codes),['lsp']);});
