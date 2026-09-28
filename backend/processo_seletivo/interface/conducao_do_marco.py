"""Operar o resultado por marco, e não por recorte (049).

Três perguntas, e as três sobre **um** marco — o marco como o Edital o publica, dentro do Perfil
(`D-001`):

- **o indicador**: em que estado está cada recorte, em cada uma das quatro operações;
- **o alcance**: sobre quais recortes um gesto vai praticar o ato, e por que os outros ficam fora;
- **o gesto**: praticar, recorte a recorte, o ato que a tela do recorte praticaria.

**Por que mora em `interface/`** (`R-2`). O gesto atravessa três apps — `classificacao` (ordem e
corte), `ocupacao` (apuração) e `divulgacao` (publicação) —, e a dependência entre eles tem sentido
único, verificado por teste: a ocupação não importa a emissão da ordem, e a classificação não lê a
apuração. Pôr o laço em qualquer um deles obrigaria a importar o que a fronteira proíbe. A camada
que já lê os três é esta, onde vivem a Supervisão e o conjunto de ações.

**Este módulo não decide nada de domínio.** Ele pergunta ao domínio, mostra, e chama o comando de
hoje (`FR-820`, `R-1`). Não há caminho de gravação aqui: cada ato nasce de `emitir_ordem`,
`emitir_corte`, `emitir_apuracao` ou `publicar_resultado`, com as validações, a autoria e a trilha
deles. O que o gesto acrescenta é **quantas vezes a pessoa confirma**, e o que ela lê antes e
depois.

**Os recortes vêm da derivação única** (`editais/domain/recortes.py`, `FR-812`), e nunca de uma
segunda lista: o recorte excedente que o sorteio dá à Modalidade declarada como ampla (`FR-491a`)
não entra aqui, pela mesma razão que não entra na ocupação.
"""

from django.db import transaction
from django.urls import reverse

from processo_seletivo.auditoria.models import IdempotencyRecord
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import (
    calcular_corte,
    estado_do_corte,
    geracao_vigente,
    linha_do_quadro,
)
from processo_seletivo.classificacao.application.emissao import (
    ATO as ATO_DE_CLASSIFICAR,
)
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import AtoDeOrdenacao, Corte
from processo_seletivo.divulgacao.application.publicar import (
    assinatura_da_previa,
    publicar_resultado,
)
from processo_seletivo.divulgacao.application.selectors import (
    divulgacao_do_ato,
    historico_do_marco,
    vigente_do_marco,
)
from processo_seletivo.divulgacao.domain.conteudo import compor as compor_divulgacao
from processo_seletivo.divulgacao.domain.publicabilidade import AVISO, natureza_regride
from processo_seletivo.divulgacao.domain.publicabilidade import aferir as aferir_publicabilidade
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado
from processo_seletivo.editais.domain import marcos
from processo_seletivo.editais.domain.recortes import recortes_do_perfil
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.application.selectors import (
    apuracao_vigente,
    causas_de_obsolescencia,
)
from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.autoridades import escolher
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.canonical import canonical_sha256

ORDENAR, CORTAR, APURAR, PUBLICAR = "ordenar", "cortar", "apurar", "publicar"
OPERACOES = (ORDENAR, CORTAR, APURAR, PUBLICAR)
#: As três que pedem a gestão da comissão. A quarta pede `resultado:publicar`, e as duas portas não
#: se fundem aqui (`R-7`): quem emite o ato não ganha, por tê-lo emitido, o poder de divulgá-lo.
DA_GESTAO = (ORDENAR, CORTAR, APURAR)

FEITO, OBSOLETO, FALTA, NAO_SE_APLICA = "feito", "obsoleto", "falta", "nao_se_aplica"
PRATICAR, FORA, IMPEDIDO = "praticar", "fora", "impedido"

#: O token da ampla no formulário. A ampla é o recorte **sem** lista, e um campo vazio num
#: formulário é ambíguo: seria lido tanto como "a ampla" quanto como "o campo não veio".
AMPLA = "ampla"

#: O que o botão da confirmação diz, por operação (`UX-092`): o verbo e a quantidade, e não
#: "Confirmar". Quem confirma precisa ler o que o clique pratica.
VERBOS = {
    ORDENAR: ("Emitir {n} ordem", "Emitir {n} ordens"),
    CORTAR: ("Emitir {n} corte", "Emitir {n} cortes"),
    APURAR: ("Apurar {n} recorte", "Apurar {n} recortes"),
    PUBLICAR: ("Publicar {n} resultado", "Publicar {n} resultados"),
}
NOMES = {
    ORDENAR: "Ordenar o marco",
    CORTAR: "Cortar o marco",
    APURAR: "Apurar a ocupação do marco",
    PUBLICAR: "Publicar o resultado do marco",
}

