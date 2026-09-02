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

from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.inscricoes.application.rascunho import requisitos_da_inscricao
from processo_seletivo.inscricoes.domain.arquivos import tamanho_legivel
from processo_seletivo.inscricoes.domain.pessoais import mascarar_cpf
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.publicacoes.application import selectors
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
    return {
        "atribuicao": atribuicao,
        "inscricao": inscricao,
        "perfil": perfil,
        "modalidade": modalidade,
        "cpf": mascarar_cpf(inscricao.cpf),
        "versao": versao,
        "documentos": documentos,
    }


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
