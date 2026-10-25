(()=>{'use strict';const p=document.querySelector('#reading-progress');function progress(){const h=document.documentElement;const denom=h.scrollHeight-h.clientHeight;p.style.width=(denom>0?(h.scrollTop/denom*100):0)+'%'}addEventListener('scroll',progress,{passive:true});progress();document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const t=b.getAttribute('data-copy')||'';try{await navigator.clipboard.writeText(t);b.textContent='Скопировано';}catch{const x=document.createElement('textarea');x.value=t;document.body.append(x);x.select();document.execCommand('copy');x.remove();b.textContent='Скопировано';}setTimeout(()=>b.textContent='Скопировать команду',1800)}));document.querySelectorAll('[data-answer]').forEach(b=>b.addEventListener('click',()=>{const e=document.getElementById(b.dataset.answer);if(e){e.hidden=!e.hidden;b.setAttribute('aria-expanded',String(!e.hidden));b.textContent=e.hidden?'Показать образец рассуждения':'Скрыть ответ'}}));})();
;(() => {
  const current = document.currentScript;
  if (!current || !/\/lessons\/\d{2}\.html$/.test(window.location.pathname)) return;
  if (document.querySelector('script[data-academy-visual-loader]')) return;
  const visual = document.createElement('script');
  visual.dataset.academyVisualLoader = 'true';
  visual.src = new URL('lesson-visuals.js', current.src).href;
  visual.onerror = () => console.error('[DEVOPS ACADEMY] Не удалось загрузить визуальный модуль:', visual.src);
  visual.onload = () => {
    if (!document.getElementById('visual-guide')) {
      console.error('[DEVOPS ACADEMY] Визуальный модуль загружен, но схемы не созданы');
    }
  };
  document.head.append(visual);
})();