JA_TEM_ORDEM = (
    "Já tem ordem vigente. Suceder uma ordem exige motivo e se faz na tela do recorte, um de cada "
    "vez."
)
JA_TEM_CORTE = (
    "Já tem faixa vigente. A sucessão e a faixa seguinte pedem motivo e quantidade próprios, e se "
    "fazem na tela do recorte."
)
JA_TEM_APURACAO = (
    "Já tem apuração vigente. Suceder uma apuração exige motivo e se faz na tela da ocupação."
)
SEM_ORDEM = "Este recorte não tem ordem vigente: emita a ordem dele antes."
MUDOU_DESDE_A_CONFERENCIA = "O recorte mudou desde a conferência; confira de novo antes de apurar."


def marco_publicado(edital, marco_id):
    """`(conteudo, perfil, marco)` pela versão vigente, ou `(conteudo, None, None)`.

    **A norma vigente, e não a histórica** (`FR-813`): o marco que uma Retificação removeu não tem
    recortes a operar, e os atos dele continuam alcançáveis pelas telas de histórico de hoje.

    **Uma varredura só**: `views._marco_publicado` delega a esta, e as telas de recorte e a do
    marco respondem "que marco é este" pelo mesmo caminho. Edital sem versão publicada recusa com a
    recusa de `effective_version`, como sempre recusou — quem quer 404 a traduz.
    """
    conteudo = effective_version(edital_id=edital.id).content
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == alvo:
                return conteudo, perfil, marco
    return conteudo, None, None


def recortes_do_marco(conteudo, perfil):
    """`[(lista_id, rótulo)]` — a derivação única, e a mesma ordem dela (`FR-812`)."""
    return recortes_do_perfil(conteudo, perfil_id=perfil["id"])


def sorteia(conteudo, perfil, marco):
    """Se a ordem deste marco nasce do sorteio público — pela resolução, e não pela chave."""
    return marcos.marco_ordena_por_sorteio(conteudo, perfil_id=perfil["id"], marco_id=marco["id"])


def corta(marco):
    return bool((marco or {}).get("cutRule"))


def lista_para_o_formulario(lista_id):
    return str(lista_id) if lista_id else AMPLA


# ---------------------------------------------------------------------------------------------
# O indicador (`FR-810` a `FR-815`)
# ---------------------------------------------------------------------------------------------


def indicador_do_marco(edital, conteudo, perfil, marco, *, pode_classificar, pode_publicar):
    """Uma linha por recorte, uma célula por operação, com o estado completo (`UX-091`, `R-6`).

    **Completo quer dizer com obsolescência.** A página do Edital diz só se há ato; aqui se
    pergunta o que as telas de recorte perguntam — `estado_do_marco`, `estado_do_corte`,
    `causas_de_obsolescencia` e `divulgacao_do_ato` —, porque *feito* ao lado de um ato que o
    sistema já sabe estar para trás seria a tela mentindo. O custo é de um marco, que tem no
    máximo as listas que o Perfil declara.

    **Cada célula leva à tela do recorte e da operação**, e só se quem olha a abre: oferecer o que
    se vai recusar é o beco que a `033` fechou. Sem caminho, a célula continua dizendo o estado.
    """
    marco_id = str(marco["id"])
    perfil_id = perfil["id"]
    do_sorteio = sorteia(conteudo, perfil, marco)
    versao = effective_version(edital_id=edital.id)
    com_corte = corta(marco)
    # A cadeia de publicações é do marco, e não do recorte: uma leitura para todas as listas.
    historico = historico_do_marco(edital=edital, marco_id=marco_id)
    linhas = []
    for lista_id, rotulo in recortes_do_marco(conteudo, perfil):
        ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
        linhas.append(
            {
                "lista_id": lista_id,
                "rotulo": rotulo,
                "celulas": {
                    ORDENAR: _celula_da_ordem(
                        edital, marco, lista_id, ato, versao, do_sorteio, pode_classificar
                    ),
                    CORTAR: _celula_do_corte(
                        edital, perfil_id, marco_id, lista_id, com_corte, pode_classificar
                    ),
                    APURAR: _celula_da_apuracao(
                        edital, conteudo, perfil_id, marco_id, lista_id, pode_classificar
                    ),
                    PUBLICAR: _celula_da_publicacao(
                        edital, marco_id, lista_id, ato, historico, pode_publicar
                    ),
                },
            }
        )
    return {"linhas": linhas, "totais": _totais(linhas)}


def _totais(linhas):
    """Por operação: quantos feitos, de quantos se aplicam.

    **Só *feito* conta** (`FR-814`): contar o obsoleto faria o marco parecer pronto com uma ordem
    que o sistema já sabe estar para trás.
    """
    totais = {}
    for operacao in OPERACOES:
        estados = [linha["celulas"][operacao]["estado"] for linha in linhas]
        aplicaveis = [estado for estado in estados if estado != NAO_SE_APLICA]
        totais[operacao] = {
            "feitos": sum(1 for estado in aplicaveis if estado == FEITO),
            "aplicaveis": len(aplicaveis),
            "se_aplica": bool(aplicaveis),
        }
    return totais


