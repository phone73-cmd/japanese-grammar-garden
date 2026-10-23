/* Japanese Grammar Garden v0.2.5-dev shared dialogs */
(()=>{
 const queue=[];let active=false;
 function show(){if(active||!queue.length)return;active=true;const {message,confirm,resolve}=queue.shift(),before=document.activeElement;
 const shade=document.createElement('div');shade.id='jgg-dialog';shade.className='app-modal-shade';shade.style.zIndex='200';
 shade.innerHTML='<div class="app-modal" role="dialog" aria-modal="true" aria-labelledby="jgg-dialog-title"><h3 id="jgg-dialog-title">'+(confirm?'확인':'안내')+'</h3><p></p><div class="app-modal-actions"></div></div>';
 shade.querySelector('p').textContent=message;const actions=shade.querySelector('.app-modal-actions');
 function finish(value){shade.remove();active=false;document.removeEventListener('keydown',key);before?.isConnected&&before.focus();resolve(value);show()}
 if(confirm){const cancel=document.createElement('button');cancel.className='secondary';cancel.textContent='취소';cancel.onclick=()=>finish(false);actions.append(cancel)}
 const ok=document.createElement('button');ok.className='primary';ok.textContent='확인';ok.onclick=()=>finish(true);actions.append(ok);
 function key(e){if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();finish(false)}if(e.key==='Tab'){const buttons=[...actions.querySelectorAll('button')];if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1).focus()}else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0].focus()}}}
 document.addEventListener('keydown',key);document.body.append(shade);actions.querySelector('button').focus();
 }
 window.jggUI={confirm:message=>new Promise(resolve=>{queue.push({message,confirm:true,resolve});show()}),notice:message=>new Promise(resolve=>{queue.push({message,confirm:false,resolve});show()})};
})();
