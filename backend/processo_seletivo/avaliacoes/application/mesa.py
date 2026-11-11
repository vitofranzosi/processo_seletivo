"""A inscrição como **instrumento de trabalho** — e a porta que a abre.

A mecânica de arquivo é a da 009, inteira: entrega mediada, conferência de integridade antes do
primeiro byte, a cópia conferida sendo a servida, e o registro de cada consulta. O que **não** se
reutiliza é a permissão: `inscricao:consultar` pertence ao Gestor e alcança o Edital inteiro, e
entregá-la ao avaliador daria a ele o acervo — contradizendo FR-055 na primeira linha (D-005).

A autorização aqui é a composta, e ela é verificada no servidor a cada acesso:

```text
pode_atuar_na_etapa (011)  →  Atribuição ativa desta pessoa para esta inscrição  →  sim
```

**O que a tela mostra** é o necessário ao trabalho, e nada além (FR-030): protocolo, nome, Perfil,
Modalidade, CPF mascarado e os documentos sob o requisito que cada um atende. Fora ficam e-mail e
telefone, que não decidem avaliação nenhuma. O nome **fica**: avaliação cega está fora do escopo, e
esconder metade da identidade produziria a meia anonimização que é pior que nenhuma.
"""

from decimal import Decimal

from django.utils.dateparse import parse_datetime

from processo_seletivo.avaliacoes.domain import barema
from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.avaliacoes.domain.previsao import decisoria, pontuacao_maxima, rotulos
from processo_seletivo.editais.domain.documentos import (
    OBRIGATORIO,
    modelo_do_requisito,
    razao_legivel,
)
from processo_seletivo.inscricoes.application.lista_exigida import lista_exigida
from processo_seletivo.inscricoes.application.rascunho import nome_da_modalidade
from processo_seletivo.inscricoes.domain.pessoais import mascarar_cpf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.arquivos import tamanho_legivel

CONSULTAR_DOCUMENTO = "CONSULTAR_DOCUMENTO"
INTEGRIDADE = "INTEGRIDADE"
# A base que a trilha registra. Não é permissão nomeada: o que autoriza aqui é a conjunção da
# alocação com a Atribuição, e chamá-la pelo nome é o que faz a trilha dizer **por que** o acesso
# foi concedido, como a 011 fez com a presidência (FR-051).
BASE_DA_MESA = "avaliacao:atribuida"


def motivo_da_abertura(requirement_id):
    """O motivo que a trilha guarda de cada abertura: **qual requisito** foi aberto.

    O formato é escrito aqui e lido aqui, num lugar só, porque a tela passou a responder "quais
    documentos desta inscrição eu já abri" a partir dele — e um formato combinado de longe entre
    quem escreve e quem lê quebra em silêncio na primeira mudança de texto.

    A trilha continua sem o nome do arquivo, que é do candidato (FR-054): o requisito basta para
    saber o que foi aberto.
    """
    return f"requisito {requirement_id}"


def nomes_dos_requisitos(edital_id):
    """Identificador do requisito → nome, do mesmo conteúdo que a Mesa usa para listar documentos.

    A trilha atravessa muitas inscrições e não tem a versão aceita de cada uma; a seleção pública
    é a base compartilhada, e é a que a Mesa já consulta quando a inscrição não traz a sua.
    """
    versao = selectors.selecao_publica(edital_id=edital_id)
    conteudo = getattr(versao, "content", None) or {}
    return {
        str(requisito.get("id")): requisito.get("name")
        for requisito in (conteudo.get("documentRequirements") or [])
        if requisito.get("id")
    }


def motivo_legivel(motivo, nomes_dos_requisitos):
    """O mesmo motivo, dito para gente.

    A trilha guarda o identificador do requisito, e é ele que precisa estar gravado: nome muda por
    Retificação, identificador não. Mas na tela o identificador não responde a pergunta que se faz
    olhando um histórico — **qual documento foi aberto** —, e trinta e seis caracteres de UUID por
    linha empurram para fora o que se lê.

    O nome vem do conteúdo publicado, no momento de exibir. Continua sem o nome do arquivo, que é
    do candidato (FR-054): o requisito é a Etapa dizendo o que exigiu, não a pessoa dizendo o que
    enviou. Sem correspondência — requisito removido por Retificação —, fica o identificador, que
    é sempre verdadeiro.
    """
    requisito = requisito_do_motivo(motivo)
    if requisito is None:
        return motivo
    nome = (nomes_dos_requisitos or {}).get(str(requisito))
    # Sem aspas próprias: a trilha já cita o motivo inteiro, e aspas dentro de aspas é o que
    # produz o `""` no fim da linha.
    return f"requisito {nome}" if nome else motivo