def _com_lista(endereco, lista_id):
    return f"{endereco}?lista={lista_id}" if lista_id else endereco


def _celula_da_ordem(edital, marco, lista_id, ato, versao, do_sorteio, pode_classificar):
    marco_id = str(marco["id"])
    # **O marco de sorteio leva à tela do sorteio** (`FR-815`): lá a ordem se refaz com relação e
    # ocorrência novas, e a tela da ordenação ofereceria recalcular o que só uma semente produz.
    rota = "interface:sorteio" if do_sorteio else "interface:ordenacao"
    url = _com_lista(reverse(rota, args=[edital.id, marco_id]), lista_id)
    if ato is None:
        return {"estado": FALTA, "nota": "", "url": url if pode_classificar else ""}
    nota = ""
    # **Ninguém concorreu é nota, e não estado** (`D-003`): a ordem vazia está feita, e dizê-la
    # como pendência mandaria emitir de novo o que já existe.
    if not ato.posicoes.exists():
        nota = "ninguém concorreu"
    return {
        "estado": OBSOLETO if _ordem_obsoleta(edital, marco, lista_id, ato, versao) else FEITO,
        "nota": nota,
        "url": url if pode_classificar else "",
    }


def _ordem_obsoleta(edital, marco, lista_id, ato, versao):
    """A obsolescência da ordem, pelas duas passagens da Supervisão (`UX-004`, `T-003`).

    `estado_do_marco` recalcula a ordem inteira, e a tela do marco é reaberta a cada gesto. O
    filtro barato — versão citada diferente da vigente, ou Resultado mais novo que o ato — é o que
    a Supervisão já usa, e é conservador por construção: admite candidato que a confirmação
    descarta, e nunca o contrário. Só o candidato paga o recálculo.
    """
    from processo_seletivo.interface.supervisao import candidato_a_obsoleto

    if not candidato_a_obsoleto(edital, ato, marco, versao):
        return False
    try:
        return estado_do_marco(edital=edital, marco_id=str(marco["id"]), lista_id=lista_id)[
            "obsoleto"
        ]
    except DomainError:
        return False


def _celula_do_corte(edital, perfil_id, marco_id, lista_id, com_corte, pode_classificar):
    if not com_corte:
        return {"estado": NAO_SE_APLICA, "nota": "o marco não corta", "url": ""}
    url = _com_lista(reverse("interface:corte", args=[edital.id, marco_id]), lista_id)
    estado = estado_do_corte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    if not estado["geracao"]:
        situacao = FALTA
    else:
        situacao = OBSOLETO if estado["obsoleto"] else FEITO
    return {"estado": situacao, "nota": "", "url": url if pode_classificar else ""}


def _celula_da_apuracao(edital, conteudo, perfil_id, marco_id, lista_id, pode_classificar):
    url = reverse("interface:ocupacao", args=[edital.id, marco_id]) if pode_classificar else ""
    vigente = apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    if (
        vigente is None
        and linha_do_quadro(conteudo, perfil_id=perfil_id, lista_id=lista_id) is None
    ):
        # **Sem linha no quadro não há quantidade a apurar, e isso não é falta** (`FR-811`). Contado
        # como falta, o recorte deixava a apuração do marco incompleta para sempre, e o gesto de
        # apurar continuava oferecido para sempre impedir. É o `NO_VACANCY_TABLE` da tela da
        # ocupação, que diz o caminho — a Retificação do Perfil —, e é para lá que a célula leva.
        return {"estado": NAO_SE_APLICA, "nota": "sem quadro de vagas publicado", "url": url}
    if vigente is None:
        situacao = FALTA
    else:
        situacao = OBSOLETO if causas_de_obsolescencia(vigente) else FEITO
    return {"estado": situacao, "nota": "", "url": url}


def _celula_da_publicacao(edital, marco_id, lista_id, ato, historico, pode_publicar):
    url = reverse("interface:publicacoes-do-marco", args=[edital.id, marco_id])
    if ato is None:
        # **Sem ordem não há o que publicar, e isso conta como falta** (`data-model.md`): o
        # recorte ainda não chegou à divulgação, e dizer "não se aplica" o tiraria da conta.
        return {"estado": FALTA, "nota": "falta a ordem", "url": ""}
    estado = divulgacao_do_ato(
        edital=edital, marco_id=marco_id, ato=ato, lista_id=lista_id, historico=historico
    )
    if estado["defasadas"]:
        # **Obsoleto, e com a frase do caso** (`FR-811`): o público lê um ato anterior, e isso se
        # resolve publicando o vigente — que é outra coisa que "falta".
        return {
            "estado": OBSOLETO,
            "nota": "o público lê um ato anterior",
            "url": url if pode_publicar else "",
        }
    if estado["nunca_divulgado"]:
        return {"estado": FALTA, "nota": "", "url": url if pode_publicar else ""}
    natureza = next(
        (
            linha["publicacao"].get_natureza_display()
            for linha in historico
            if linha["vigente"] and str(linha["publicacao"].ato_id) == str(ato.id)
        ),
        "",
    )
    return {"estado": FEITO, "nota": natureza.lower(), "url": url if pode_publicar else ""}


