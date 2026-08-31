"""O envio dos documentos (US4 da 009, FR-041 a FR-053).

Três propriedades, e as três são o que separa esta feature de um formulário com anexo: o arquivo
persiste sozinho, ele fica ligado ao requisito que atende, e a recusa de um não custa os outros.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_PPP,
    identificar,
    imagem,
    pdf,
)
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)


def _enviar(client, inscricao, requisito, arquivo):
    return client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, requisito]), {"arquivo": arquivo}
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_persiste_na_hora_e_sem_salvar(client, inscricao_de_maria):
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    assert resposta.status_code == 200
    documento = DocumentoSubmetido.objects.get()
    assert str(documento.requirement_id) == DOCUMENTO_DE_TODOS
    assert documento.nome_original == "rg.pdf"
    assert documento.tamanho > 0
    assert len(documento.content_hash) == 64


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_nome_fisico_nao_e_o_nome_enviado(client, inscricao_de_maria, raiz_de_arquivos):
    """FR-052: nome de arquivo carrega dado pessoal, e viaja em log, backup e listagem."""
    identificar(client, MARIA)

    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("cpf-de-maria-silva.pdf"))

    documento = DocumentoSubmetido.objects.get()
    assert "maria" not in documento.arquivo.name.lower()
    assert documento.nome_original == "cpf-de-maria-silva.pdf"
    assert str(inscricao_de_maria.id) in documento.arquivo.name


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_contagem_conta_os_obrigatorios_que_faltam(client, inscricao_de_maria):
    identificar(client, MARIA)

    antes = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))
    assert "0 de 2" in antes.content.decode(), "ampla concorrência recebe dois pedidos"

    depois = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf())

    assert "1 de 2" in depois.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_de_um_envio_nao_derruba_os_outros(client, inscricao_de_maria):
    """FR-049: cada arquivo numa requisição própria, e é isso que preserva o que já valia."""
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    recusa = _enviar(client, inscricao_de_maria, DOCUMENTO_DO_PERFIL, imagem())

    corpo = recusa.content.decode()
    assert "imagem" in corpo and "Converta" in corpo
    assert "rg.pdf" in corpo, "o que já estava enviado continua lá"
    assert DocumentoSubmetido.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_substituir_sobrescreve_e_descarta_o_anterior(
    client, inscricao_de_maria, raiz_de_arquivos
):
    """FR-043 e FR-050: um arquivo por requisito, e fica claro qual passou a valer."""
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("primeiro.pdf"))
    caminho_antigo = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("segundo.pdf"))

    assert DocumentoSubmetido.objects.count() == 1
    documento = DocumentoSubmetido.objects.get()
    assert documento.nome_original == "segundo.pdf"
    assert "segundo.pdf" in resposta.content.decode()
    assert not caminho_antigo.exists(), "o arquivo antigo sai do disco junto"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_remover_apaga_o_registro_e_o_arquivo(client, inscricao_de_maria, raiz_de_arquivos):
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf())
    caminho = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    client.post(
        reverse("portal:remover-documento", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS])
    )

    assert DocumentoSubmetido.objects.count() == 0
    assert not caminho.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_modalidade_decide_quantos_documentos_sao_pedidos(client, inscricao_de_maria):
    """O cenário emblemático: ampla concorrência recebe dois pedidos; a reservada, três."""
    identificar(client, MARIA)
    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_PPP, "confirmar_descarte": "1"},
    )

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert "0 de 3" in corpo
    assert "Autodeclaração étnico-racial" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_envio_e_auditado_sem_o_nome_do_arquivo(client, inscricao_de_maria):
    from processo_seletivo.auditoria.models import RegistroAuditoria

    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("cpf-de-maria.pdf"))

    registro = RegistroAuditoria.objects.filter(operation="ANEXAR").get()

    assert registro.actor_subject == MARIA.subject
    assert DOCUMENTO_DE_TODOS in registro.reason
    assert "maria" not in registro.reason.lower()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_documento_de_modalidade_nao_pedida_nao_e_aceito(client, inscricao_de_maria):
    """FR-044: o requisito da modalidade PPP não se aplica a quem concorre sem reserva."""
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DA_MODALIDADE, pdf())

    assert resposta.status_code == 404
    assert DocumentoSubmetido.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quantos_documentos_faltam_aparece_junto_ao_cabecalho(client, inscricao_de_maria):
    """SC-UX-003: sem rolagem adicional.

    A contagem do bloco começa abaixo da dobra em 375px — medido em 969px, contra 812px de altura
    útil. "Quantos faltam" é a pergunta que decide se a pessoa continua agora ou volta depois com
    os arquivos, e ela não pode custar uma rolagem para ser respondida.
    """
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert 'id="resumo-documentos"' in corpo
    assert corpo.index("resumo-documentos") < corpo.index("Seus dados"), "acima da dobra"
    assert "Faltam" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_resumo_do_cabecalho_acompanha_o_envio(client, inscricao_de_maria):
    """Ele vive fora do `#documentos` e não seria alcançado pela troca normal do htmx.

    Sem a atualização fora de banda, o topo continuaria anunciando o que faltava antes do envio —
    um número errado num lugar de destaque é pior do que número nenhum.
    """
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    fragmento = resposta.content.decode()
    assert 'hx-swap-oob="true"' in fragmento, "o resumo do topo volta junto com o bloco"
    resumo = fragmento[fragmento.index('id="resumo-documentos"') :][:400]
    assert "Falta" in resumo and "1" in resumo, "o topo já conta o que acabou de chegar"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_aviso_de_nao_fechar_a_pagina_fica_escondido_em_repouso(client, inscricao_de_maria):
    """FR-048: o aviso é do envio em curso.

    `display` de classe vence o `[hidden]` da folha do navegador. Sem a regra explícita, uma barra
    vazia e um "não feche esta página" apareciam sob **cada** requisito de quem ainda nem tinha
    escolhido o arquivo — o oposto de tranquilizar.
    """
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert '<p class="progresso" hidden>' in corpo
    assert ".progresso[hidden]{display:none}" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_de_imagem_ensina_a_converter(client, inscricao_de_maria):
    """L5: a mensagem explicava a causa e não o caminho.

    Fotografar o documento é o que a maior parte das pessoas faz, e "converta em PDF" não ajuda
    quem nunca converteu. É o erro mais comum de candidato.
    """
    identificar(client, MARIA)

    corpo = _enviar(
        client, inscricao_de_maria, DOCUMENTO_DE_TODOS, imagem("foto.jpg")
    ).content.decode()

    assert "Converta a imagem em PDF" in corpo
    assert "Como transformar uma foto em PDF" in corpo
    assert "iPhone" in corpo and "Android" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_recusa_de_formato_nao_ensina_a_converter(client, inscricao_de_maria):
    """A instrução é da recusa que a exige — noutra recusa seria ruído."""
    identificar(client, MARIA)

    from django.core.files.uploadedfile import SimpleUploadedFile

    nao_e_pdf = SimpleUploadedFile("documento.pdf", b"texto qualquer", content_type="text/plain")
    corpo = _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, nao_e_pdf).content.decode()

    assert "não é um PDF" in corpo, "houve recusa"
    assert "Como transformar uma foto em PDF" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_requisito_enviado_recolhe_o_formulario_de_substituicao(client, inscricao_de_maria):
    """L6: aberto, cada requisito completo custava cerca de 850px de rolagem.

    Substituir é exceção; o estado normal de um requisito atendido é "está enviado". Mas quando a
    substituição é recusada, o formulário precisa estar à vista — senão a pessoa lê o motivo e não
    encontra onde tentar de novo.
    """
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    corpo = client.get(
        reverse("portal:inscricao", args=[inscricao_de_maria.id])
    ).content.decode()
    assert '<details class="envio-de-novo"' in corpo
    assert "Substituir ou remover" in corpo
    assert "<details class=\"envio-de-novo\" open>" not in corpo, "recolhido quando está tudo bem"

    recusado = _enviar(
        client, inscricao_de_maria, DOCUMENTO_DE_TODOS, imagem("foto.jpg")
    ).content.decode()
    assert "open" in recusado[recusado.index('class="envio-de-novo"') :][:60], (
        "aberto quando a substituição foi recusada"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_limite_exibido_e_o_limite_aplicado(client, inscricao_de_maria, settings):
    """A tela dizia "10 MB" enquanto o limite é configurável — mudá-lo faria a página mentir."""
    settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES = 5 * 1024 * 1024
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert "até 5 MB" in corpo
    assert "10 MB" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_campo_de_arquivo_do_navegador_nao_aparece_cru(client, inscricao_de_maria):
    """O `input[type=file]` é o elemento mais feio de qualquer formulário.

    Texto do sistema operacional, altura própria, "Nenhum arquivo selecionado" em cinza no meio da
    página. Ele continua existindo e continua sendo o que envia — sai de vista, mantendo foco e
    rótulo, e o `label` assume a aparência de botão.
    """
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert 'class="botao-arquivo"' in corpo
    assert "Escolher arquivo PDF" in corpo
    assert "data-nome-do-arquivo" in corpo, "o nome do escolhido tem onde aparecer"
    assert ".escolher input[type=file]{position:absolute" in corpo, "escondido, não removido"
    assert 'type="file"' in corpo and 'name="arquivo"' in corpo, "e continua sendo o que envia"
    assert "portal/arquivo.js" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_progresso_dos_documentos_e_barra_e_nao_segunda_frase(client, inscricao_de_maria):
    """O resumo do cabeçalho já diz em palavras quantos faltam.

    Repetir a mesma frase dentro do bloco era ruído; a barra diz o mesmo de relance, e o texto ao
    lado mantém o número para quem lê com leitor de tela.
    """
    identificar(client, MARIA)
    _enviar(client, inscricao_de_maria, DOCUMENTO_DE_TODOS, pdf("rg.pdf"))

    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()

    assert 'class="progresso-documentos' in corpo
    assert 'class="feito" style="width:50%"' in corpo, "metade da barra, sem modalidade escolhida"
    texto = " ".join(corpo.split())
    assert "1 de 2 documentos obrigatórios enviados." in texto
    assert texto.count("documentos obrigatórios enviados.") == 1, "uma contagem, não duas"
