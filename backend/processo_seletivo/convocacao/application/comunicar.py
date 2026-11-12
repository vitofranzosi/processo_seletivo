"""A emissão da comunicação da convocação, na forma que o Edital declarou (019, `D-009`).

**Este módulo é a terceira situação em que o sistema envia mensagem**, e a única que não é recibo
de ato praticado pela própria pessoa. A `FR-084` da `010` dizia que havia exatamente duas e que
acrescentar uma terceira **exige revisar a regra**; a revisão está escrita em
`specs/010-area-do-candidato/spec.md`, datada de 2026-09-12, e é a `REVISAO_DA_FR_084` abaixo que a
declara aqui.

**A guarda é de implantação, e não de domínio** (`FR-289`). Não é regra do certame: é recusa de
subir com duas normas contraditórias vigentes no mesmo repositório. Por isso o código dela está
separado dos demais no contrato, e por isso ela alcança só a mensagem individual — a convocação por
publicação não passa por caixa de entrada nenhuma.
"""

import logging
import re
from dataclasses import dataclass
from types import SimpleNamespace
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.domain import nomes, prazo, vocabulario_do_canal
from processo_seletivo.convocacao.domain.mensagem import (
    CORRECAO,
    INICIAL,
    escolha_da_mensagem,
    identificacao_do_modelo,
)
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
from processo_seletivo.convocacao.models import (
    ComunicacaoEmitida,
    Convocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.requerimentos.domain.disponibilidade import momento_declarado
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import identificacao

logger = logging.getLogger("processo_seletivo.convocacao")

COMUNICAR = "CONVOCACAO_COMUNICAR"
ATO = "convocacao:comunicar"

# **O texto da mensagem mora em arquivos de modelo, e não aqui** (121, FR-3882, D-009). Cada envio
# grava o resumo das duas fontes que o renderizaram (`modelo_da_mensagem`), e só o que está no
# arquivo entra no resumo: uma frase escrita neste módulo sairia sem versão identificável. Por isso
# o assunto também mora no modelo, na primeira linha do texto puro.
#
# O mínimo necessário continua (`FR-290`, revista pela `121`): o que a chamada pede, sem nomear nem
# contar documentos, até quando, como entrar e por onde falar. Sem CPF, sem nome, sem posição na
# ordem; e sem afirmar direito à vaga (`FR-292c`).
MODELOS = {
    INICIAL: ("convocacao/mensagem/inicial.html", "convocacao/mensagem/inicial.txt"),
    CORRECAO: ("convocacao/mensagem/correcao.html", "convocacao/mensagem/correcao.txt"),
}
SEM_ENDERECO = "sem endereço de destino para esta Inscrição"
FALHA_NA_MONTAGEM = "falha na montagem da mensagem"


@dataclass(frozen=True)
class Envio:
    """O que o envio devolve: o detalhe técnico da falha, ou `""`, e o modelo que renderizou."""

    detalhe: str
    modelo: str


#: A data da revisão escrita da `FR-084` da `010`, declarada aqui e conferida contra a spec por
#: `tests/test_situacoes_de_mensagem.py`.
#:
#: **Constante, e não leitura da spec em tempo de execução.** Ler `specs/` daqui acoplaria o envio
#: a uma árvore que o contêiner de produção não carrega — e a convocação passaria a falhar por
#: ausência de arquivo de documentação, que é uma falha pior do que a que a guarda existe para
#: impedir. A contradição entre norma e código é achada onde ela pertence: na suíte, que lê as duas.
#:
#: `None` desliga a terceira situação, e é o valor correto enquanto a revisão não estiver escrita.
REVISAO_DA_FR_084 = "2026-09-12"


#: A recusa da comunicação sem forma declarada, dita uma vez: o envio e a conferência da chamada
#: (152, FR-5817) a dizem com as mesmas palavras.
SEM_FORMA_DECLARADA = (
    "O Perfil publicado não declarou como este Edital comunica a convocação: declare a forma por "
    "Retificação antes de emitir."
)


def guarda_da_revisao_da_010():
    """Recusa a mensagem individual enquanto a `FR-084` da `010` não estiver revisada (`FR-289`).

    A `R-008` fez da revisão uma **fase própria**, anterior a qualquer envio individual, e não uma
    exceção silenciosa dentro desta feature. Implementar o envio sem ela deixaria duas regras
    vigentes e contraditórias no mesmo repositório — e a que o candidato leria seria a errada.
    """
    if not REVISAO_DA_FR_084:
        raise DomainError(
            nomes.ENVIO_SEM_REVISAO_DA_010,
            "A mensagem individual de convocação depende da revisão escrita da FR-084 da 010, "
            "que ainda não foi feita: enquanto ela não existir, o sistema não envia.",
            409,
        )


def forma_declarada(convocacao):
    """A forma que o Perfil publicado declarou, lida da **versão que a convocação citou**.

    **Da versão citada, e não da vigente.** A convocação congelou a norma que valia quando foi
    praticada; uma Retificação posterior não pode mudar por qual canal aquela chamada foi feita.

    `None` significa *"este Edital não declarou forma"*, e nunca a publicação por omissão: as duas
    formas da amostra são normais, e escolher uma decidiria norma no lugar do Edital.
    """
    from processo_seletivo.convocacao.application.selectors import forma_do_perfil

    return forma_do_perfil((convocacao.versao.content or {}).get("profiles"), convocacao.perfil_id)


def destinatario_de(convocacao):
    """Para onde a mensagem individual vai: a credencial principal, ou o endereço da Inscrição.

    **A regra mora em `identidade/application/endereco.py`** desde a `066`, porque o aviso
    complementar precisa exatamente dela, e duas cópias divergiriam no primeiro ajuste. Este nome
    fica, para que nenhum chamador da convocação mude.
    """
    from processo_seletivo.identidade.application.endereco import endereco_da_inscricao

    return endereco_da_inscricao(convocacao.inscricao)


def comunicar(
    *,
    actor,
    processo_id,
    convocacao_id,
    idempotency_key,
    correlation_id,
    endereco_do_portal="",
    referencia_da_publicacao="",
):
    """Emite a comunicação na forma declarada, e registra o que aconteceu — inclusive a falha.

    **A falha não apaga o ato** (`FR-269a`). A convocação continua praticada; o que se registra é
    que a emissão não completou, e o recorte passa a exibir *"convocado, prazo não iniciado"* até
    que uma emissão tenha sucesso.

    **O envio acontece fora da transação, e nunca dentro dela.** É a regra que
    `inscricoes/application/mensagem.py` escreve com todas as letras, e a razão aqui é a mesma
    aumentada de um grau: `comando_de_comissao` trava o Processo com `select_for_update`, de modo
    que um SMTP lento paralisaria **todos** os comandos daquele certame — e um `rollback` posterior
    desfaria o registro sem desfazer a mensagem.

    **E a chave é reservada antes do envio**, numa transação curta e própria. Tirar o envio de
    dentro da transação deixou a idempotência **depois** dele: um duplo clique, ou o retry de um
    proxy, entregava a segunda mensagem e só então descobria que o ato já havia terminado. A ordem
    é reservar, conferir, enviar, gravar.

    **Reserva pendente não reenvia.** Quando a chave já existe e nunca foi concluída, ou o envio
    está em curso noutra requisição, ou ele saiu e a gravação falhou depois dele — e as duas
    hipóteses têm a mesma aparência daqui. Reenviar por conta própria entregaria a mesma convocação
    duas vezes; o que o comando faz é dizer que o estado é indeterminado e pedir reconciliação, que
    é o único desfecho honesto.
    """
    from processo_seletivo.comissoes.application import exigir_base_de_comissao

    # **Autorizar antes de trabalhar** (Princípio III): sem isto, um ator sem base faria o sistema
    # reservar chave e ir à rede antes de a pergunta "quem está pedindo" ser feita.
    exigir_base_de_comissao(actor=actor, processo_id=processo_id)
    convocacao = _convocacao_do_processo_id(processo_id, convocacao_id, actor=actor)
    forma = forma_declarada(convocacao)
    if forma is None:
        raise DomainError(nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA, SEM_FORMA_DECLARADA, 409)
    agora = timezone.now()
    _recusar_convocacao_desfechada(convocacao)
    _recusar_vencimento_anterior_ao_envio(convocacao, agora=agora)

    referencia = (referencia_da_publicacao or "").strip()
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        guarda_da_revisao_da_010()
    elif not referencia:
        # **O sistema não publica no site do certame**, e registrar `ENVIADA` sem referência
        # iniciaria o prazo de uma convocação que ninguém viu (`FR-288`).
        raise DomainError(
            nomes.REFERENCIA_DA_PUBLICACAO_OBRIGATORIA,
            "Este Edital comunica a convocação por publicação: declare onde ela foi publicada — "
            "o endereço e a data —, porque o prazo corre a partir disso e o sistema não publica "
            "por conta própria.",
            422,
            campo="referencia_da_publicacao",
        )

    # **A mesma carga que `comando_de_comissao` usará adiante**: a reserva é a mesma linha, e um
    # conteúdo diferente aqui produziria `idempotency_conflict` contra a própria chamada.
    payload = {"convocacao": str(convocacao_id)}
    concluida, pendente = _reservar_a_chave(actor=actor, key=idempotency_key, payload=payload)
    if concluida is not None:
        # **Repetição concluída não envia nada**, e devolve o que o ato respondeu — o duplo clique
        # recebe a emissão original, e não uma segunda mensagem na caixa da pessoa.
        return concluida
    if pendente:
        raise DomainError(
            nomes.EMISSAO_EM_ESTADO_INDETERMINADO,
            vocabulario_do_canal.canal(forma).recusa_do_estado_indeterminado,
            409,
        )

    destinatario, detalhe, modelo = "", "", ""
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        destinatario = destinatario_de(convocacao)
        envio = _enviar(
            convocacao,
            destinatario=destinatario,
            endereco_do_portal=endereco_do_portal,
            agora=agora,
        )
        detalhe, modelo = envio.detalhe, envio.modelo

    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        emitida = ComunicacaoEmitida(
            convocacao=convocacao,
            forma=forma,
            destinatario=destinatario,
            referencia_da_publicacao=referencia if forma == FORMA_POR_PUBLICACAO else "",
            # **`FALHA` não tem instante, e a constraint o exige.** Um registro marcado enviado sem
            # instante faria o prazo correr a partir de nada.
            enviado_em=None if detalhe else agora,
            resultado="FALHA" if detalhe else "ENVIADA",
            detalhe_tecnico=detalhe,
            # A versão do modelo que renderizou, na mesma linha e na mesma transação do resultado
            # — também na falha, que diz qual texto se tentou enviar (121, FR-3889). Vazia na
            # publicação, que não tem modelo.
            modelo_da_mensagem=modelo,
        )
        emitida.save()
        return _concluir(ctx, emitida, actor, correlation_id, idempotency_key)


def _reservar_a_chave(*, actor, key, payload):
    """Reserva a chave numa transação curta e diz o que ela encontrou.

    Devolve `(desfecho_anterior, pendente)`: o desfecho quando a chave já foi **concluída**, e
    `pendente=True` quando ela existe e nunca foi. Nos dois casos nada é enviado.

    **Transação própria, curta, e sem travar o Processo.** O que ela precisa garantir é que duas
    requisições com a mesma chave não criem duas reservas — e é o `UNIQUE` de
    `IdempotencyRecord` que o garante, não a duração da transação. Segurá-la aberta durante o SMTP
    seria trocar um problema por outro.
    """
    from django.db import transaction

    from processo_seletivo.shared.idempotency import reservar

    with transaction.atomic():
        reserva, criada = reservar(actor=actor, operation=ATO, key=key, payload=payload)
        if reserva.response_status is not None:
            return reserva.result_payload, False
        return None, not criada


def _convocacao_do_processo_id(processo_id, convocacao_id, *, actor):
    """A convocação, conferida contra o Processo **antes** de a transação abrir.

    A conferência de autoridade já aconteceu em `exigir_base_de_comissao`; esta confere que a
    convocação pertence ao Processo autorizado — e recusa como não encontrada, pela mesma razão de
    sempre: dizer *"existe, mas não é sua"* já entregaria que existe.
    """
    convocacao = (
        Convocacao.objects.filter(
            id=identificador(convocacao_id), edital__processo_id=identificador(processo_id)
        )
        .select_related("edital", "versao", "inscricao")
        .first()
    )
    if convocacao is None:
        raise DomainError("convocacao_nao_encontrada", "Convocação não encontrada.", 404)
    return convocacao


def _recusar_convocacao_desfechada(convocacao):
    """Chamada com desfecho não se comunica (050).

    **A mensagem diria "você foi convocada" a quem já respondeu**, ou a quem a Administração já deu
    por não atendida. O gesto das comunicações pendentes confere o alcance fora da trava, e o
    desfecho registrado entre a conferência e o envio passava; a recusa aqui, logo antes de reservar
    a chave, é a última porta antes da caixa de entrada da pessoa.
    """
    from processo_seletivo.convocacao.application.selectors import desfecho_de

    if desfecho_de(convocacao) is not None:
        raise DomainError(
            nomes.CONVOCACAO_DESFECHADA,
            "Esta convocação já tem desfecho registrado: não há o que comunicar.",
            409,
        )


def _recusar_vencimento_anterior_ao_envio(convocacao, *, agora):
    """`FR-269b`, `vencimento_anterior_ao_envio`: prazo que vence antes de a pessoa poder saber.

    **A conferência é aqui, e não ao convocar**, porque é o envio que inicia o relógio: no instante
    da convocação ainda não existe envio com que comparar. Um vencimento informado com o ano errado
    só se revela quando a mensagem vai partir — e é aí que a recusa precisa acontecer, antes de a
    pessoa receber um prazo já vencido.
    """
    if prazo.vencimento_precede_o_envio(vencimento=convocacao.vencimento, enviado_em=agora):
        raise DomainError(
            nomes.VENCIMENTO_ANTERIOR_AO_ENVIO,
            # A frase do canal (125, FR-4001).
            vocabulario_do_canal.canal(forma_declarada(convocacao)).recusa_do_vencimento
            + "corrija a convocação, sucedendo-a com motivo, antes de comunicar.",
            409,
        )


def escolha_de(convocacao, *, instante):
    """A mensagem que sai para `convocacao` no `instante`, só de registros gravados (121, R-002).

    **A mesma função no envio e na reconstrução** (FR-3889): chamada depois, sobre os mesmos
    registros, ela devolve o mesmo modelo, a mesma variante e a mesma citada. A cadeia é lida de uma
    vez — todas as convocações da inscrição, com as comunicações — e percorrida em memória, da
    imediatamente anterior à raiz. A lista é a da raiz, que é a dona dela (D-009 da `115`); o
    Requerimento é o da versão que a convocação citou, e não o de hoje.
    """
    # Sem anterior não há cadeia a ler: a primeira chamada é a inicial, e é a maioria dos envios —
    # na convocação em lote, a leitura seriam duas consultas por pessoa sem resposta nenhuma.
    da_inscricao = (
        {
            elo.id: elo
            for elo in Convocacao.objects.filter(
                inscricao_id=convocacao.inscricao_id
            ).prefetch_related("comunicacoes")
        }
        if convocacao.convocacao_anterior_id is not None
        else {}
    )
    anteriores, raiz_id = [], convocacao.id
    atual = da_inscricao.get(convocacao.convocacao_anterior_id)
    while atual is not None:
        anteriores.append(
            SimpleNamespace(
                vencimento=atual.vencimento, comunicacoes=list(atual.comunicacoes.all())
            )
        )
        raiz_id = atual.id
        atual = da_inscricao.get(atual.convocacao_anterior_id)
    itens = ItemDaListaDaConvocacao.objects.filter(chamada_id=raiz_id).only(
        "situacao", "gravada_em"
    )
    return escolha_da_mensagem(
        itens=list(itens),
        instante=instante,
        requerimento_na_chamada=(
            momento_declarado(convocacao.versao.content) == requerimento_nomes.NA_CONVOCACAO
        ),
        anteriores=anteriores,
    )


def link_da_convocacao(endereco_do_portal, inscricao_id):
    """A convocação da inscrição, juntada à origem do portal; o caminho, sem base (121, FR-3883).

    O link nunca autentica (P-001 da `010`): sem sessão, ele leva ao acesso, e depois do código à
    convocação. O identificador da inscrição só vai aqui (FR-1102 da `059`).
    """
    return urljoin(endereco_do_portal or "", reverse("portal:convocacao", args=[inscricao_id]))


def _enviar(convocacao, *, destinatario, endereco_do_portal, agora=None, escolha=None):
    """Monta e envia a mensagem, e devolve o `Envio`: o detalhe da falha e o modelo que renderizou.

    **Sem dado pessoal no detalhe técnico**: ele vai para o registro e para a tela de quem conduz o
    certame, e o endereço de alguém não tem por que estar em nenhum dos dois.
    """
    agora = agora or timezone.now()
    try:
        escolha = escolha or escolha_de(convocacao, instante=agora)
        # A unidade do Edital assina e diz por onde falar (109, FR-3209, FR-3212). Uma leitura por
        # envio, e o envio é de uma pessoa: a convocação por mensagem individual não sai em lote.
        unidade = identificacao.da_unidade(convocacao.edital.institution_scope)
        conteudo = convocacao.versao.content or {}
    except Exception as erro:
        # **A chave já está reservada** quando se chega aqui: uma exceção que subisse deixaria a
        # reserva sem registro, e toda nova tentativa com ela diria "estado indeterminado" por uma
        # mensagem que nunca saiu. A falha vira `FALHA` gravada, como a do correio (`FR-269a`).
        logger.exception("Falha ao montar a comunicação de convocação.")
        return Envio(f"{type(erro).__name__}: {FALHA_NA_MONTAGEM}", "")
    return enviar_mensagem_de_convocacao(
        para=destinatario,
        dados=_dados_da_mensagem(
            edital=convocacao.edital,
            conteudo=conteudo,
            unidade=unidade,
            vencimento=convocacao.vencimento,
            enviado_em=agora,
            link=link_da_convocacao(endereco_do_portal, convocacao.inscricao_id),
            escolha=escolha,
        ),
    )


def _dados_da_mensagem(*, edital, conteudo, unidade, vencimento, enviado_em, link, escolha):
    """O que o modelo recebe, montado num lugar só para o envio e para a conferência (140)."""
    return {
        "edital": f"Edital {edital.number}/{edital.year}",
        "processo": conteudo.get("processoTitle", ""),
        "vencimento": vencimento,
        "enviado_em": enviado_em,
        "link": link,
        "escolha": escolha,
        "requerimento_exigido": bool(momento_declarado(conteudo)),
        "atendimento": unidade.canal("a comissão do certame"),
        "assinatura": unidade.rotulo,
        "unidade": unidade.sigla,
    }


def _contexto(dados):
    """O que os modelos leem: o prazo apresentado no fuso da instalação, do instante do envio."""
    fuso = ZoneInfo(settings.TIME_ZONE)
    enviado_em = dados.get("enviado_em") or timezone.now()
    escolha = dados["escolha"]
    citada = escolha.citada
    return {
        "instituicao": identificacao.SIGLA_DA_INSTITUICAO,
        "instituicao_por_extenso": identificacao.NOME_DA_INSTITUICAO,
        "unidade": dados.get("unidade", ""),
        "edital": dados["edital"],
        "processo": dados.get("processo", ""),
        "variante": escolha.variante,
        "prazo": (
            apresentar(dados["vencimento"], enviado_em, fuso) if dados.get("vencimento") else None
        ),
        "link": dados["link"],
        "requerimento_exigido": dados.get("requerimento_exigido", False),
        # Chega resolvida, como o canal: quem envia sabe o Edital (109). Exigida, e sem recaída —
        # uma recaída aqui seria um Cefor escrito de novo, ou uma consulta que a função não faz.
        "assinatura": dados["assinatura"],
        "atendimento": dados["atendimento"],
        "citada_enviada": apresentar(citada.enviado_em, enviado_em, fuso) if citada else None,
        "citada_prazo": (
            apresentar(citada.vencimento, enviado_em, fuso)
            if citada and citada.vencimento
            else None
        ),
    }


def _assunto_e_corpo(texto):
    """A primeira linha do texto puro é o assunto; o resto, sem as linhas vazias das tags."""
    linhas = [linha.rstrip() for linha in texto.strip("\n").split("\n")]
    corpo = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas[1:]).strip("\n"))
    return linhas[0].strip(), corpo + "\n"


