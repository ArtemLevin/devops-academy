(function academyVisuals(){
'use strict';
const PATHS={
1:"Браузер|DNS / сеть|HTTP endpoint|HTTP-ответ",
2:"Клиент|Сервис платформы|Внутренний API|Геометрический движок",
3:"Вход пользователя|Сессия / токен|Документ доски|Публикация материала",
4:"PowerShell|WSL2 VM|Ubuntu / Bash|Docker Desktop",
5:"systemd / родитель|PID / PPID|Процесс|CPU / RAM / swap",
6:"Имя|DNS|TCP / TLS|HTTP",
7:"Dockerfile|BuildKit / cache|Image + digest|Контейнер",
8:"Docker network|DNS имя сервиса|Контейнер|Volume / данные",
9:"compose.yaml|Сервисы|Health checks|Приложение",
10:"Переменные среды|Конфигурация|Процесс|Наблюдаемое поведение",
11:"PostgreSQL / Redis|Backend / worker|API|TutorBoard UI",
12:"Изолированный стенд|Неисправность A / B|Гипотезы|Проверки и исправления",
13:"Git push / PR|Workflow trigger|Runner / job|Step / artifact",
14:"Исходный код|Lint / unit|Build|Artifact / quality gate",
15:"Учебный PR|Преднамеренный fail|CI logs|Fix + green",
16:"Исходник .tex / .md|Валидация|Компиляция|PDF / HTML",
17:"HTML / Math|Headless browser|DOM / pixels|Assertion / screenshot",
18:"CI job|Report / screenshot|Artifact store|Staging preview",
19:"Migration file|Тестовая PostgreSQL|Schema version|SQL invariants",
20:"Producer|Redis broker|Celery worker|ACK / результат",
21:"Событие|Retry / повторная доставка|Idempotency key|Единственный side effect",
22:"Commit|Tested artifact|Approval|Digest → staging/prod",
23:"Учебный HTML / PDF|Build workflow|Static artifacts|GitHub Pages",
24:"Staging release|Smoke / метрики|Решение|Rollback / validation",
25:"Input event|JS main thread|Layout / paint|Frame / INP",
26:"Фикстура доски|Нагрузка / жесты|Performance trace|Повторяемый отчёт",
27:"Baseline runs|Candidate runs|Distribution / variance|Decision + evidence",
28:"Request / event|Instrumentation|Counter / histogram|SLI / alert",
29:"HTTP request ID|API log|Queue task ID|Worker log / trace",
30:"SLI query|Dashboard panel|Alert rule|Notification / runbook",
31:"Offline client|Local command queue|Reconnect|Server ACK / sync",
32:"Клиент A и B|Версия документа|Conflict resolution|Согласованное состояние",
33:"Учебное отключение|Локальные изменения|Reconnect / replay|Инварианты",
34:"Backup schedule|Recovery point|Restore procedure|RPO / RTO evidence",
35:"Синтетическая БД|pg_dump archive|Отдельный restore target|SQL checks",
36:"Synthetic incident|Detection|Containment|Recovery / postmortem",
37:"Asset / data|Trust boundary|Threat|Mitigation / test",
38:"Pull request|Secret / dependency scan|Finding|Triage + gate",
39:"Test principal|Role / tenant scope|Resource ACL|Allow / deny + audit",
40:"Администратор|SSH|VPS / процесс|Reverse proxy / HTTPS",
41:"HCL code|terraform validate|terraform plan|Review → apply",
42:"Inventory|Ansible playbook|Check mode|Apply + rerun",
43:"Deployment|ReplicaSet|Pod|Service selector",
44:"kind cluster|K8s manifest|Pods / Service|Probes / request",
45:"Нагрузочные требования|Compose vs Kubernetes|Операционные риски|Выбор и доказательства",
46:"Logs / artifacts|Evidence matrix|Coverage / gaps|Independent review",
47:"Test release|Monitoring window|Rollback|Restore + validation",
48:"Новый инцидент|Самостоятельные гипотезы|Проверки|Восстановление + защита"
};
const SPECIAL={
6:["Имя разрешено?","TCP/TLS соединение установлено?","HTTP-ответ соответствует контракту?"],
9:["Compose-конфигурация валидна?","Зависимость готова по healthcheck?","API действительно обслуживает запрос?"],
20:["Сообщение опубликовано в правильную очередь?","Worker получил задачу?","Побочный эффект подтверждён отдельно?"],
35:["Целевая БД точно изолирована?","Архив и восстановление корректны?","SQL-инварианты совпали?"],
44:["Активен учебный kind-контекст?","Pod Ready и Service видит endpoints?","Тестовый запрос успешен?"],
43:["Deployment создал Pod?","Pod Ready?","Service selector находит endpoints?"],
28:["Собираются исходные метрики?","PromQL согласуется с типом метрики?","SLI и alert интерпретированы верно?"],
5:["Нужный процесс существует?","Наблюдается нагрузка на ресурсы?","Диагноз подтверждён несколькими метриками?"]
};
const match=location.pathname.match(/(?:^|\/)lessons\/(\d{2})\.html$/);
if(!match)return;
const num=Number(match[1]),path=PATHS[num];if(!path||document.getElementById('visual-guide'))return;
const mechanism=document.getElementById('mechanism'),scenario=document.getElementById('case');
if(!mechanism||!scenario)return;
const nodes=path.split('|');
const lessons=[...mechanism.querySelectorAll('ol li')].slice(0,3);
const examples=[...mechanism.querySelectorAll('article.example')].slice(0,3);
if(lessons.length!==3||examples.length!==3)return;
const css=`
#visual-guide{background:linear-gradient(160deg,#fffefa,#f8fcfa);border-color:#bad3ca}
.vs-note{font-size:13px;color:#536970}
.vs-frame{border:1px solid #d4e2dd;border-radius:13px;padding:17px;margin:18px 0;background:#f4f9f6}
.vs-frame figcaption{font-size:14px;font-weight:800;color:#244f58;margin-bottom:15px}
.vs-nodes{list-style:none;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin:0}
.vs-nodes li{position:relative;background:white;border:1px solid #bad2ca;border-radius:11px;padding:13px 11px;min-height:76px;display:flex;flex-direction:column;gap:9px;overflow-wrap:anywhere}
.vs-nodes li:not(:last-child):after{content:"→";position:absolute;left:calc(100% + 3px);top:34%;font-size:20px;color:#507970;font-weight:800}
.vs-nodes li:before{content:attr(data-idx);font:800 10px/1 monospace;color:#66817e}
.vs-nodes strong{font-size:13px;line-height:1.4}
.vs-scroll{overflow-x:auto;border:1px solid #d9e2dc;border-radius:12px;margin:18px 0;background:#fff}
.vs-table{width:100%;min-width:550px;border-collapse:collapse;text-align:left;table-layout:fixed;font-size:12.5px;line-height:1.55}
.vs-table caption{caption-side:top;text-align:left;padding:12px 14px;background:#e9f1ee;font-size:14px;font-weight:800;color:#25525c}
.vs-table th,.vs-table td{padding:11px 13px;border-bottom:1px solid #e2e7e4;vertical-align:top;overflow-wrap:anywhere}
.vs-table thead{background:#f6f8f5}.vs-table th{font-weight:750}
.vs-table tr:last-child td,.vs-table tr:last-child th{border-bottom:0}
.vs-table tbody tr:nth-child(even){background:#f9faf8}
.vs-table code{white-space:pre-wrap;font-size:11.5px}
.vs-steps{padding:0;margin:0;list-style:none;display:grid;gap:21px}
.vs-steps>li{display:grid;grid-template-columns:minmax(130px,1fr) minmax(0,1.2fr);gap:16px;align-items:center;position:relative}
.vs-steps>li:not(:last-child):after{content:"↓";position:absolute;bottom:-20px;left:29%;font-size:21px;color:#527f79;font-weight:800}
.vs-question{border:2px solid #80ada3;background:#fff;border-radius:12px;padding:17px;min-height:82px;display:flex;flex-direction:column;justify-content:center}
.vs-question span{font:800 10px/1.6 monospace;letter-spacing:.13em;text-transform:uppercase;color:#527c77}
.vs-question strong{font-size:13px;line-height:1.45}
.vs-forks{display:grid;gap:7px;font-size:12px;line-height:1.5}
.vs-forks div{padding:9px 12px;border-left:3px solid;border-radius:7px}
.vs-yes{background:#e5f2ec;border-color:#39766e!important}
.vs-no{background:#fbf0e4;border-color:#bc8b57!important}
.vs-context{border-left:3px solid #be9558;padding:11px 15px;margin:13px 0;background:#fffaef;font-size:13px}
.vs-context strong{color:#725d31}
@media(max-width:780px){.vs-nodes{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:25px}.vs-nodes li:nth-child(2):after{content:"↓";top:100%;left:49%}.vs-steps>li{grid-template-columns:1fr;gap:7px}.vs-steps>li:not(:last-child):after{left:50%}}
@media(max-width:520px){.vs-nodes{grid-template-columns:1fr;gap:24px}.vs-nodes li:not(:last-child):after,.vs-nodes li:nth-child(2):after{content:"↓";top:calc(100% + 2px);left:49%}.vs-table{min-width:480px}.vs-frame{padding:13px}}
@media print{.vs-frame,.vs-scroll{break-inside:avoid}.vs-frame{background:#fff}#visual-guide{background:#fff}}
`;
const style=document.createElement('style');style.textContent=css;document.head.append(style);
function el(tag,cl,text){const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=text;return x}
function mkTable(title,headers,rows){const wrap=el('div','vs-scroll'),t=el('table','vs-table');t.append(el('caption','',title));const thd=el('thead'),tr=el('tr');headers.forEach(h=>{const cell=el('th','',h);cell.scope='col';tr.append(cell)});thd.append(tr);t.append(thd);const tb=el('tbody');rows.forEach(row=>{const r=el('tr');row.forEach((value,i)=>{const c=el(i===0?'th':'td','',value);if(i===0)c.scope='row';r.append(c)});tb.append(r)});t.append(tb);wrap.append(t);return wrap}
const sec=el('section','unit');sec.id='visual-guide';
sec.append(el('div','section-kicker','Визуальное повторение'),el('h2','','Схемы, таблицы и алгоритм'));
sec.append(el('p','vs-note','Визуальные модели упрощают реальную архитектуру. Таблицы построены из технических правил и примеров текущего урока; наблюдения нуждаются в подтверждении на отдельном учебном стенде.'));
const figure=el('figure','vs-frame');figure.append(el('figcaption','','01 · Карта механизма'));const list=el('ol','vs-nodes');
nodes.forEach((name,i)=>{const li=el('li','');li.dataset.idx=String(i+1).padStart(2,'0');li.append(el('strong','',name));list.append(li)});
figure.append(list,el('p','vs-note','Для каждого перехода определите: какие данные или состояния передаются, какой компонент отвечает за результат и где можно измерить ошибку.'));sec.append(figure);
sec.append(mkTable('02 · Три опорных правила и границы понимания',['№','Суть технического правила'],lessons.map((x,i)=>[String(i+1).padStart(2,'0'),x.textContent.trim()])));
const rows=examples.map((x,i)=>{
const h=x.querySelector('h3')?.textContent?.trim()||`Пример ${i+1}`;
const code=x.querySelector('pre code')?.textContent?.trim()||'Код в уроке';
const sentence=x.querySelector('p')?.textContent?.trim()||'Сравните ожидаемое и фактическое поведение';
return [h,code.split('\n').slice(0,2).join('\n'),sentence]
});
sec.append(mkTable('03 · Практическая шпаргалка: код → интерпретация',['Сценарий','Команда или фрагмент','Что даёт наблюдение'],rows));
const chart=el('figure','vs-frame'),algorithm=el('ol','vs-steps');chart.append(el('figcaption','','04 · Алгоритм диагностического решения'));
const symptom=scenario.querySelector('.warning p')?.textContent?.trim()||'Наблюдается отклонение от ожидаемого поведения.';
const context=el('div','vs-context');context.append(el('strong','','Исходный симптом: '),document.createTextNode(symptom));chart.append(context);
const custom=SPECIAL[num]||[`Симптом «${nodes[3]}» воспроизведён?`,`Проверен переход через «${nodes[1]}»?`,`Результат на этапе «${nodes[2]}» подтверждён?`];
const flows=[
 [custom[0],`Уточните входные условия и исходный симптом.`,`Зафиксируйте наблюдение и перейдите к следующему слою.`],
 [custom[1],`Изучите техническую развилку в разделе «Разобранный пример»; получите stdout/stderr или trace.`,`Сравните гипотезу с независимым измерением.`],
 [custom[2],`Не объявляйте исправление; проверьте альтернативную причину и повторите эксперимент.`,`Сохраните результат, версию, условия и границы вывода.`]
];
flows.forEach(([q,no,yes],i)=>{const li=el('li',''),qel=el('div','vs-question'),fork=el('div','vs-forks');qel.append(el('span','',`Шаг ${i+1}`),el('strong','',q));const yy=el('div','vs-yes'),nn=el('div','vs-no');yy.append(el('b','','ДА → '),document.createTextNode(yes));nn.append(el('b','','НЕТ → '),document.createTextNode(no));fork.append(yy,nn);li.append(qel,fork);algorithm.append(li)});
chart.append(algorithm,el('p','vs-note','После ветви «НЕТ» повторите проверку до перехода к следующему шагу. Все изменения системы выполняются только в изолированной тестовой среде с планом восстановления.'));sec.append(chart);
scenario.parentNode.insertBefore(sec,scenario);
const nav=document.querySelector('.sidebar nav');if(nav&&!nav.querySelector('a[href="#visual-guide"]')){const a=el('a','','Схемы и таблицы');a.href='#visual-guide';const before=nav.querySelector('a[href="#case"]');if(before)nav.insertBefore(a,before);else nav.append(a)}
})();