def requisito_do_motivo(motivo):
    """O caminho de volta: de que requisito fala este motivo, ou `None`."""
    prefixo = "requisito "
    texto = (motivo or "").strip()
    return texto[len(prefixo) :] if texto.startswith(prefixo) else None


def _nao_encontrado():
    """A mesma resposta para tudo que o avaliador não alcança (FR-044)."""
    return DomainError("not_found", "Recurso não encontrado.", 404)


def _autorizar(ator, edital, etapa_id, inscricao_id):
    atribuicao = pode_avaliar_inscricao(ator, edital, etapa_id, inscricao_id)
    if atribuicao is None:
        # Inscrição de outro avaliador, alocação removida, escopo divergente ou inscrição que não
        # existe: uma resposta só. Trocar o identificador na URL não alcança nada (FR-045).
        raise _nao_encontrado()
    return atribuicao


def inscricao_para_avaliar(*, ator, edital, etapa_id, inscricao_id):
    """O que o candidato enviou, sob o Documento Exigido que cada arquivo atende (FR-025)."""
    atribuicao = _autorizar(ator, edital, etapa_id, inscricao_id)
    inscricao = Inscricao.objects.select_related("versao_aceita").filter(pk=inscricao_id).first()
    if inscricao is None:
        raise _nao_encontrado()
    # **A versão que a inscrição aceitou**, e não a vigente: usar a vigente faria Perfil,
    # Modalidade e a lista de requisitos mudarem retroativamente a cada Retificação, na tela de
    # quem avalia. É a mesma escolha que a consulta administrativa da 009 já faz.
    versao = inscricao.versao_aceita or selectors.selecao_publica(edital_id=inscricao.edital_id)
    conteudo = versao.content
    enviados = {
        str(documento.requirement_id): documento
        for documento in DocumentoSubmetido.objects.filter(inscricao=inscricao)
    }
    # **A lista gravada no envio**, e não o recorte refeito agora (044, FR-718). No 903/2026 a Mesa
    # recalculava, e herdou o erro do portal: o laudo que ele dispensou sumiu também daqui, e o
    # analista indeferiu por um documento que o sistema nunca pediu. Inscrição enviada antes da
    # `044` não tem lista gravada, e a lista é reconstruída — e a tela diz que foi (FR-726).
    lista = lista_exigida(inscricao, conteudo)
    documentos = [
        {
            "id": str(veredito.requisito["id"]),
            "nome": veredito.requisito.get("name", ""),
            # A instrução que o candidato leu ao enviar — "Apenas para quem concorre na
            # modalidade PcD." Sem ela, a autodeclaração ausente de quem concorre em ampla e a de
            # quem concorre em PcD se liam iguais na Mesa, e quem avalia não tinha como saber qual
            # das duas faltava de fato (conferência de 25/09/2026).
            "instrucoes": (veredito.requisito.get("instructions") or "").strip(),
            "obrigatorio": veredito.situacao == OBRIGATORIO,
            # A quem o documento foi pedido, em frase (UX-081): é o que dá a quem analisa o que
            # antes só se sabia conhecendo o Edital de cor.
            "razao": razao_legivel(veredito, conteudo),
            "enviado": enviados.get(str(veredito.requisito["id"])),
            "tamanho": (
                None
                if enviados.get(str(veredito.requisito["id"])) is None
                else tamanho_legivel(enviados[str(veredito.requisito["id"])].tamanho)
            ),
            # O modelo que estava valendo **sob a versão que a inscrição aceitou** (020, FR-048,
            # FR-050). Não é o vigente: uma Retificação pode ter substituído o formulário depois,
            # e mostrar o novo faria a banca conferir o que voltou contra uma forma que não era a
            # pedida.
            #
            # O que o sistema **não** afirma, e a tela não pode sugerir: que foi este o arquivo
            # que o candidato baixou. Ele pode ter baixado sob outra versão, e os bytes devolvidos
            # não dizem de onde vieram. Conformidade é juízo de quem avalia (D-004, FR-049).
            "modelo": modelo_do_requisito(conteudo, veredito.requisito),
        }
        # A lista é a dos **requisitos**, e não a dos arquivos: requisito sem arquivo aparece como
        # requisito sem arquivo, que é informação para quem avalia — e não uma linha que some.
        for veredito in lista.pedidos
    ]
    # O que não se aplicava, com a razão (FR-717, UX-082). Antes, sumia — e com ele o que o
    # portal dispensou por erro. Agora é estado com nome, abaixo do que foi pedido.
    nao_se_aplicam = [
        {
            "id": str(veredito.requisito["id"]),
            "nome": veredito.requisito.get("name", ""),
            "razao": razao_legivel(veredito, conteudo),
            "divergente": veredito.divergente_do_publicado,
        }
        for veredito in lista.nao_se_aplicam
    ]
    perfil, modalidade = _perfil_e_modalidade(conteudo, inscricao)
    # A regra que vale **agora**, e a que a Avaliação vai gravar. A versão da inscrição governa o
    # que o candidato enviou; a versão **vigente** governa a avaliação, e são coisas diferentes:
    # uma Retificação pode ter mudado a pontuação máxima depois da inscrição (FR-071, FR-096).
    vigente = effective_version(edital_id=edital.id)
    # A Etapa sai da **mesma** versão que a tela declara ao avaliador, pela razão de FR-096: o
    # `versao_reconhecida` que o formulário envia precisa corresponder à regra que ele leu.
    etapa = next(
        (
            item
            for item in vigente.content.get("stages") or []
            if str(item.get("id")) == str(etapa_id)
        ),
        None,
    )
    avaliacao = getattr(atribuicao, "avaliacao", None)
    return {
        # A ficha do barema, só na Etapa que o publicou (146, FR-5214): o rascunho pela versão
        # vigente, reconciliado; a concluída pela versão que ela cita (D-011).
        "ficha": ficha_da_avaliacao(avaliacao, etapa, etapa_id, documentos, vigente.content),
        "atribuicao": atribuicao,
        "avaliacao": avaliacao,
        "etapa": etapa,
        "versao_vigente": vigente,
        "maxima": pontuacao_maxima(etapa),
        "minima": (etapa or {}).get("minimumScore"),
        "eliminatoria": bool((etapa or {}).get("eliminatory")),
        # O instrumento que a Mesa apresenta vem da forma **publicada**, e não de preferência de
        # tela (FR-122). Os rótulos vêm junto porque é com eles que o avaliador lê as opções — o
        # domínio guarda o sentido, e a tela mostra o vocabulário deste Edital (FR-118).
        "decisoria": decisoria(etapa),
        "rotulo_favoravel": rotulos(etapa)[0],
        "rotulo_desfavoravel": rotulos(etapa)[1],
        "fora_do_periodo": _fora_do_periodo(edital, etapa),
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        "cpf": mascarar_cpf(inscricao.cpf),
        "versao": versao,
        "documentos": documentos,
        "nao_se_aplicam": nao_se_aplicam,
        "lista_reconstruida": lista.reconstruida,
    }