def _modelos(nome):
    return tuple(get_template(caminho) for caminho in MODELOS[nome])


def _renderizar(html_do_modelo, texto_do_modelo, dados):
    """O HTML, o assunto e o corpo da mensagem — **a mesma composição no envio e na conferência**.

    A conferência antes de convocar (140, D-003) mostra o texto que sairá. Uma segunda composição
    feita para a tela poderia divergir do envio em silêncio; esta é a única.
    """
    contexto = _contexto(dados)
    html = html_do_modelo.render(contexto)
    assunto, corpo = _assunto_e_corpo(texto_do_modelo.render(contexto))
    return html, assunto, corpo


#: O que a conferência mostra no lugar do link, que é de cada pessoa (140, FR-4803).
LINK_NA_CONFERENCIA = "[o link da convocação de cada pessoa, na área do candidato]"


def previa_das_mensagens(*, edital, versao, inscricoes, vencimento, agora):
    """As mensagens que o gesto dos titulares enviaria agora, **sem enviar nada** (140, D-003).

    **A variante sai do que o ato gravaria**: a lista da chamada é a aplicabilidade da versão
    vigente, no momento da convocação, para o Perfil e a Modalidade de cada pessoa
    (`gravar_lista_da_chamada`), e o Requerimento é o que a versão declara para esse momento. O
    modelo é o inicial: o gesto só alcança quem ainda não foi chamado, e quem não foi chamado não
    tem mensagem anterior a citar (D-008 da `121`, pelo assunto).

    Devolve um item por mensagem distinta, com quantas pessoas a receberiam e quem são, na ordem em
    que vieram. Nenhuma consulta por pessoa: uma para as inscrições, uma para a unidade.
    """
    from processo_seletivo.convocacao.domain.mensagem import EscolhaDaMensagem, variante_de
    from processo_seletivo.editais.domain.documentos import NA_CONVOCACAO, aplicabilidade
    from processo_seletivo.inscricoes.models import Inscricao

    conteudo = versao.content or {}
    requerimento = momento_declarado(conteudo) == requerimento_nomes.NA_CONVOCACAO
    unidade = identificacao.da_unidade(edital.institution_scope)
    por_id = {
        str(linha["id"]): linha
        for linha in Inscricao.objects.filter(id__in=list(inscricoes)).values(
            "id", "profile_id", "modality_id"
        )
    }
    modelos = _modelos(INICIAL)
    grupos = {}
    for inscricao in inscricoes:
        linha = por_id[str(inscricao)]
        vereditos = aplicabilidade(
            conteudo,
            profile_id=str(linha["profile_id"]),
            modality_id=None if linha["modality_id"] is None else str(linha["modality_id"]),
            momento=NA_CONVOCACAO,
        )
        itens = [SimpleNamespace(situacao=v.situacao, gravada_em=agora) for v in vereditos]
        variante = variante_de(itens=itens, instante=agora, requerimento_na_chamada=requerimento)
        if variante not in grupos:
            _, assunto, corpo = _renderizar(
                *modelos,
                _dados_da_mensagem(
                    edital=edital,
                    conteudo=conteudo,
                    unidade=unidade,
                    vencimento=vencimento,
                    enviado_em=agora,
                    link=LINK_NA_CONFERENCIA,
                    escolha=EscolhaDaMensagem(modelo=INICIAL, variante=variante),
                ),
            )
            grupos[variante] = {"assunto": assunto, "corpo": corpo, "inscricoes": []}
        grupos[variante]["inscricoes"].append(str(inscricao))
    return list(grupos.values())


