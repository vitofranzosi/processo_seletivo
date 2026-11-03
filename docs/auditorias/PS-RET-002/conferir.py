"""HTTP real e SQL somente leitura no cluster exclusivo PS-RET-002."""
import sys,json,urllib.request,urllib.error,uuid
from pathlib import Path
sys.path.insert(0,'/app/backend')
import django
django.setup()
from django.db import connection
assert connection.settings_dict['HOST']=='ps-ret-002-db'
assert connection.settings_dict['NAME']=='auditoria_ret_002'
from processo_seletivo.publicacoes.models_retificacao import Retificacao
p=Path('/evidencias');dados=json.loads((p/'cenarios.json').read_text());casos=json.loads((p/'resultados-e2e.json').read_text());http=[]
def request(nome,method,path,payload=None,permissao=None,revision=None,esperado=403):
 headers={'Content-Type':'application/json','Idempotency-Key':str(uuid.uuid4())}
 if permissao is not None:headers['Authorization']=f'Bearer ator.sintetico.002|cefor|{permissao}'
 if revision is not None:headers['If-Match']=f'"{revision}"'
 req=urllib.request.Request('http://127.0.0.1:8000'+path,method=method,headers=headers,data=json.dumps(payload).encode() if payload is not None else None)
 try:r=urllib.request.urlopen(req)
 except urllib.error.HTTPError as e:r=e
 body=r.read().decode();http.append({'nome':nome,'method':method,'path':path,'request':payload,'status':r.status,'expected':esperado,'passed':r.status==esperado,'response':json.loads(body) if body.startswith('{') else None})
 assert r.status==esperado,(nome,r.status,body)
 return http[-1]['response']
draft=next(c for c in casos if c['id']=='E2E-04');r=Retificacao.objects.get(pk=draft['rid']);event=r.base_snapshot.content['schedule'][0]
payload={'baseSnapshotId':str(r.base_snapshot_id),'justification':'Teste de autorização','changes':[{'targetPath':f'/schedule/id={event["id"]}/endAt','operation':'REPLACE','newValue':'2026-11-13T01:37:00+00:00'}]}
request('criar-sem-permissao','POST',f'/api/v1/admin/editais/{r.edital_id}/retificacoes',payload,'retificacao:publicar')
request('editar-sem-permissao','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:homologar',r.revision)
request('submeter-sem-permissao','POST',f'/api/v1/admin/retificacoes/{r.id}/submissoes',{},'retificacao:publicar',r.revision)
request('homologar-sem-permissao','POST',f'/api/v1/admin/retificacoes/{r.id}/homologacoes',{'reason':'Teste'},'retificacao:publicar',r.revision)
request('devolver-sem-permissao','POST',f'/api/v1/admin/retificacoes/{r.id}/devolucoes',{'reason':'Teste'},'retificacao:publicar',r.revision)
invalida=next(c for c in casos if c['id']=='E2E-03');i=Retificacao.objects.get(pk=invalida['rid'])
request('publicar-sem-permissao','POST',f'/api/v1/admin/retificacoes/{i.id}/publicacoes',{'signatory':{'authorityId':dados['autoridade']}},'retificacao:elaborar',i.revision)
request('edicao-autorizada','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:elaborar',r.revision,200)
request('edicao-obsoleta','PUT',f'/api/v1/admin/retificacoes/{r.id}/rascunho',payload,'retificacao:elaborar',r.revision,412)
request('historico-publico-anonimo','GET',f'/api/v1/public/editais/{r.edital_id}/historico',esperado=200)
for c in casos:
 request('versao-vigente-anonima-'+c['id'],'GET',f'/api/v1/public/editais/{c["eid"]}/versao-vigente',esperado=200)
(p/'autorizacao-http.json').write_text(json.dumps(http,ensure_ascii=False,indent=2))
queries={
'retificacoes':'SELECT id,edital_id,status,revision,base_snapshot_id,publication_id,justification,effective_at,created_by,created_at,prepared_by,submitted_at,homologated_by,homologated_at,homologation_reason FROM publicacoes_retificacao ORDER BY created_at',
'alteracoes':'SELECT retificacao_id,target_path,new_value,expected_previous_hash FROM publicacoes_alteracaonormativa ORDER BY retificacao_id,"order"',
'publicacoes':'SELECT id,edital_id,publication_order,published_at,effective_at,published_by,content_hash,canonical_content FROM publicacoes_publicacao ORDER BY edital_id,publication_order',
'versoes':'SELECT id,edital_id,valid_from,materialized_at,source_publication_id,content,content_hash,applied_publications FROM publicacoes_versaoconsolidada ORDER BY edital_id,valid_from,materialized_at',
'auditoria':"SELECT aggregate_id,actor_subject,operation,occurred_at,previous_state,new_state,reason FROM auditoria_registroauditoria ORDER BY occurred_at",
'privilegios':"SELECT tablename,has_table_privilege('auditoria_002_runtime',quote_ident(schemaname)||'.'||quote_ident(tablename),'UPDATE') AS atualiza,has_table_privilege('auditoria_002_runtime',quote_ident(schemaname)||'.'||quote_ident(tablename),'DELETE') AS exclui FROM pg_tables WHERE schemaname='public' AND tablename IN ('publicacoes_publicacao','publicacoes_versaoconsolidada','auditoria_registroauditoria')"
}
snapshot={}
for nome,sql in queries.items():
 with connection.cursor() as cur:
  cur.execute(sql);rows=[dict(zip([d[0] for d in cur.description],row)) for row in cur.fetchall()]
  for row in rows:
   for k,v in row.items():
    if isinstance(v,(memoryview,bytes)):row[k]=bytes(v).decode()
    if k in ('content','applied_publications') and isinstance(v,str):row[k]=json.loads(v)
  snapshot[nome]={'sql':sql,'rows':rows}
(p/'postgresql.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2,default=str))
print('HTTP',len(http),'aprovados');print('SQL',[(k,len(v['rows'])) for k,v in snapshot.items()])
