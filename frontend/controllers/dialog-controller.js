/** Mantiene un recorrido de Tab predecible dentro de los diálogos abiertos. */
export function bindDialogKeyboard(dialog){
  dialog.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const controls=[...dialog.querySelectorAll('a[href],button,input,select,textarea,summary,[tabindex]')]
      .filter(node=>!node.disabled&&node.tabIndex>=0&&node.getClientRects().length>0&&getComputedStyle(node).visibility!=='hidden');
    if(!controls.length){event.preventDefault();dialog.focus();return;}
    const first=controls[0],last=controls.at(-1),active=document.activeElement;
    if(!controls.includes(active)){event.preventDefault();(event.shiftKey?last:first).focus();}
    else if(event.shiftKey&&active===first){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&active===last){event.preventDefault();first.focus();}
  });
}
