"""O cenário instruível da `036`: uma peça admitida, com parecer escrito e documento apresentado.

Ela existe porque quatro módulos de teste precisam do mesmo ponto de partida — o alcance, a tela de
quem julga, a trilha e o parecer do titular —, e montá-lo em cada um faria os quatro divergirem no
primeiro ajuste.

**O caminho é o real** em tudo que o produto sabe fazer: avaliar com parecer, consolidar, divulgar,
interpor e admitir passam pelos comandos. A decisão é a exceção, e é a mesma exceção que as fixtures
da `018` já abrem: `DecisaoRecurso.objects.create` em vez do comando, porque julgar pelo comando
exigiria montar o alvo da correção — e o que estes testes precisam da decisão é só que ela
**exista**, para que o alcance feche.
"""

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.conftest import ator_institucional
from tests.fixtures.edital import identificador
from tests.fixtures.recursos import decidir
from tests.fixtures.recursos_us4 import JULGADORA, cenario_julgavel, julgador

# O texto que o avaliador escreveu, e é ele que a feature entrega. **Uma frase de domínio, e não
# "Atende"**: as asserções procuram por substring, e um rótulo curto e comum é indistinguível de
# ruído de página — foi assim que um protocolo de quatro dígitos derrubou um teste de vazamento uma
# vez em mil execuções.
PARECER = "O currículo apresentado não comprova os seis meses de experiência exigidos."
# O requisito do documento apresentado. Derivado de `identificador`, como toda identidade dos
# cenários: um UUID fixo colidiria entre Editais do mesmo teste.
REQUISITO_BASE = 436
# Quem instrui, na gestão e nos testes de integração: julga **e** gere a comissão. Nome próprio para
# que a trilha e as asserções distingam quem instruiu de quem julgou.
INSTRUTORA = "marcia.gestora"


def requisito_de(seed=0):
    return identificador(REQUISITO_BASE, seed)


def cenario_instruivel(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    seed,
    codigo,
    admitir_a_peca=True,
    janela_recursal=None,
):
    """Peça admitida contra um Resultado **eliminado com parecer**, e um documento na inscrição.

    A primeira nota é 55 contra mínima 60, como em `cenario_julgavel`: é a eliminação que faz o
    parecer ser obrigatório, e é contra ela que o recurso corre.
    """
    montado = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        admitir_a_peca=admitir_a_peca,
        parecer=PARECER,
        documentos=[requisito_de(seed)],
        janela_recursal=janela_recursal,
    )
    inscricao = montado["inscricao"]
    montado["documento"] = inscricao.documentos.get(requirement_id=requisito_de(seed))
    montado["parecer"] = PARECER
    montado["outra_inscricao"] = montado["cenario"]["inscricoes"][1]
    return montado


def decidir_a_peca(montado, *, especie=DecisaoRecurso.Especie.INDEFERIDO):
    """A decisão que **fecha o alcance** — o indeferimento, espécie sem efeito sobre Resultado.

    Indeferir é o desfecho mais barato de montar e o mais honesto para o que estes testes medem: o
    alcance morre com **qualquer** decisão, e não com o deferimento. Usar a correção fixada
    obrigaria a declarar par, protegido e consequência, e nada disso muda o que se afere.
    """
    return decidir(
        montado["recurso"],
        especie=especie,
        versao=selecao_publica(edital_id=montado["inscricao"].edital_id),
    )


def inadmitir_a_peca(montado, *, motivo="Intempestivo: a peça chegou depois da janela."):
    """O **outro** desfecho terminal de um recurso, e o que a `036` esquecera (`FR-529`).

    Juízo negativo encerra a peça sem mérito, e o banco garante que ele é definitivo: a trigger
    `decisao_recurso_coerente` recusa decisão sobre recurso não admitido. Um alcance que espere pela
    decisão, portanto, **nunca** fecha — não é uma janela larga, é uma janela sem fechadura.
    """
    from processo_seletivo.recursos.application.admitir import admitir
    from tests.fixtures.recursos_us4 import assinatura_de

    return admitir(
        actor=julgador(),
        recurso_id=montado["recurso"].id,
        admitido=False,
        motivo=motivo,
        assinatura_do_estado=assinatura_de(montado["recurso"]),
        idempotency_key=f"inadmitir-{montado['recurso'].id}",
    )


def outra_peca(montado, *, chave="interpor-outra-036"):
    """Um **segundo** recurso da mesma Etapa, do outro candidato — a contraprova da `T021`.

    É o que distingue ato de permissão: o mesmo julgador, na mesma Etapa e no mesmo Edital, não pode
    alcançar nada por causa da instrução praticada na primeira peça. Se alcançar, o que se construiu
    foi uma permissão com outro nome.

    A segunda inscrição foi pontuada com 90 e **habilitada**, de modo que ela não tem eliminação a
    contestar. O que ela tem é o mesmo Resultado vigente, e é contra ele que a peça corre: recorrer
    de resultado favorável é possível — a `018` não exige prejuízo para interpor.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos_us4 import assinatura_de

    inscricao = montado["outra_inscricao"]
    etapa = montado["cenario"]["etapa_do_recurso"]
    resultado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=etapa)
    peca = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "outra@ex.br"
        ),
        inscricao=inscricao,
        resultado=resultado,
        fundamentacao="A pontuação atribuída não corresponde aos critérios publicados.",
        assinatura_do_objeto=str(resultado.pk),
        idempotency_key=chave,
    )
    admitir(
        actor=julgador(),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo e regularmente instruído.",
        assinatura_do_estado=assinatura_de(peca),
        idempotency_key=f"admitir-{chave}",
    )
    peca.refresh_from_db()
    return peca


def autoridade(subject=INSTRUTORA):
    """Quem instrui **com documento**: julga, gere a comissão e consulta inscrições (FR-530).

    As três são as do papel `gestor` somado ao `julgador`, e nenhuma é nova — é exatamente o ator
    que `test_quem_consulta_inscricoes_alcanca_os_documentos` já usava antes desta feature.

    **`inscricao:consultar` está aqui porque instruir documento exige alcançá-lo.** A base composta
    — gestão ou presidência — autoriza o **ato**; ela não concede leitura dos documentos do
    candidato, e quem não os abre não os anexa: seria conceder a si mesmo, por um `POST`, o acesso
    que a porta nega.

    A presidência **sem** `inscricao:consultar` continua instruindo o parecer, e é o caso de
    `test_quem_nao_consulta_inscricoes_ainda_instrui_o_parecer`.
    """
    return ator_institucional(subject, "recurso:julgar", "comissao:gerir", "inscricao:consultar")


__all__ = [
    "INSTRUTORA",
    "JULGADORA",
    "PARECER",
    "autoridade",
    "cenario_instruivel",
    "decidir_a_peca",
    "inadmitir_a_peca",
    "julgador",
    "outra_peca",
    "requisito_de",
]