def resumo_dos_marcos(edital, conteudo):
    """Por marco: quantos recortes têm ato vigente em cada operação (`UX-090`, `R-6`, `SC-305`).

    **Presença, e não estado completo.** A página do Edital lista todos os marcos, e perguntar a
    obsolescência de cada recorte seria um recálculo por recorte a cada abertura — o erro que a
    `018` recusou ao não usar a verificação do ponto como varredura de listagem. O que envelhece
    continua sinalizado na Supervisão e aparece inteiro na tela do marco.

    **Quatro consultas para o Edital inteiro**, qualquer que seja o número de marcos e de recortes:
    uma por espécie de ato vigente. O cruzamento com os recortes é em memória.
    """
    atos = {
        (str(marco), str(lista) if lista else None): str(ident)
        for ident, marco, lista in AtoDeOrdenacao.objects.filter(
            edital=edital, sucessores__isnull=True
        ).values_list("id", "marco_id", "lista_id")
    }
    cortes = {
        (str(marco), str(lista) if lista else None)
        for marco, lista in Corte.objects.filter(
            edital=edital, raiz__isnull=True, sucessores__isnull=True
        ).values_list("marco_id", "lista_id")
    }
    apuracoes = {
        (str(marco), str(lista) if lista else None)
        for marco, lista in ApuracaoDeOcupacao.objects.filter(
            edital=edital, sucessoras__isnull=True
        ).values_list("marco_id", "lista_id")
    }
    publicadas = {
        (str(marco), str(lista) if lista else None, str(ato))
        for marco, lista, ato in PublicacaoResultado.objects.filter(
            edital=edital, sucessoras__isnull=True
        ).values_list("marco_id", "lista_id", "ato_id")
    }
    resumo = {}
    for perfil in (conteudo or {}).get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            marco_id = str(marco.get("id"))
            chaves = [
                (marco_id, str(lista) if lista else None)
                for lista, _ in recortes_do_perfil(conteudo, perfil_id=perfil.get("id"))
            ]
            resumo[marco_id] = {
                "recortes": len(chaves),
                "ordem": sum(1 for chave in chaves if chave in atos),
                "corte": sum(1 for chave in chaves if chave in cortes) if corta(marco) else None,
                "apuracao": sum(1 for chave in chaves if chave in apuracoes),
                "publicacao": sum(
                    1 for chave in chaves if chave in atos and (*chave, atos[chave]) in publicadas
                ),
            }
    return resumo


# ---------------------------------------------------------------------------------------------
# O alcance (`FR-816` a `FR-819`, `FR-826` a `FR-828`)
# ---------------------------------------------------------------------------------------------


def alcance(edital, conteudo, perfil, marco, operacao, *, natureza="", autoridade=""):
    """Um item por recorte do marco: `praticar`, `fora` ou `impedido`, com a razão (`FR-818`).

    **Nada é gravado aqui.** É a conferência: compõe, para cada recorte a praticar, a mesma
    assinatura que a tela do recorte compõe, e é ela que a confirmação devolve e o comando confere
    (`R-3`). O que mudou entre ler e confirmar é recusado lá, recorte a recorte.

    **O gesto pratica só o primeiro ato do recorte** (`D-002`, `FR-816`). Recorte que já tem o ato
    — obsoleto ou não — fica `fora`, e a sucessão continua na tela dele: ela exige motivo, e um
    motivo único para N sucessões diria a mesma razão para fatos diferentes.

    Recusa o gesto inteiro, com `DomainError`, só quando **o marco** não o admite: ordenar um marco
    de sorteio, cortar um marco sem regra, publicar sem natureza ou sem autoridade — ou quando o
    Processo, em estado final, não admite mais ato da comissão.
    """
    if operacao in DA_GESTAO:
        # **A recusa que vale para o marco inteiro é dita na conferência** (`FR-818`). Os três
        # comandos da comissão recusam o Processo em estado final, recorte a recorte; sem esta
        # pergunta, a conferência prometia "Emitir 3 ordens" e a confirmação devolvia três recusas
        # iguais. É a mesma função que `comando_de_comissao` chama, e não uma segunda regra.
        ensure_processo_accepts_changes(edital.processo)
    if operacao == ORDENAR:
        return _alcance_da_ordem(edital, conteudo, perfil, marco)
    if operacao == CORTAR:
        return _alcance_do_corte(edital, conteudo, perfil, marco)
    if operacao == APURAR:
        return _alcance_da_apuracao(edital, conteudo, perfil, marco)
    return _alcance_da_publicacao(edital, conteudo, perfil, marco, natureza, autoridade)