def ficha_da_avaliacao(avaliacao, etapa_vigente, etapa_id, documentos, conteudo_vigente):
    """A ficha que a Mesa mostra, ou `None` quando a Etapa não tem barema.

    **Concluída, pela versão que ela cita** (D-011, FR-5233): uma Retificação posterior que
    renomeie um critério não muda o que a conclusão afirmou. **Rascunho, pela vigente** — é o que a
    avaliadora vai concluir, e a conclusão recusa versão mudada —, com o detalhamento reconciliado:
    o valor do critério que continua fica para reconfirmação, o do removido sai e o novo fica
    pendente (FR-5222).
    """
    if avaliacao is not None and avaliacao.estado == "CONCLUIDA" and avaliacao.versao_id:
        criterios = barema.barema_da_versao(avaliacao.versao, etapa_id)
        if not criterios:
            return None
        return ficha_do_barema(
            criterios,
            avaliacao.criterios,
            documentos,
            avaliacao.versao.content,
            total=avaliacao.pontuacao,
            concluida=True,
        )
    criterios = barema.criterios_da_etapa(etapa_vigente)
    if not criterios:
        return None
    anterior = avaliacao.criterios if avaliacao is not None else []
    return ficha_do_barema(
        criterios, barema.reconciliar(anterior, criterios), documentos, conteudo_vigente
    )


