exec(open("/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-auditoria-edital-pdf-d33731/fba18c90-9168-4aeb-8300-d572628e7dd7/scratchpad/cenario_a.py").read())
from comum import ator, gravar
from processo_seletivo.publicacoes.application.retificacoes import create_retification, transition_retification, publish_retification
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

elab = ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
hom = ator("bruno.homologador", "retificacao:homologar")
pub = ator("carla.publicadora", "retificacao:publicar")
base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
conteudo = base.content
inscr = next(e for e in conteudo["schedule"] if e.get("isRegistrationPeriod"))
perfil0 = conteudo["profiles"][0]
geral = next(l for l in perfil0["vacancyTable"] if l.get("modalityId") is None)
mudancas = [
    {"targetPath": f"/schedule/id={inscr['id']}/endAt", "operation": "REPLACE", "newValue": "2026-11-04T23:59:00-03:00"},
    {"targetPath": f"/profiles/id={perfil0['id']}/immediateVacancies", "operation": "REPLACE", "newValue": 45},
    {"targetPath": f"/profiles/id={perfil0['id']}/vacancyTable/id={geral['id']}/immediateVacancies", "operation": "REPLACE", "newValue": 33},
]
ret, _ = create_retification(actor=elab, edital_id=edital.id, data={"baseSnapshotId": base.id, "justification": "Prorrogação das inscrições e ampliação de vagas no polo Bom Jesus do Norte.", "changes": mudancas}, idempotency_key="auditoria-pdf-ret-a-elab", correlation_id="auditoria-pdf")
for acao, quem in (("submeter", elab), ("homologar", hom)):
    ret, _ = transition_retification(actor=quem, retificacao_id=ret.id, expected_revision=ret.revision, action=acao, reason="Conferido.", idempotency_key=f"auditoria-pdf-ret-a-{acao}", correlation_id="auditoria-pdf")
publicacao, _ = publish_retification(actor=pub, retificacao_id=ret.id, expected_revision=ret.revision, autoridade_id=aut.pk, idempotency_key="auditoria-pdf-ret-a-pub", correlation_id="auditoria-pdf")
gravar(publicacao, "A-retificado")