def _item(
    lista_id,
    rotulo,
    situacao,
    *,
    razao="",
    resumo="",
    assinatura="",
    com_declaracao=False,
):
    return {
        "com_declaracao": com_declaracao,
        "lista_id": lista_id,
        "campo": lista_para_o_formulario(lista_id),
        "rotulo": rotulo,
        "situacao": situacao,
        "razao": razao,
        "resumo": resumo,
        "assinatura": assinatura,
    }


def _alcance_da_ordem(edital, conteudo, perfil, marco):
    marco_id = str(marco["id"])
    if sorteia(conteudo, perfil, marco):
        # A frase é a do domínio (`_recusar_marco_de_sorteio`): a ordem de um marco de sorteio nasce
        # do sorteio público, e emiti-la por cálculo era o dano irreversível que a `021` fechou.
        raise DomainError(
            "ordering_milestone_is_drawn",
            "Este marco tem o método de sorteio declarado no Edital: a ordem dele nasce do sorteio "
            "público, e não do cálculo por Etapas. Conduza o sorteio na tela do marco.",
            422,
        )
    itens = []
    for lista_id, rotulo in recortes_do_marco(conteudo, perfil):
        if ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id) is not None:
            itens.append(_item(lista_id, rotulo, FORA, razao=JA_TEM_ORDEM))
            continue
        try:
            proposta = calcular_ordem(
                edital=edital, perfil_id=perfil["id"], marco_id=marco_id, lista_id=lista_id
            )
        except DomainError as recusa:
            itens.append(_item(lista_id, rotulo, IMPEDIDO, razao=recusa.detail))
            continue
        com_posicao, sem_posicao = len(proposta["posicoes"]), len(proposta["sem_posicao"])
        vazio = not com_posicao and not sem_posicao
        itens.append(
            _item(
                lista_id,
                rotulo,
                PRATICAR,
                resumo=(
                    "ninguém concorreu — a ordem vazia é emitida e registra isso"
                    if vazio
                    else f"{com_posicao} com posição, {sem_posicao} sem posição"
                ),
                assinatura=assinatura_da_proposta(proposta, ato_vigente=None),
            )
        )
    return itens


def _alcance_do_corte(edital, conteudo, perfil, marco):
    marco_id = str(marco["id"])
    if not corta(marco):
        raise DomainError(
            "marco_sem_regra_de_corte",
            "Este marco não declara regra de corte: o Edital não publicou quantos progridem.",
            409,
        )
    itens = []
    for lista_id, rotulo in recortes_do_marco(conteudo, perfil):
        if geracao_vigente(
            edital=edital, perfil_id=perfil["id"], marco_id=marco_id, lista_id=lista_id
        ):
            itens.append(_item(lista_id, rotulo, FORA, razao=JA_TEM_CORTE))
            continue
        try:
            proposta = calcular_corte(
                edital=edital, perfil_id=perfil["id"], marco_id=marco_id, lista_id=lista_id
            )
        except DomainError as recusa:
            itens.append(_item(lista_id, rotulo, IMPEDIDO, razao=recusa.detail))
            continue
        itens.append(
            _item(
                lista_id,
                rotulo,
                PRATICAR,
                resumo=f"{proposta['progrediram']} na faixa, {proposta['fora']} fora dela",
                assinatura=assinatura_do_corte(proposta, geracao=[]),
            )
        )
    return itens


def assinatura_da_apuracao(edital, perfil_id, marco_id, lista_id):
    """O que a apuração vai ler — a única das quatro que não tinha assinatura (`R-4`).

    `emitir_apuracao` não recebe confirmação: apura o que houver. Sem esta assinatura, a apuração
    seria o único ato do gesto sem conferência, e é ela que a convocação consome. Mudar o comando
    mexeria numa porta da `016` que a tela de hoje usa sem conferência; a assinatura mora aqui, e é
    conferida sob a mesma trava do comando.

    Cobre o que a apuração lê: a ordem vigente, a geração vigente do corte, a apuração vigente e a
    versão normativa — é nesta que mora a linha do quadro.
    """
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    geracao = geracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    apuracao = apuracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    return canonical_sha256(
        {
            "recorte": str(lista_id) if lista_id else None,
            "ato": str(ato.id) if ato is not None else None,
            "geracao": [str(item.id) for item in geracao],
            "apuracao": str(apuracao.id) if apuracao is not None else None,
            "versao": str(effective_version(edital_id=edital.id).id),
        }
    )


