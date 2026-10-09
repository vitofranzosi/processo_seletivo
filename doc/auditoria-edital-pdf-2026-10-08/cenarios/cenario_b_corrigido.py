"""CENÁRIO B corrigido só pelo que as mensagens da 065 dizem, e a Retificação que desloca a numeração.

Lê o `cenario_b.py` e troca, nas seções, apenas os números que os achados apontaram: 3.x→4.x
(Da Inscrição), 4.x→6.x (Da Verificação da Autodeclaração), 8.x→11.x e "item 8.1"→"item 11.1"
(Dos Recursos), 11.x→12.x (Da Convocação), 14.x→15.x (Disposições Finais). Depois publica e retifica,
esvaziando "Do Atendimento à Pessoa com Deficiência".
"""
import re

ORIGEM = "/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-auditoria-edital-pdf-d33731/fba18c90-9168-4aeb-8300-d572628e7dd7/scratchpad/cenario_b.py"
fonte = open(ORIGEM).read()
TROCAS = {"inscricao": ("3.", "4."), "verificacao-autodeclaracao": ("4.", "6."), "recursos": ("8.", "11."), "convocacao": ("11.", "12."), "disposicoes-finais": ("14.", "15.")}
linhas = []
for linha in fonte.split("\n"):
    casada = re.match(r'    \("([\w-]+)", "', linha)
    if casada and casada[1] in TROCAS:
        de, para = TROCAS[casada[1]]
        corpo = linha[casada.end() - 1:]
        corpo = re.sub(r'(?<=["n])' + re.escape(de) + r"(\d)", para + r"\1", corpo)
        corpo = corpo.replace("item 8.1", "item 11.1")
        linha = linha[: casada.end() - 1] + corpo
    linhas.append(linha)
fonte = "\n".join(linhas).replace('previa(edital, "B-previa")\npublicar(edital, aut.pk, "B-publicado")', 'publicar(edital, aut.pk, "B-corrigido")')
assert 'publicar(edital, aut.pk, "B-corrigido")' in fonte
exec(compile(fonte, "cenario_b_corrigido", "exec"))

from comum import ator, gravar
from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato, create_retification, publish_retification, transition_retification
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

elab = ator("ana.elaboradora", "retificacao:elaborar", "retificacao:submeter")
hom = ator("bruno.homologador", "retificacao:homologar")
pub = ator("carla.publicadora", "retificacao:publicar")
base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
secao = next(s for s in base.content["sections"] if s["key"] == "atendimento-pcd")
ret, _ = create_retification(actor=elab, edital_id=edital.id, data={"baseSnapshotId": base.id, "justification": "Retirada da seção de atendimento à pessoa com deficiência.", "changes": [{"targetPath": f"/sections/id={secao['id']}/content", "operation": "REPLACE", "newValue": ""}]}, idempotency_key="auditoria-065-ret-b-elab", correlation_id="auditoria-065")
for achado in advertencias_do_ato(ret):
    if achado.code.startswith(("typed_numbering", "cross_reference")):
        print("  aviso na Retificação:", achado.code, "|", achado.message[:160])
for acao, quem in (("submeter", elab), ("homologar", hom)):
    ret, _ = transition_retification(actor=quem, retificacao_id=ret.id, expected_revision=ret.revision, action=acao, reason="Conferido.", idempotency_key=f"auditoria-065-ret-b-{acao}", correlation_id="auditoria-065")
publicacao, _ = publish_retification(actor=pub, retificacao_id=ret.id, expected_revision=ret.revision, autoridade_id=aut.pk, idempotency_key="auditoria-065-ret-b-pub", correlation_id="auditoria-065")
gravar(publicacao, "B-corrigido-retificado")
