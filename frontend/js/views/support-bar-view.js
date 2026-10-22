import {$,element} from './catalog-view.js';

/** Barra de navegación de apoyos; el controlador decide cómo aplicar el filtro. */
export class SupportBarView {
  render(supports,onChange){
    const create=(code,label)=>{const button=element('button','support-shortcut',label);button.type='button';button.dataset.support=code;button.setAttribute('aria-pressed','false');button.addEventListener('click',()=>onChange(code));return button;};
    $('support-shortcuts').replaceChildren(create('','Todos los apoyos'),...supports.map(s=>create(s.code,s.label)));
  }
  selected(codes){
    for(const button of $('support-shortcuts').querySelectorAll('button'))button.setAttribute('aria-pressed',String(button.dataset.support?codes.includes(button.dataset.support):codes.length===0));
    $('support-selection').textContent=codes.length?`${codes.length} ${codes.length===1?'apoyo elegido':'apoyos elegidos'}`:'Sin filtro de apoyos';
  }
}