def _alcance_da_apuracao(edital, conteudo, perfil, marco):
    marco_id = str(marco["id"])
    itens = []
    for lista_id, rotulo in recortes_do_marco(conteudo, perfil):
        if apuracao_vigente(
            edital=edital, perfil_id=perfil["id"], marco_id=marco_id, lista_id=lista_id
        ):
            itens.append(_item(lista_id, rotulo, FORA, razao=JA_TEM_APURACAO))
            continue
        if ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id) is None:
            itens.append(_item(lista_id, rotulo, IMPEDIDO, razao=SEM_ORDEM))
            continue
        linha = linha_do_quadro(conteudo, perfil_id=perfil["id"], lista_id=lista_id)
        if linha is None:
            # A frase é a que a apuração daria (`sem_quadro_publicado`): dita já na conferência,
            # e não depois do clique.
            itens.append(
                _item(
                    lista_id,
                    rotulo,
                    IMPEDIDO,
                    razao=(
                        "Este Edital não publicou quadro de vagas para este recorte: não há "
                        "quantidade declarada a apurar. A quantidade é declarada por Retificação "
                        "do Perfil."
                    ),
                )
            )
            continue
        itens.append(
            _item(
                lista_id,
                rotulo,
                PRATICAR,
                resumo=f"{linha.get('immediateVacancies') or 0} vaga(s) publicada(s) no quadro",
                assinatura=assinatura_da_apuracao(edital, perfil["id"], marco_id, lista_id),
            )
        )
    return itens


def conferir_natureza_e_autoridade(natureza, autoridade):
    """As duas escolhas que a publicação pede uma vez para o marco (`FR-826`)."""
    if natureza not in Natureza.values:
        raise DomainError(
            "publication_nature_required", "Escolha a natureza do resultado a divulgar.", 422
        )
    if escolher(autoridade) is None:
        raise DomainError(
            "publication_authority_required",
            "Escolha a autoridade signatária entre as do catálogo.",
            422,
        )


def exige_declaracao(ato, marco_id, natureza):
    """A declaração de encerramento do prazo: só na definitiva, e só onde **aquele ato** não tem
    janela computável.

    **Por ato, e não por marco** (RC-121, decisão de 28/09). A janela de um ato é a da versão que
    ele cita, salvo o que a vigente concede — e, num mesmo marco, o ato de um recorte pode citar
    uma versão e o de outro, outra. Perguntar ao marco daria uma resposta só para atos que podem
    discordar: a declaração iria a quem tem janela, e o comando a recusaria ali.

    A pergunta é a mesma que `publicar_resultado` faz, pela mesma função, lida pelo módulo para que
    as duas nunca divirjam.
    """
    from processo_seletivo.recursos.domain import janela as janela_recursal

    return natureza == Natureza.DEFINITIVA and janela_recursal.janela_do_ato(ato, marco_id) is None


def _alcance_da_publicacao(edital, conteudo, perfil, marco, natureza, autoridade):
    conferir_natureza_e_autoridade(natureza, autoridade)
    marco_id = str(marco["id"])
    itens = []
    for lista_id, rotulo in recortes_do_marco(conteudo, perfil):
        ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
        if ato is None:
            itens.append(_item(lista_id, rotulo, IMPEDIDO, razao=SEM_ORDEM))
            continue
        # **Já divulgado naquela natureza fica fora** (`FR-826`): é a publicação que o gesto
        # faria, e ela já existe. É também o que protege o recorte que o recurso não alcançou — os
        # outros recortes do marco não são republicados por ele.
        if PublicacaoResultado.objects.filter(ato=ato, natureza=natureza).exists():
            itens.append(
                _item(
                    lista_id,
                    rotulo,
                    FORA,
                    razao=f"O ato vigente já está divulgado como resultado {natureza.lower()}.",
                )
            )
            continue
        sucede = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
        if natureza_regride(sucede, natureza):
            itens.append(
                _item(
                    lista_id,
                    rotulo,
                    FORA,
                    razao=(
                        "Já tem resultado definitivo divulgado: um preliminar não sucede um "
                        "definitivo."
                    ),
                )
            )
            continue
        afericao = aferir_publicabilidade(
            edital=edital,
            marco_id=marco_id,
            ato=ato,
            sucede=sucede,
            natureza=natureza,
            lista_id=ato.lista_id,
        )
        if not afericao.publicavel:
            itens.append(_item(lista_id, rotulo, IMPEDIDO, razao=afericao.mensagem))
            continue
        projecao = compor_divulgacao(ato)
        posicoes = len(projecao["posicoes"])
        partes = [
            "ninguém concorreu — a lista vazia é divulgada"
            if not projecao["situacoes"]
            else f"{posicoes} posição(ões) divulgada(s)"
        ]
        if afericao.nivel == AVISO:
            partes.append("sucede a divulgação vigente deste recorte")
        com_declaracao = exige_declaracao(ato, marco_id, natureza)
        if com_declaracao:
            partes.append("leva a declaração de encerramento do prazo")
        itens.append(
            _item(
                lista_id,
                rotulo,
                PRATICAR,
                resumo="; ".join(partes),
                assinatura=assinatura_da_previa(
                    ato=ato, publicacao_anterior=sucede, projecao=projecao
                ),
                com_declaracao=com_declaracao,
            )
        )
    return itens


