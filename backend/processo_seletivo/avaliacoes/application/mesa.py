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

from django.utils.dateparse import parse_datetime

from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.avaliacoes.domain.previsao import pontuacao_maxima
from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao
from processo_seletivo.inscricoes.domain.arquivos import tamanho_legivel
from processo_seletivo.inscricoes.domain.pessoais import mascarar_cpf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError

CONSULTAR_DOCUMENTO = "CONSULTAR_DOCUMENTO"
INTEGRIDADE = "INTEGRIDADE"
# A base que a trilha registra. Não é permissão nomeada: o que autoriza aqui é a conjunção da
# alocação com a Atribuição, e chamá-la pelo nome é o que faz a trilha dizer **por que** o acesso
# foi concedido, como a 011 fez com a presidência (FR-051).
BASE_DA_MESA = "avaliacao:atribuida"


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
    documentos = [
        {
            "id": str(requisito["id"]),
            "nome": requisito.get("name", ""),
            "obrigatorio": requisito.get("required", True),
            "enviado": enviados.get(str(requisito["id"])),
            "tamanho": (
                None
                if enviados.get(str(requisito["id"])) is None
                else tamanho_legivel(enviados[str(requisito["id"])].tamanho)
            ),
        }
        # A lista é a dos **requisitos**, e não a dos arquivos: requisito sem arquivo aparece como
        # requisito sem arquivo, que é informação para quem avalia — e não uma linha que some.
        for requisito in requisitos_da_inscricao(conteudo, inscricao)
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
        "atribuicao": atribuicao,
        "avaliacao": avaliacao,
        "etapa": etapa,
        "versao_vigente": vigente,
        "maxima": pontuacao_maxima(etapa),
        "minima": (etapa or {}).get("minimumScore"),
        "eliminatoria": bool((etapa or {}).get("eliminatory")),
        "fora_do_periodo": _fora_do_periodo(edital, etapa),
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        "cpf": mascarar_cpf(inscricao.cpf),
        "versao": versao,
        "documentos": documentos,
    }


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
    modalidade = next(
        (
            item.get("name", "")
            for item in perfil.get("competitionModalities") or []
            if str(item.get("id")) == str(inscricao.modality_id)
        ),
        "",
    )
    return perfil.get("name", ""), modalidade


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
