"""O percurso emblemático da `009`, ponta a ponta e pelo canal de cada ator (SC-017).

Um teste, e ele existe para provar a **jornada**, não as regras: cada regra já tem o seu, e o que
este acrescenta é que as peças se encaixam na ordem em que uma pessoa real as encontra. É o
critério do princípio VI da Constituição — capacidade que o domínio sustenta mas que nenhuma
interface alcança não está entregue.

O que ainda falta aqui é a última parte do SC-017: a equipe abrindo `Inscrições` e visualizando os
documentos. Ela chega na entrega 6, e este arquivo cresce com ela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.candidato import MODALIDADE_PPP, PERFIL_DOCENTE, pdf
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_do_edital_publicado_ao_protocolo_do_candidato(client, selecao):
    """Gestor publica; candidata encontra, se inscreve e recebe protocolo — só pelo navegador.

    `selecao` é o Edital publicado pelo canal administrativo, com três atores distintos —
    elaborador, homologador e publicador — como as features anteriores já demonstram.
    """
    # 1. Encontra a seleção sem se identificar, e o convite existe porque o período está aberto.
    vitrine = client.get(reverse("portal:vitrine")).content.decode()
    assert "Processo Seletivo 2026" in vitrine

    detalhe = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()
    assert "Inscrições abertas até" in detalhe
    assert "Inscrever-se nesta vaga" in detalhe

    # 2. Aciona o convite da vaga e é levada a identificar-se — voltando para a mesma vaga.
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    assert client.post(vaga)["Location"] == f"{reverse('portal:identificar')}?destino={vaga}"

    identificada = client.post(
        reverse("portal:identificar"),
        {
            "nome": "Maria Silva",
            "cpf": "123.456.789-09",
            "email": "maria@exemplo.br",
            "destino": vaga,
        },
    )
    inscricao = Inscricao.objects.get()
    assert identificada["Location"] == reverse("portal:inscricao", args=[inscricao.id])
    assert str(inscricao.profile_id) == PERFIL_DOCENTE, "chegou pela vaga, e não escolheu de novo"

    # 3. A tela traz os dados da identidade e pede só o que falta.
    sua_inscricao = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert "Maria Silva" in sua_inscricao and "maria@exemplo.br" in sua_inscricao
    assert 'name="nome"' not in sua_inscricao, "nada do que a identidade forneceu é redigitado"
    assert "0 de 2" in sua_inscricao, "sem modalidade escolhida, dois documentos"

    # 4. Escolhe a modalidade reservada, e o sistema passa a pedir exatamente três documentos.
    client.post(
        reverse("portal:inscricao", args=[inscricao.id]),
        {"modalidade": MODALIDADE_PPP, "telefone": "(27) 99999-0000"},
    )
    com_modalidade = client.get(
        reverse("portal:inscricao", args=[inscricao.id])
    ).content.decode()
    assert "0 de 3" in com_modalidade
    assert "Autodeclaração étnico-racial" in com_modalidade

    # 5. Envia os três PDFs, cada um no seu requisito.
    for requisito, nome in (
        (DOCUMENTO_DE_TODOS, "identidade.pdf"),
        (DOCUMENTO_DO_PERFIL, "diploma.pdf"),
        (DOCUMENTO_DA_MODALIDADE, "autodeclaracao.pdf"),
    ):
        enviado = client.post(
            reverse("portal:enviar-documento", args=[inscricao.id, requisito]),
            {"arquivo": pdf(nome)},
        )
        assert enviado.status_code == 200
    assert "3 de 3" in client.get(
        reverse("portal:inscricao", args=[inscricao.id])
    ).content.decode()

    # 6. Revisa: tudo o que ela declarou, com os três arquivos nomeados.
    revisao = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()
    for esperado in ("Professor de Informática", "Maria Silva", "identidade.pdf", "diploma.pdf"):
        assert esperado in revisao
    assert "Falta enviar" not in revisao

    # 7. Aceita as declarações, envia, e recebe o protocolo.
    envio = client.post(
        reverse("portal:revisao", args=[inscricao.id]), {"veracidade": "on", "ciencia": "on"}
    )
    assert envio["Location"] == reverse("portal:comprovante", args=[inscricao.id])

    inscricao.refresh_from_db()
    comprovante = client.get(envio["Location"]).content.decode()
    assert inscricao.protocolo in comprovante
    assert "Inscrição realizada" in comprovante
    assert inscricao.status == Inscricao.Status.SUBMETIDA
    assert inscricao.versao_aceita_id is not None
    assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == 3

    # 8. Volta à seleção depois e reencontra o que fez.
    de_volta = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()
    assert "Inscrição enviada" in de_volta
    assert "Ver comprovante" in de_volta