# ---------------------------------------------------------------------------------------------
# O gesto (`FR-820` a `FR-825`)
# ---------------------------------------------------------------------------------------------


def chave_do_recorte(chave, operacao, lista_id):
    """A chave de idempotência de um recorte, derivada da do gesto (`R-5`).

    Uma chave só para o gesto não serve: ordem, corte e apuração usam a mesma operação
    (`classificacao:emitir`) com payloads diferentes, e a chave comum daria conflito no segundo
    recorte. Derivada, a repetição do envio repete cada chave, e cada comando devolve o desfecho da
    primeira vez (`FR-822`).
    """
    return f"marco:{chave}:{operacao}:{lista_para_o_formulario(lista_id)}"


def correlacao_do_gesto(chave):
    """O que liga os N atos de um gesto na trilha (`FR-825`)."""
    return f"gesto-{chave}"


RECORTE_AUSENTE = (
    "Este recorte já não é do marco na norma vigente — uma Retificação o retirou depois da "
    "conferência. Nada foi praticado nele."
)


def recortes_ausentes(campos):
    """Os pedidos que a derivação de agora não conhece, como desfechos recusados (`FR-824`).

    Nada é praticado neles, e o gesto segue nos demais: a recusa de um não pode deixar os outros
    sem ato, que é a mesma promessa da `FR-823` vista pelo lado do formulário.
    """
    return [
        {
            "lista_id": campo,
            "rotulo": "Recorte retirado do marco",
            "feito": False,
            "razao": RECORTE_AUSENTE,
            "url": "",
        }
        for campo in campos
    ]


def praticar(
    *,
    ator,
    edital,
    perfil,
    marco,
    operacao,
    itens,
    chave,
    natureza="",
    autoridade="",
    declaracao="",
):
    """Pratica o ato em cada recorte confirmado, **cada um na sua transação** (`R-1`, `FR-823`).

    `itens` é `[(lista_id, rótulo, assinatura)]`, na ordem da derivação — só o que a conferência
    mostrou e o formulário devolveu (`SC-303`). Quem chama já conferiu que cada `lista_id` é
    recorte deste marco.

    **Uma recusa não interrompe as seguintes.** Cada comando abre a própria transação, e o projeto
    não usa `ATOMIC_REQUESTS`: o que um recorte grava já está confirmado quando o seguinte começa,
    e a recusa de um desfaz só a transação dele. Desfazer os outros seria trabalho perdido; calar
    sobre eles seria trabalho escondido — e a spec proíbe os dois.

    **Motivo vazio, sempre.** O gesto nunca sucede nada (`D-002`): a sucessão exige motivo, e os
    comandos a recusam sem ele. É a segunda trava, depois da assinatura, contra suceder em lote.
    """
    marco_id = str(marco["id"])
    correlacao = correlacao_do_gesto(chave)
    desfechos = []
    for lista_id, rotulo, assinatura in itens:
        chave_do_ato = chave_do_recorte(chave, operacao, lista_id)
        try:
            url = _DESPACHO[operacao](
                ator=ator,
                edital=edital,
                perfil=perfil,
                marco_id=marco_id,
                lista_id=lista_id,
                assinatura=assinatura,
                chave=chave_do_ato,
                correlacao=correlacao,
                natureza=natureza,
                autoridade=autoridade,
                declaracao=declaracao,
            )
        except DomainError as recusa:
            desfechos.append(
                {
                    "lista_id": lista_para_a_sessao(lista_id),
                    "rotulo": rotulo,
                    "feito": False,
                    "razao": recusa.detail,
                    "url": _tela_do_recorte(edital, marco_id, operacao, lista_id),
                }
            )
            continue
        desfechos.append(
            {
                "lista_id": lista_para_a_sessao(lista_id),
                "rotulo": rotulo,
                "feito": True,
                "razao": "",
                "url": url,
            }
        )
    return desfechos


def lista_para_a_sessao(lista_id):
    """O desfecho vai para a sessão, que só guarda o que o JSON serializa (`R-10`)."""
    return str(lista_id) if lista_id else None


def _tela_do_recorte(edital, marco_id, operacao, lista_id):
    rota = {
        ORDENAR: "interface:ordenacao",
        CORTAR: "interface:corte",
        APURAR: "interface:ocupacao",
        PUBLICAR: "interface:publicacoes-do-marco",
    }[operacao]
    endereco = reverse(rota, args=[edital.id, marco_id])
    return _com_lista(endereco, lista_id) if operacao in (ORDENAR, CORTAR) else endereco