def enviar_mensagem_de_convocacao(*, para, dados):
    """A terceira situação em que o sistema envia mensagem (`FR-084` da `010`, revisada).

    **HTML e texto puro, dos modelos da mensagem** (121, FR-3882 a FR-3887): o texto contém tudo o
    que o HTML diz, e a mensagem diz o que a chamada pede, com o prazo e o dia da semana, o link da
    convocação e o que o Ifes nunca pede por e-mail.

    **A renderização vem antes da conferência do destinatário** (121, plano, seção 5): toda
    tentativa tem modelo, e a falha por endereço ausente também grava qual texto se tentou enviar.
    Nada sai a mais: sem endereço, nada sai.

    **Nenhuma exceção sai daqui** depois da reserva da chave: o modelo que não carrega, a
    renderização que quebra e o correio que recusa voltam todos como `Envio` com detalhe, e o
    comando grava a `FALHA` — com o modelo, sempre que ele chegou a carregar.

    **Nenhum link que autentica** (P-001 da `010`): o link leva à convocação, e a entrada continua
    sendo por código digitado.
    """
    try:
        html_do_modelo, texto_do_modelo = _modelos(dados["escolha"].modelo)
    except Exception as erro:
        logger.exception("Falha ao carregar o modelo da comunicação de convocação.")
        return Envio(f"{type(erro).__name__}: {FALHA_NA_MONTAGEM}", "")
    # O resumo das fontes que o motor compilou e que renderizam logo abaixo, e não do arquivo
    # relido do disco (R-009). Antes da renderização, para a falha dela também dizer o modelo.
    modelo = identificacao_do_modelo(dados["escolha"].modelo, html_do_modelo, texto_do_modelo)
    try:
        html, assunto, corpo = _renderizar(html_do_modelo, texto_do_modelo, dados)
    except Exception as erro:
        logger.exception("Falha ao renderizar a comunicação de convocação.")
        return Envio(f"{type(erro).__name__}: {FALHA_NA_MONTAGEM}", modelo)
    if not para:
        return Envio(SEM_ENDERECO, modelo)
    mensagem = EmailMultiAlternatives(
        subject=assunto,
        body=corpo,
        from_email=settings.DEFAULT_FROM_EMAIL or None,
        to=[para],
    )
    mensagem.attach_alternative(html, "text/html")
    try:
        # **O retorno é contado**, e não descartado: o envio devolve quantas mensagens entraram na
        # fila, e um backend que engole a mensagem devolve `0` sem levantar exceção nenhuma.
        # Ignorá-lo gravava `ENVIADA` e iniciava o prazo de uma convocação que não saiu — a falha
        # mais silenciosa possível, porque tudo indica sucesso.
        entregues = mensagem.send(fail_silently=False)
    except Exception as erro:
        # Sem o endereço: o registro técnico diz que falhou e qual foi o erro, e nada além disso.
        logger.exception("Falha ao emitir a comunicação de convocação.")
        return Envio(f"{type(erro).__name__}: falha na emissão", modelo)
    if not entregues:
        logger.error("A comunicação de convocação não foi aceita pelo servidor de correio.")
        return Envio("o servidor de correio não aceitou a mensagem", modelo)
    return Envio("", modelo)


