import fs from 'node:fs';
import assert from 'node:assert/strict';
const dir=new URL('.',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1');
const dados=JSON.parse(fs.readFileSync(dir+'cenarios.json'));
const base='http://127.0.0.1:8018';
const tabs=await(await fetch('http://127.0.0.1:9228/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let seq=0;const pending=new Map(),rede=[],resultados=fs.existsSync(dir+'resultados-e2e.json')?JSON.parse(fs.readFileSync(dir+'resultados-e2e.json')):[];
function limparPost(text){if(!text)return undefined;const p=new URLSearchParams(text);p.delete('csrfmiddlewaretoken');return Object.fromEntries(p);}
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Network.requestWillBeSent'){const r=m.params.request;if(r.url.startsWith(base))rede.push({tipo:'request',url:r.url,method:r.method,form:limparPost(r.postData),redirect:m.params.redirectResponse?{url:m.params.redirectResponse.url,status:m.params.redirectResponse.status}:undefined});}else if(m.method==='Network.responseReceived'){const r=m.params.response;if(r.url.startsWith(base))rede.push({tipo:'response',url:r.url,status:r.status});}};
function cmd(method,params={}){return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
const pausa=ms=>new Promise(r=>setTimeout(r,ms));
async function ev(expression){const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function go(path){await cmd('Page.navigate',{url:base+path});await pausa(650);}
async function shot(nome){fs.writeFileSync(dir+nome+'.png',Buffer.from((await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));fs.writeFileSync(dir+nome+'.txt',await ev('document.body.innerText'));}
async function click(text){await ev(`(()=>{const x=[...document.querySelectorAll('a,button')].find(x=>x.textContent.trim()===${JSON.stringify(text)});if(!x)throw Error('Controle ausente: '+${JSON.stringify(text)});x.click()})()`);await pausa(650);}
async function login(role){await go('/gestao/identificar/demonstracao');await ev(`(()=>{document.querySelector('details.avancado').open=true;document.querySelector('#subject').value='${role}.sintetico.002';const f=document.querySelector('#subject').form;f.querySelector('input[value="${role}"]').checked=true;f.querySelector('button[type=submit]').click()})()`);await pausa(650);}
async function api(eid){const r=await fetch(base+`/api/v1/public/editais/${eid}/versao-vigente`);assert.equal(r.status,200);return r.json();}
async function admin(method,path,data,permissao,subject,revision){const headers={'Authorization':`Bearer ${subject}|cefor|${permissao}`,'Content-Type':'application/json','Idempotency-Key':crypto.randomUUID()};if(revision)headers['If-Match']=`"${revision}"`;const r=await fetch(base+path,{method,headers,body:JSON.stringify(data)});const body=await r.json();rede.push({tipo:'api-concorrente',method,path,request:data,status:r.status,response:body});assert(r.status<400,JSON.stringify(body));return body;}
async function criar(eid,nome,end,draw,vigencia=''){
 await login('elaborador');await go('/gestao/');await ev(`document.querySelector('a[href="/gestao/processos/${dados.cenarios.find(c=>c.edital===eid).processo}/"]').click()`);await pausa(650);await ev(`document.querySelector('a[href="/gestao/editais/${eid}/"]').click()`);await pausa(650);await click('Retificar');
 const campos=await ev(`(()=>{const xs=[...document.querySelectorAll('input[type="datetime-local"][name^="campo:"]')];return {base:document.querySelector('[name="base"]').value,campos:xs.map(x=>({name:x.name,value:x.value,label:document.querySelector('label[for="'+x.id+'"]')?.innerText}))}})()`);
 fs.writeFileSync(dir+nome+'-base.json',JSON.stringify(campos,null,2));
 const fim=campos.campos.find(x=>x.label==='Término');const inicio=campos.campos.filter(x=>x.label==='Início')[1];
 await ev(`(()=>{document.querySelector('[name=${JSON.stringify(fim.name)}]').value=${JSON.stringify(end)};document.querySelector('[name=${JSON.stringify(inicio.name)}]').value=${JSON.stringify(draw)};document.querySelector('#justificativa').value=${JSON.stringify(nome+' — prazo e sorteio')};document.querySelector('#vigencia').value=${JSON.stringify(vigencia)}})()`);
 await click('Ver o que vai mudar');await shot(nome+'-comparativo');await ev(`document.querySelector('button[name="confirmar"]').click()`);await pausa(650);const url=await ev('location.pathname');assert(url.includes('/retificacoes/'));await shot(nome+'-rascunho');return {eid,nome,url,rid:url.split('/')[3],end,draw,vigencia,campos};
}
async function homologar(c){await click('Submeter para revisão');await click('Confirmar: Submeter para revisão');await go(c.url);await shot(c.nome+'-revisao');await login('homologador');await go(c.url);await click('Homologar');await ev(`document.querySelector('#motivo').value='Fundamento sintético PS-RET-002'`);await click('Confirmar: Homologar');await go(c.url);await shot(c.nome+'-homologada');}
async function publicar(c,erro=false){await login('publicador');await go(c.url);await click('Publicar Retificação');await ev(`(()=>{const s=document.querySelector('select[name="signatario"]');s.value=[...s.options].find(o=>o.value).value})()`);await click('Confirmar: Publicar Retificação');await shot(c.nome+'-resultado');const text=await ev('document.body.innerText');if(erro)assert(text.includes('término anterior ao início'));else assert(text.includes('Publicada em'));await go(c.url);await shot(c.nome+'-estado');}
async function portal(c){const a=await api(c.eid);fs.writeFileSync(dir+c.nome+'-api.json',JSON.stringify(a,null,2));await go(`/selecoes/${c.eid}/`);await shot(c.nome+'-portal');return a;}
function registrar(id,c,antes,depois,detalhe){resultados.push({id,...c,antes,depois,detalhe,resultado:'APROVADO'});fs.writeFileSync(dir+'resultados-e2e.json',JSON.stringify(resultados,null,2));}
await cmd('Page.enable');await cmd('Network.enable');await cmd('Runtime.enable');
try{
 if(!process.argv.includes('continuar')){
 const e1=dados.cenarios[0].edital,antes1=await api(e1);
 const c1=await criar(e1,'E2E-01','2026-11-12T22:37','2026-11-14T14:23');
 assert.deepEqual((await api(e1)).content,antes1.content);
 await homologar(c1);assert.deepEqual((await api(e1)).content,antes1.content);await publicar(c1);const depois1=await portal(c1);
 assert.equal(depois1.content.schedule[0].endAt,'2026-11-13T01:37:00+00:00');assert.equal(depois1.content.schedule[1].startAt,'2026-11-14T17:23:00+00:00');registrar('E2E-01',c1,antes1,depois1,'Publicação imediata e duas datas conferidas');
 const e2=dados.cenarios[1].edital,antes2=await api(e2);
 const futura=await criar(e2,'E2E-05','2026-11-12T22:37','2026-11-14T14:23','2026-10-30T12:00');await homologar(futura);await publicar(futura);const depoisFutura=await portal(futura);assert.deepEqual(depoisFutura.content,antes2.content);registrar('E2E-05',futura,antes2,depoisFutura,'Publicada futura sem efeito antecipado');
 const imediata=await criar(e2,'E2E-02','2026-11-11T21:17','2026-11-13T15:29');assert.equal(imediata.campos.base,antes2.id);await homologar(imediata);await publicar(imediata);const depoisImediata=await portal(imediata);assert.equal(depoisImediata.content.schedule[0].endAt,'2026-11-12T00:17:00+00:00');registrar('E2E-02',imediata,antes2,depoisImediata,'Base vigente e imediata publicável com ato futuro preservado');
 }
 const e3=dados.cenarios[2].edital,antesCriacao=await api(e3);
 // A tentativa inicial de intervalo invertido foi recusada na criação, antes de haver UUID.
 const invalida=await criar(e3,'E2E-03','2026-11-06T12:00','2026-11-14T14:23');await homologar(invalida);
 const caminho='/schedule/id='+antesCriacao.content.schedule[0].id+'/startAt';
 let concorrente=await admin('POST',`/api/v1/admin/editais/${e3}/retificacoes`,{baseSnapshotId:antesCriacao.id,justification:'Concorrente válido que move apenas o início',changes:[{targetPath:caminho,operation:'REPLACE',newValue:'2026-11-06T23:00:00-03:00'}]},'retificacao:elaborar','criadora.concorrente');
 const rp=`/api/v1/admin/retificacoes/${concorrente.id}`;
 concorrente=await admin('POST',rp+'/submissoes',{},'retificacao:submeter','criadora.concorrente',concorrente.revision);
 concorrente=await admin('POST',rp+'/homologacoes',{reason:'Fundamento concorrente válido'},'retificacao:homologar','homologadora.concorrente',concorrente.revision);
 await admin('POST',rp+'/publicacoes',{signatory:{authorityId:dados.autoridade}},'retificacao:publicar','publicadora.concorrente',concorrente.revision);
 const antes3=await api(e3);await publicar(invalida,true);const depois3=await portal(invalida);assert.deepEqual(depois3,antes3);registrar('E2E-03',invalida,antes3,depois3,'Criação inválida recusada; 422 na publicação quando ato concorrente inverteria intervalo; versão válida preservada');
 const e4=dados.cenarios[3].edital,antes4=await api(e4);
 const rascunho=await criar(e4,'E2E-04','2026-11-12T22:37','2026-11-14T14:23');const depois4=await portal(rascunho);assert.deepEqual(depois4,antes4);registrar('E2E-04',rascunho,antes4,depois4,'Rascunho sem alteração pública');
 await login('elaborador');await go(invalida.url+'atos/publicar');await shot('E2E-06-sem-permissao');
 const negado=await ev(`fetch(location.href,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':document.cookie.split('; ').find(x=>x.startsWith('csrftoken=')).split('=')[1]},body:new URLSearchParams({chave_idempotencia:'negado-ps-ret-002',signatario:${JSON.stringify(dados.autoridade)}})}).then(async r=>({status:r.status,body:await r.text()}))`);
 assert.equal(negado.status,403);fs.writeFileSync(dir+'E2E-06-resposta.json',JSON.stringify({status:negado.status,mensagem:negado.body.includes('permiss')},null,2));const depois6=await api(e3);assert.deepEqual(depois6,antes3);registrar('E2E-06',{...invalida,nome:'E2E-06'},antes3,depois6,'POST real sem permissão 403, sem efeito');
 console.log(resultados.map(x=>({id:x.id,rid:x.rid,resultado:x.resultado})));
}catch(e){console.error(e);await shot('falha-e2e');process.exitCode=1;}
finally{fs.writeFileSync(dir+(process.argv.includes('continuar')?'rede-continuacao-sanitizada.json':'rede-sanitizada.json'),JSON.stringify(rede,null,2));ws.close();}