def _ordenar(*, ator, edital, perfil, marco_id, lista_id, assinatura, chave, correlacao, **_):
    emitir_ordem(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=perfil["id"],
        marco_id=marco_id,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id=correlacao,
        confirmacao_do_calculo=assinatura,
        motivo="",
    )
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        return _tela_do_recorte(edital, marco_id, ORDENAR, lista_id)
    return reverse("interface:ato-de-ordenacao", args=[edital.id, marco_id, ato.id])


def _cortar(*, ator, edital, perfil, marco_id, lista_id, assinatura, chave, correlacao, **_):
    emitir_corte(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=perfil["id"],
        marco_id=marco_id,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id=correlacao,
        confirmacao_do_calculo=assinatura,
        motivo="",
    )
    return _tela_do_recorte(edital, marco_id, CORTAR, lista_id)


def _apurar(*, ator, edital, perfil, marco_id, lista_id, assinatura, chave, correlacao, **_):
    """A apuração conferida **sob a trava do Processo**, antes do comando (`R-4`).

    A transação de fora toma a mesma linha que `comando_de_comissao` toma; o comando roda
    aninhado, num ponto de salvamento, e reencontra a trava que já é desta transação. Conferir
    fora da trava deixaria a ordem ser sucedida entre a conferência e a gravação.

    **A repetição do envio não é conferida de novo.** Depois da primeira apuração, a assinatura
    mudou — há apuração vigente —, e conferir recusaria a repetição em vez de devolver o desfecho
    da primeira (`FR-822`). A reserva concluída daquela chave diz que o ato já aconteceu, e o
    comando a devolve.
    """
    with transaction.atomic():
        ProcessoSeletivo.objects.select_for_update().filter(pk=edital.processo_id).first()
        repetido = IdempotencyRecord.objects.filter(
            institution_scope=ator.institution_scope,
            actor_subject=ator.subject,
            operation=ATO_DE_CLASSIFICAR,
            key=chave,
            response_status__isnull=False,
        ).exists()
        if not repetido and assinatura != assinatura_da_apuracao(
            edital, perfil["id"], marco_id, lista_id
        ):
            raise DomainError("stale_occupancy_reading", MUDOU_DESDE_A_CONFERENCIA, 409)
        emitir_apuracao(
            actor=ator,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=perfil["id"],
            marco_id=marco_id,
            lista_id=lista_id,
            idempotency_key=chave,
            correlation_id=correlacao,
            motivo="",
        )
    return _com_lista(reverse("interface:ocupacao-historico", args=[edital.id, marco_id]), lista_id)


def _publicar(
    *,
    ator,
    edital,
    marco_id,
    lista_id,
    assinatura,
    chave,
    correlacao,
    natureza,
    autoridade,
    declaracao,
    **_,
):
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        raise DomainError("sem_ato_vigente", SEM_ORDEM, 409)
    # **A declaração vai só a quem a exige** (RC-121): o ato com janela computável a recusaria,
    # porque ali o sistema verifica o prazo. A pergunta é refeita aqui, e não lida da conferência,
    # pela mesma razão de toda assinatura deste gesto: o que vale é o mundo da gravação.
    if not exige_declaracao(ato, marco_id, natureza):
        declaracao = ""
    publicar_resultado(
        actor=ator,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        marco_id=marco_id,
        ato_id=ato.id,
        natureza=natureza,
        autoridade=autoridade,
        confirmacao_da_previa=assinatura,
        idempotency_key=chave,
        correlation_id=correlacao,
        # Uma vez para o marco, gravada em cada publicação que a exige (`FR-827`): o comando decide
        # se ela é exigida, recusada ou gravada, e o gesto apenas a transporta — como a prévia.
        declaracao_de_encerramento=declaracao,
    )
    return reverse("interface:publicacoes-do-marco", args=[edital.id, marco_id])


_DESPACHO = {ORDENAR: _ordenar, CORTAR: _cortar, APURAR: _apurar, PUBLICAR: _publicar}


def verbo_da_confirmacao(operacao, quantidade):
    singular, plural = VERBOS[operacao]
    return (singular if quantidade == 1 else plural).format(n=quantidade)


__all__ = [
    "AMPLA",
    "APURAR",
    "CORTAR",
    "DA_GESTAO",
    "NOMES",
    "OPERACOES",
    "ORDENAR",
    "PUBLICAR",
    "alcance",
    "assinatura_da_apuracao",
    "chave_do_recorte",
    "conferir_natureza_e_autoridade",
    "correlacao_do_gesto",
    "exige_declaracao",
    "indicador_do_marco",
    "marco_publicado",
    "praticar",
    "recortes_ausentes",
    "recortes_do_marco",
    "resumo_dos_marcos",
    "verbo_da_confirmacao",
]