def _concluir(ctx, emitida, actor, correlation_id, idempotency_key):
    convocacao = emitida.convocacao
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=COMUNICAR,
        aggregate=emitida,
        now=ctx.now,
        correlation_id=correlation_id,
        # **"Enviada em", e nunca "recebida em"** (`UX-039`, `FR-288a`). A trilha diz o que o
        # sistema fez; o que aconteceu na caixa de entrada da pessoa ele não sabe, e não afirma.
        # Na publicação, nada foi enviado: a trilha diz que a comissão registrou onde publicou
        # (125, R-008). Os registros antigos ficam como estão — a trilha só acrescenta.
        reason=(
            (
                f"Publicação da convocação {convocacao.id}, inscrição {convocacao.inscricao_id}, "
                f"registrada pela comissão: {emitida.referencia_da_publicacao}. Registro em "
                f"{emitida.enviado_em.isoformat()}."
            )
            if emitida.forma == FORMA_POR_PUBLICACAO and emitida.enviado_em
            else (
                f"Comunicação {emitida.resultado} da convocação {convocacao.id}, inscrição "
                f"{convocacao.inscricao_id}, na forma {emitida.forma}."
                + (f" Enviada em {emitida.enviado_em.isoformat()}." if emitida.enviado_em else "")
                + (
                    f" Detalhe técnico: {emitida.detalhe_tecnico}"
                    if emitida.detalhe_tecnico
                    else ""
                )
            )
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(emitida.id),
        "convocacao": str(convocacao.id),
        "forma": emitida.forma,
        "resultado": emitida.resultado,
        "enviadaEm": emitida.enviado_em.isoformat() if emitida.enviado_em else None,
        # A referência, para a confirmação dizer onde foi publicada (125, FR-4000).
        "referencia": emitida.referencia_da_publicacao,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


__all__ = [
    "MODELOS",
    "REVISAO_DA_FR_084",
    "Envio",
    "comunicar",
    "destinatario_de",
    "enviar_mensagem_de_convocacao",
    "escolha_de",
    "forma_declarada",
    "guarda_da_revisao_da_010",
    "link_da_convocacao",
    "previa_das_mensagens",
]
