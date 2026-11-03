import fs from 'node:fs';
const dir=new URL('.',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1');
const base='http://127.0.0.1:8017';
const dados=JSON.parse(fs.readFileSync(dir+'cenarios.json'));
const tabs=await(await fetch('http://127.0.0.1:9227/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map(),network=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method?.startsWith('Network.'))network.push(m);};
function cmd(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function ev(expression){const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function go(path){await cmd('Page.navigate',{url:path.startsWith('http')?path:base+path});await pause(700);}
async function shot(name){fs.writeFileSync(dir+name+'.png',Buffer.from((await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));fs.writeFileSync(dir+name+'.txt',await ev('document.body.innerText'));}
async function click(text){await ev(`(()=>{const x=[...document.querySelectorAll('a,button')].find(x=>x.textContent.trim()===${JSON.stringify(text)});if(!x)throw Error('Controle ausente: '+${JSON.stringify(text)});x.click()})()`);await pause(700);}
async function login(role){await go('/gestao/identificar/demonstracao');await ev(`(()=>{document.querySelector('details.avancado').open=true;document.querySelector('#subject').value='${role}.sintetico';const f=document.querySelector('#subject').form;f.querySelector('input[value="${role}"]').checked=true;f.querySelector('button[type=submit]').click()})()`);await pause(700);}
await cmd('Page.enable');await cmd('Network.enable');await cmd('Runtime.enable');
const mode=process.argv[2]||'inspect';
try{
 if(mode==='inspect'){
  await login('elaborador');await go('/gestao/');await shot('00-lista');await go(`/gestao/editais/${dados.cenarios[0].edital}/`);await click('Retificar');await shot('01-formulario');
  console.log(await ev(`JSON.stringify([...document.querySelectorAll('input')].map(x=>({name:x.name,type:x.type,value:x.value,label:x.closest('label')?.innerText||document.querySelector('label[for="'+x.id+'"]')?.innerText})))`));
 }else if(mode==='base'){
  const eid=dados.cenarios[1].edital;await login('elaborador');await go(`/gestao/editais/${eid}/retificar`);
  const fields=await ev(`JSON.stringify({base:document.querySelector('[name="base"]').value,dates:[...document.querySelectorAll('input[type="datetime-local"]')].map(x=>({name:x.name,value:x.value}))})`);
  fs.writeFileSync(dir+'base-futura.json',fields);await shot('base-futura-formulario');
  await ev(`(()=>{const x=[...document.querySelectorAll('input')].find(x=>document.querySelector('label[for="'+x.id+'"]')?.innerText==='Término');x.value='2026-11-13T22:37';document.querySelector('#justificativa').value='Teste de base futura com vigência imediata';})()`);
  await click('Ver o que vai mudar');await shot('base-futura-comparativo');await ev(`document.querySelector('button[name="confirmar"]').click()`);await pause(700);
  const url=await ev('location.pathname');fs.writeFileSync(dir+'base-futura-url.txt',url);
  await click('Submeter para revisão');await click('Confirmar: Submeter para revisão');await login('homologador');await go(url);await click('Homologar');await ev(`document.querySelector('#motivo').value='Teste de base futura'`);await click('Confirmar: Homologar');
  await login('publicador');await go(url);await click('Publicar Retificação');await ev(`(()=>{const s=document.querySelector('select[name="signatario"]');s.value=[...s.options].find(o=>o.value).value})()`);await click('Confirmar: Publicar Retificação');await shot('base-futura-resultado');
  await login('elaborador');await go(`/gestao/editais/${eid}/`);await shot('pendencias-ausentes');
  await go('/gestao/retificacoes/00000000-0000-0000-0000-000000000099/');await shot('erro-inexistente');
  const cases=JSON.parse(fs.readFileSync(dir+'resultados-navegador.json'));await go(cases[2].url+'atos/publicar');await shot('erro-sem-permissao');
  await ev(`fetch(location.href,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':document.cookie.split('; ').find(x=>x.startsWith('csrftoken=')).split('=')[1]},body:new URLSearchParams({chave_idempotencia:'tentativa-sem-permissao-001',signatario:${JSON.stringify(dados.autoridade)}})}).then(async r=>({status:r.status,body:await r.text()}))`).then(r=>fs.writeFileSync(dir+'erro-sem-permissao-post.json',JSON.stringify(r,null,2)));
 }else{
  const out=[];
  for(let i=0;i<4;i++){
   await login('elaborador');await go('/gestao/');await ev(`document.querySelector('a[href="/gestao/processos/${dados.cenarios[i].processo}/"]').click()`);await pause(700);
   const eid=dados.cenarios[i].edital;
   await ev(`document.querySelector('a[href="/gestao/editais/${eid}/"]').click()`);await pause(700);await click('Retificar');
   const inputs=await ev(`(()=>{const xs=[...document.querySelectorAll('input[type="datetime-local"][name^="campo:"]')];return xs.map(x=>({name:x.name,value:x.value,label:document.querySelector('label[for="'+x.id+'"]')?.innerText,context:x.closest('section')?.innerText.slice(0,250)}))})()`);
   fs.writeFileSync(dir+`campos-${i}.json`,JSON.stringify(inputs,null,2));
   const ends=inputs.filter(x=>x.label?.includes('Término'));const starts=inputs.filter(x=>x.label?.includes('Início'));
   if(!ends[0]||!starts[1])throw Error('Campos temporais não identificados '+JSON.stringify(inputs));
   const end=new Date(Date.now()+15*86400000).toISOString().slice(0,10)+'T22:37';const draw=new Date(Date.now()+17*86400000).toISOString().slice(0,10)+'T14:23';
   const future=new Date(Date.now()+2*86400000).toISOString().slice(0,10)+'T12:00';const past='2026-01-01T12:00';
   await ev(`(()=>{document.querySelector('[name=${JSON.stringify(ends[0].name)}]').value=${JSON.stringify(end)};document.querySelector('[name=${JSON.stringify(starts[1].name)}]').value=${JSON.stringify(draw)};document.querySelector('#justificativa').value='PS-RET-E2E-001 cenário ${i+1}: prazo e sorteio';document.querySelector('#vigencia').value=${JSON.stringify(i===1?future:i===2?past:'')};})()`);
   await click('Ver o que vai mudar');await shot(`c${i+1}-comparativo`);
   await ev(`document.querySelector('button[name="confirmar"]').click()`);await pause(800);
   const url=await ev('location.pathname');if(!url.includes('/retificacoes/'))throw Error(await ev('document.body.innerText'));
   const rid=url.split('/')[3];await shot(`c${i+1}-elaboracao`);
   const before=await(await fetch(base+`/api/v1/public/editais/${eid}/versao-vigente`)).json();
   await click('Submeter para revisão');await click('Confirmar: Submeter para revisão');await go(url);await shot(`c${i+1}-revisao`);
   await login('homologador');await go(url);
   if(i===3){await click('Devolver para elaboração');await ev(`document.querySelector('#motivo').value='Devolução sintética para testar edição'`);await click('Confirmar: Devolver para elaboração');await shot('c4-devolvida');out.push({eid,rid,url,end,draw,kind:'devolvida'});continue;}
   await click('Homologar');await ev(`document.querySelector('#motivo').value='Fundamento sintético PS-RET-E2E-001'`);await click('Confirmar: Homologar');await go(url);await shot(`c${i+1}-homologada`);
   await login('publicador');await go(url);await click('Publicar Retificação');await shot(`c${i+1}-confirmacao`);
   await ev(`(()=>{const s=document.querySelector('select[name="signatario"]');s.value=[...s.options].find(o=>o.value).value;})()`);
   await click('Confirmar: Publicar Retificação');await shot(`c${i+1}-resultado`);
   const after=await(await fetch(base+`/api/v1/public/editais/${eid}/versao-vigente`)).json();
   fs.writeFileSync(dir+`c${i+1}-api.json`,JSON.stringify({before,after},null,2));
   await go(`/selecoes/${eid}/`);await shot(`c${i+1}-portal`);
   out.push({eid,rid,url,end,draw,kind:i===0?'imediata':i===1?'futura':'vencida'});
   fs.writeFileSync(dir+'resultados-navegador.json',JSON.stringify(out,null,2));
  }
  fs.writeFileSync(dir+'resultados-navegador.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out));
 }
}catch(e){console.error(e);await shot('falha-navegador');process.exitCode=1;}
finally{fs.writeFileSync(dir+'rede-'+mode+'.json',JSON.stringify(network,null,2));ws.close();}