def ficha_do_barema(
    criterios,
    detalhamento,
    documentos,
    conteudo,
    *,
    total=None,
    concluida=False,
    titulo="Barema",
    chave="do-barema",
    na_mesa=True,
):
    """As linhas da ficha, com a comprovação resolvida — o que o template desenha (UX-422).

    `documentos` é a lista que a Mesa já mostra; o critério ligado a um deles ganha o "Abrir" do
    mesmo painel. O documento que a inscrição não apresentou aparece como "não apresentado", e zero
    é a resposta esperada. A parcela de cada linha do rascunho é refeita sem recusar: o valor que a
    máxima nova não admite precisa aparecer para ser corrigido, e quem recusa é a gravação.

    É o mesmo componente na tela de julgamento de recurso (146, FR-5227), com `na_mesa=False`: lá o
    "Abrir" da Mesa não vale — ele passa pela Atribuição de quem avalia —, e a comprovação é só o
    nome do documento. `titulo` e `chave` distinguem duas fichas na mesma página.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import pontuacao_do_criterio

    por_requisito = {str(item["id"]): item for item in documentos or []}
    nomes = {
        str(item.get("id")): item.get("name", "")
        for item in (conteudo or {}).get("documentRequirements") or []
        if isinstance(item, dict)
    }
    afirmado = {
        str(linha.get("criterionId")): linha
        for linha in detalhamento or []
        if isinstance(linha, dict)
    }
    linhas, soma, respondidos = [], Decimal("0"), 0
    for criterio in criterios:
        chave = str(criterio["id"])
        linha = afirmado.get(chave) or {}
        if concluida:
            parcela, limitada = linha.get("parcela"), bool(linha.get("limitada"))
        else:
            parcela, limitada = barema.parcela_exibivel(criterio, linha)
        if parcela is not None:
            respondidos += 1
            soma += Decimal(str(parcela))
        requisito = criterio.get("documentRequirementId")
        documento = None
        if requisito:
            listado = por_requisito.get(str(requisito))
            documento = {
                "id": str(requisito),
                "nome": (listado or {}).get("nome") or nomes.get(str(requisito), ""),
                "enviado": bool(listado and listado.get("enviado")),
                "tamanho": (listado or {}).get("tamanho"),
            }
        linhas.append(
            {
                "id": chave,
                "nome": criterio.get("name", ""),
                "descricao": (criterio.get("description") or "").strip(),
                "maxima": criterio.get("maximumScore"),
                "pontos_por_unidade": criterio.get("pointsPerUnit"),
                "por_unidade": barema.por_unidade(criterio),
                "unidade": (criterio.get("unitLabel") or "").strip(),
                "frase": pontuacao_do_criterio(criterio),
                "quantidade": _no_campo(linha.get("quantidade")),
                "pontos": _no_campo(linha.get("pontos")),
                "justificativa": linha.get("justificativa") or "",
                "parcela": None if parcela is None else Decimal(str(parcela)),
                "limitada": limitada,
                "pendente": parcela is None,
                "documento": documento,
            }
        )
    if total is None and respondidos:
        total = soma
    return {
        "linhas": linhas,
        "total": total,
        "maxima": sum((Decimal(str(c.get("maximumScore") or 0)) for c in criterios), Decimal("0")),
        "pendentes": [linha["nome"] for linha in linhas if linha["pendente"]],
        "concluida": concluida,
        "titulo": titulo,
        "chave": chave,
        "na_mesa": na_mesa,
    }


def _no_campo(valor):
    """O valor como o campo numérico o aceita: `"12.5000"` → `"12.5"`; `None` → `""`."""
    if valor is None or valor == "":
        return ""
    texto = str(valor)
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto


def _fora_do_periodo(edital, etapa):
    """Se **agora** está fora do período previsto da Etapa (FR-077, FR-095).

    O período é **informado, e não aplicado**: a Etapa pode não referenciar Evento algum, o Edital
    publica datas previstas e não a proibição de trabalhar fora delas, e o efeito de avaliar
    atrasado é administrativo. O que não pode é o sistema conhecer a divergência e escondê-la de
    quem responde por ela.
    """
    from django.utils import timezone

    from processo_seletivo.comissoes.domain.etapas import evento_vigente

    if not etapa:
        return False
    try:
        evento = evento_vigente(edital, etapa.get("scheduleEventId"))
    except DomainError:
        return False
    if not evento:
        return False
    agora = timezone.now()
    inicio = parse_datetime(evento["startAt"]) if evento.get("startAt") else None
    fim = parse_datetime(evento["endAt"]) if evento.get("endAt") else None
    return bool((inicio and agora < inicio) or (fim and agora > fim))


def _perfil_e_modalidade(conteudo, inscricao):
    perfil = next(
        (
            item
            for item in conteudo.get("profiles") or []
            if str(item.get("id")) == str(inscricao.profile_id)
        ),
        {},
    )
    # O nulo tem nome onde é a ampla sem Modalidade, como no comprovante do candidato (A-14.3;
    # FR-068 da 009): em branco, o avaliador não sabia se a pessoa concorria na ampla ou se faltava
    # dado.
    return perfil.get("name", ""), nome_da_modalidade(
        conteudo, inscricao.profile_id, inscricao.modality_id
    )


def documento_para_avaliar(*, ator, edital, etapa_id, inscricao_id, requirement_id):
    """O documento, sob a Atribuição que autoriza abri-lo.

    Devolve `(documento, atribuicao)`. A conferência de integridade e a entrega ficam na view,
    porque é lá que a cópia conferida vira resposta — e conferir aqui, servindo lá, reabriria a
    janela que a 009 fechou de propósito.
    """
    atribuicao = _autorizar(ator, edital, etapa_id, inscricao_id)
    documento = DocumentoSubmetido.objects.filter(
        inscricao_id=inscricao_id, requirement_id=requirement_id
    ).first()
    if documento is None:
        raise _nao_encontrado()
    return documento, atribuicao
