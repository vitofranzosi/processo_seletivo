"""Carregar, verificar e restaurar cenários (134, FR-4610 a FR-4626).

**Três garantias, e cada uma tem o seu lugar.**

1. *Só acrescenta.* Nenhum caminho deste módulo apaga linha, e nenhum altera linha que o gerador não
   criou: a escrita é dos comandos da aplicação, e o único `UPDATE` direto é o do manifesto.
2. *Tudo ou nada por cenário.* A montagem e o manifesto estão na mesma transação: se um passo
   recusa, o cenário inteiro some, e o que fica no banco é o que havia antes (FR-4612).
3. *Não sobrescreve.* Um cenário pronto não é tocado de novo pela carga, e um vestígio sem manifesto
   — um Processo com o código reservado que o gerador não reconhece — é relatado, não reaproveitado
   (FR-4614).

**Restaurar não é apagar** (D-002). Publicação, trilha e as tabelas append-only recusam exclusão,
por gatilho e por privilégio, e a Constituição a proíbe. Restaurar é criar a rodada seguinte do
cenário, do zero e com as datas de hoje, e cancelar a anterior pelos comandos de cancelamento —
que deixam o histórico inteiro, e tiram o Processo antigo da aba "Em andamento".
"""

import traceback
from dataclasses import dataclass, field
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.test.utils import override_settings
from django.utils import timezone

from processo_seletivo.processos.management.commands.seed_demo import (
    _relogio_atrasado as relogio_atrasado,
)
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.treinamento import ambiente
from processo_seletivo.treinamento.catalogo import CENARIOS, POR_CODIGO, concurso_da_rodada
from processo_seletivo.treinamento.construcao import (
    ACESSOS,
    FORMALIZACAO,
    GESTAO,
    MARCA,
    Montagem,
    ano_local,
    ator,
    codigo_do_processo,
    numero_do_edital,
)
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from processo_seletivo.treinamento.retrato import diferencas, retratar

PREFIXO_DO_CODIGO = "SIM-TREINAMENTO-"


class Recusa(Exception):
    """Uma recusa do gerador, com a frase para quem roda o comando."""


@dataclass
class Situacao:
    cenario: object
    manifesto: CenarioDeTreinamento | None = None
    vestigios: list = field(default_factory=list)
    problemas: list = field(default_factory=list)
    mudancas: list = field(default_factory=list)
    avisos: list = field(default_factory=list)

    @property
    def estado(self):
        if self.problemas:
            return "INCONSISTENTE"
        if self.manifesto is None:
            return "CONFLITO" if self.vestigios else "AUSENTE"
        if self.mudancas:
            return "EXERCITADO"
        return "INTACTO"


def escolher(codigos):
    """Os cenários pedidos, na ordem do catálogo; todos, sem pedido."""
    if not codigos:
        return list(CENARIOS)
    pedidos = {codigo.strip().upper() for codigo in codigos}
    desconhecidos = sorted(pedidos - set(POR_CODIGO))
    if desconhecidos:
        raise Recusa(
            f"Cenário desconhecido: {', '.join(desconhecidos)}. "
            f"Os do catálogo são {', '.join(POR_CODIGO)}."
        )
    return [cenario for cenario in CENARIOS if cenario.codigo in pedidos]


def autoridade_vigente(unidade, escolhida=None):
    """A autoridade que assina os atos fictícios — sem criar nenhuma, e sem mudar nenhuma.

    **O gerador não cria configuração institucional** (FR-4615): uma autoridade é registro da
    unidade, com motivo e trilha, e quem a cadastra é o Gestor pela tela.

    **E só usa, sem pedir, autoridade que já foi usada** (FR-4616). O primeiro ato praticado com uma
    autoridade grava `usada_em`, e a partir dali o nome, o cargo e a nomeação dela ficam imutáveis
    (060, FR-1121): um gerador que escolhesse uma autoridade recém-cadastrada congelaria, em
    silêncio, um registro que a equipe ainda pode estar completando. A suíte achou isto — o
    instantâneo linha a linha acusou a autoridade alterada. Sem autoridade já usada, a carga é
    recusada e diz como escolher uma por extenso, com `--autoridade`.
    """
    from processo_seletivo.shared.tempo import ZONA
    from processo_seletivo.unidades.application.selectors import autoridades_vigentes

    hoje = timezone.now().astimezone(ZONA).date()
    vigentes = list(autoridades_vigentes(unidade, hoje))
    if escolhida:
        for autoridade in vigentes:
            if str(autoridade.pk) == str(escolhida):
                return str(autoridade.pk)
        raise Recusa(f"A autoridade {escolhida} não é vigente na unidade {unidade}.")
    usadas = [autoridade for autoridade in vigentes if autoridade.usada_em is not None]
    if usadas:
        return str(usadas[0].pk)
    if not vigentes:
        raise Recusa(
            f"A unidade {unidade} não tem autoridade vigente para assinar os atos. Cadastre uma "
            "pela tela de autoridades do Gestor e rode de novo — o gerador não cria configuração "
            "institucional."
        )
    opcoes = "; ".join(f"{autoridade.pk} ({autoridade.cargo})" for autoridade in vigentes)
    raise Recusa(
        f"Nenhuma autoridade vigente da unidade {unidade} foi usada ainda, e o primeiro uso torna "
        "o cadastro dela imutável (FR-1121). Escolha uma por extenso com --autoridade, sabendo "
        f"disso: {opcoes}."
    )


def _vestigios(cenario, unidade):
    """Processos com o código reservado do cenário que nenhum manifesto reconhece."""
    # Por expressão, e não por lista de rodadas: a lista ia até a R99, e um Processo -R100 sem
    # manifesto passava sem ser acusado.
    base = codigo_do_processo(cenario.codigo, 1)
    candidatos = ProcessoSeletivo.objects.filter(
        institution_scope=unidade, institutional_code__regex=rf"^{base}(-R[0-9]+)?$"
    )
    reconhecidos = set(
        CenarioDeTreinamento.objects.filter(unidade=unidade, codigo=cenario.codigo).values_list(
            "processo_id", flat=True
        )
    )
    return [processo for processo in candidatos if processo.id not in reconhecidos]


def _conferir_propriedade(manifesto):
    """O que impede tratar o Processo do manifesto como do gerador (FR-4613, FR-4622)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    problemas = []
    processo = manifesto.processo
    if not processo.institutional_code.startswith(PREFIXO_DO_CODIGO):
        problemas.append(f"o Processo {processo.id} não tem mais o código reservado.")
    if processo.institution_scope != manifesto.unidade:
        problemas.append("o Processo é de outra unidade que a do manifesto.")
    criacao = (
        RegistroAuditoria.objects.filter(aggregate_id=processo.id, operation="CRIAR")
        .order_by("occurred_at")
        .first()
    )
    if criacao is None or criacao.correlation_id != manifesto.correlation_id:
        problemas.append(
            "a trilha não mostra o Processo criado pelo gerador nesta rodada "
            f"(esperado {manifesto.correlation_id})."
        )
    registrados = set(manifesto.registros.get("edital", []))
    existentes = {
        str(pk) for pk in Edital.objects.filter(processo=processo).values_list("id", flat=True)
    }
    if not registrados <= existentes:
        problemas.append("um Edital registrado no manifesto não está mais no Processo.")
    return problemas


def _em_uso(cenario, unidade):
    return (
        CenarioDeTreinamento.objects.select_related("processo")
        .filter(
            unidade=unidade, codigo=cenario.codigo, situacao=CenarioDeTreinamento.Situacao.PRONTO
        )
        .first()
    )


def situacao(cenario, unidade):
    manifesto = _em_uso(cenario, unidade)
    resultado = Situacao(
        cenario=cenario, manifesto=manifesto, vestigios=_vestigios(cenario, unidade)
    )
    if manifesto is None:
        return resultado
    resultado.problemas = _conferir_propriedade(manifesto)
    if not resultado.problemas:
        resultado.mudancas = diferencas(manifesto.retrato, retratar(manifesto.processo))
    if manifesto.versao_da_definicao != cenario.versao:
        resultado.avisos.append(
            f"gerado com a versão {manifesto.versao_da_definicao} da receita; a atual é "
            f"{cenario.versao}. Restaure para ter a atual."
        )
    if cenario.validade_dias is not None:
        vence = manifesto.criado_em + timezone.timedelta(days=cenario.validade_dias)
        if timezone.now() >= vence:
            resultado.avisos.append(
                f"o prazo do estado inicial venceu em {timezone.localtime(vence):%d/%m/%Y}: "
                "restaure para ter datas novas."
            )
    return resultado


def _proxima_rodada(cenario, unidade):
    ultima = (
        CenarioDeTreinamento.objects.filter(unidade=unidade, codigo=cenario.codigo)
        .order_by("-rodada")
        .values_list("rodada", flat=True)
        .first()
    )
    return (ultima or 0) + 1


def conflitos_de_montagem(cenario, unidade, rodada, ano):
    """O que impediria a rodada de nascer, conferido **antes** de qualquer escrita (FR-4614)."""
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    conflitos = []
    codigo, numero = (
        codigo_do_processo(cenario.codigo, rodada),
        numero_do_edital(cenario.codigo, rodada),
    )
    if ProcessoSeletivo.objects.filter(
        institution_scope=unidade, institutional_code=codigo
    ).exists():
        conflitos.append(f"já existe Processo {codigo} na unidade.")
    if Edital.objects.filter(institution_scope=unidade, number=numero, year=ano).exists():
        conflitos.append(f"já existe Edital {numero}/{ano} na unidade.")
    if cenario.exige_fonte_de_demonstracao:
        if not getattr(settings, "SORTEIO_FONTE_DE_DEMONSTRACAO", False):
            conflitos.append(
                "a fonte de demonstração do sorteio não está ligada neste ambiente "
                "(SORTEIO_FONTE_DE_DEMONSTRACAO)."
            )
        elif OcorrenciaDaFonte.objects.filter(
            referencia=(concurso := concurso_da_rodada(unidade, cenario.codigo, rodada))
        ).exists():
            conflitos.append(
                f"o concurso {concurso} da fonte de demonstração já foi observado por outro "
                "certame."
            )
    return conflitos


def planejar(codigos, unidade):
    """O que a carga faria, sem escrever nada — a pré-visualização (FR-4604).

    **Sem o retrato.** Decidir entre criar e manter só pede o manifesto em uso e os vestígios; o
    retrato é uma contagem por vínculo do domínio, e a pré-visualização dos quinze prontos fazia
    centenas delas para descartá-las.
    """
    plano = []
    ano = ano_local()
    # O que um cenário anterior deste mesmo plano já provisiona: com o C16 e o C17 juntos num banco
    # novo, só o primeiro cria a pessoa e concede o papel (FR-6725).
    provisionado = False
    for cenario in escolher(codigos):
        manifesto = _em_uso(cenario, unidade)
        if manifesto is not None:
            plano.append((cenario, "MANTER", [f"rodada {manifesto.rodada} já existe"]))
            continue
        vestigios = _vestigios(cenario, unidade)
        if vestigios:
            codigos_achados = ", ".join(p.institutional_code for p in vestigios)
            plano.append((cenario, "RECUSAR", [f"Processo sem manifesto: {codigos_achados}"]))
            continue
        rodada = _proxima_rodada(cenario, unidade)
        conflitos = conflitos_de_montagem(cenario, unidade, rodada, ano)
        detalhes = conflitos or [
            f"rodada {rodada}",
            *_provisionamento(cenario, unidade, ja_provisionado=provisionado),
        ]
        provisionado = provisionado or (not conflitos and cenario.provisiona_formalizacao)
        plano.append((cenario, "RECUSAR" if conflitos else "CRIAR", detalhes))
    return plano


def _provisionamento(cenario, unidade, *, ja_provisionado=False):
    """O que o C16 e o C17 criariam ou manteriam da pessoa do setor (FR-6725)."""
    if not cenario.provisiona_formalizacao:
        return []
    if ja_provisionado:
        return [f"pessoa {FORMALIZACAO} e papel Formalização em {unidade}: do cenário anterior"]
    from django.contrib.auth import get_user_model

    from processo_seletivo.formalizacao.domain import nomes
    from processo_seletivo.seguranca.application import acessos

    pessoa = get_user_model().objects.filter(username=FORMALIZACAO).first()
    com_o_papel = (
        pessoa is not None
        and acessos.vigentes().filter(pessoa=pessoa, escopo=unidade, papel=nomes.PAPEL).exists()
    )
    return [
        f"pessoa {FORMALIZACAO}: {'manter' if pessoa else 'criar'}",
        f"papel Formalização em {unidade}: {'manter' if com_o_papel else 'conceder'}",
    ]


def _designacoes_da_rodada(processo):
    """As designações vigentes em **todos** os Editais do Processo da rodada (FR-6726).

    Todos, e não só os que a restauração cancela: o Edital encerrado continua designável (a
    FR-3710 da `117`) e a lista do setor não filtra por estado — a designação que ficasse nele
    mostraria o Edital velho ao lado do novo. E de qualquer cenário, e não só do C16 e do C17: com
    a designação feita pela tela, num cenário de convocação, o caso é o mesmo.
    """
    from processo_seletivo.formalizacao.domain.autorizacao import designacoes_vigentes

    return designacoes_vigentes().filter(edital__processo=processo).order_by("id")


def _revogar_designacoes(processo, unidade, motivo, correlacao):
    """As designações vigentes da rodada anterior, revogadas com motivo (FR-6726).

    Pelo comando da `117`, e não por exclusão: a designação fica no histórico do Edital, e a lista
    do setor deixa de oferecê-lo.
    """
    from processo_seletivo.formalizacao.application.designar import revogar

    for designacao in _designacoes_da_rodada(processo):
        revogar(
            ator(ACESSOS, unidade),
            designacao_id=designacao.id,
            motivo=motivo,
            now=timezone.now(),
            correlation_id=correlacao,
        )


def _correio_inerte():
    """Nenhuma mensagem sai durante a montagem (FR-4634).

    A inscrição manda comprovante e a convocação comunica: são os comandos da aplicação, e eles
    enviam. O correio de memória do Django guarda a mensagem no processo e a descarta com ele; o
    domínio `.test` das pessoas fictícias é a segunda barreira, para o que escapasse disto.
    """
    return override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")


def _recusar_atraso_que_nao_cabe(cenario, unidade, autoridade_id, dias_atras):
    """O que o relógio atrasado não pode produzir, dito antes de montar qualquer coisa.

    **Estado inicial que nasce vencido**: a validade do cenário conta do instante da montagem, e
    com o relógio atrasado esse instante é o atrasado — um C08 montado há seis dias nasce com a
    janela recursal de cinco já fechada, e o exercício dele é recorrer.

    **Autoridade que ainda não era vigente**: os atos são assinados no instante atrasado, e a
    autoridade cadastrada depois dele não podia assiná-los. A publicação recusaria no meio da
    montagem, com uma frase sobre vigência que não diz que a causa é o atraso.
    """
    from processo_seletivo.shared.tempo import ZONA
    from processo_seletivo.unidades.application.selectors import autoridades_vigentes

    if dias_atras < 0:
        raise Recusa("--dias-atras não aceita número negativo: o gerador não monta no futuro.")
    if not dias_atras:
        return
    if cenario.validade_dias is not None and dias_atras >= cenario.validade_dias:
        raise Recusa(
            f"{cenario.codigo}: o estado inicial vale {cenario.validade_dias} dia(s), e montado "
            f"há {dias_atras} ele nasceria vencido. Use um atraso menor, ou nenhum."
        )
    naquele_dia = (timezone.now() - timedelta(days=dias_atras)).astimezone(ZONA).date()
    if not any(
        str(autoridade.pk) == str(autoridade_id)
        for autoridade in autoridades_vigentes(unidade, naquele_dia)
    ):
        raise Recusa(
            f"{cenario.codigo}: a autoridade que assina os atos não era vigente em "
            f"{naquele_dia:%d/%m/%Y}, {dias_atras} dia(s) atrás. Use um atraso menor, ou escolha "
            "com --autoridade uma que já fosse vigente naquele dia."
        )


def montar(
    cenario, unidade, *, rodada, autoridade_id, saida=None, por="linha de comando", dias_atras=0
):
    """Uma rodada nova do cenário, inteira ou nenhuma, com o manifesto na mesma transação.

    `dias_atras` monta o cenário como se ele tivesse ocorrido há N dias, pelo mesmo relógio do
    `seed_demo`: os comandos e as aferições são os de sempre, e só o instante é outro. Serve para
    que o que depende de prazo já decorrido — o definitivo depois da janela recursal, a vaga não
    preenchida, o encerramento — possa ser exercitado no dia da carga. **O manifesto leva o
    instante atrasado**: a validade do estado inicial conta de quando os atos ocorreram.
    """
    _recusar_atraso_que_nao_cabe(cenario, unidade, autoridade_id, dias_atras)
    with relogio_atrasado(dias_atras):
        return _montar(cenario, unidade, rodada, autoridade_id, saida, por, dias_atras)


def _montar(cenario, unidade, rodada, autoridade_id, saida, por, dias_atras):
    conflitos = conflitos_de_montagem(cenario, unidade, rodada, ano_local())
    if conflitos:
        raise Recusa(f"{cenario.codigo}: " + " ".join(conflitos))
    with _correio_inerte(), transaction.atomic():
        montagem = Montagem(
            codigo=cenario.codigo,
            rodada=rodada,
            unidade=unidade,
            autoridade_id=autoridade_id,
            titulo=cenario.nome,
            saida=saida,
        )
        cenario.montar(montagem)
        processo = ProcessoSeletivo.objects.get(pk=montagem.processo.id)
        return CenarioDeTreinamento.objects.create(
            unidade=unidade,
            codigo=cenario.codigo,
            rodada=rodada,
            versao_da_definicao=cenario.versao,
            processo=processo,
            correlation_id=montagem.correlacao,
            registros=montagem.registros,
            retrato=retratar(processo),
            banco=ambiente.banco_conectado(),
            criado_em=timezone.now(),
            criado_por=f"{por}, há {dias_atras} dia(s)" if dias_atras else por,
        )


def carregar(
    codigos,
    unidade,
    *,
    saida=None,
    erros=None,
    por="linha de comando",
    autoridade=None,
    dias_atras=0,
):
    """Cria só os cenários que não existem; relata e pula os demais (FR-4611).

    **A recusa do domínio e o defeito do gerador saem diferentes.** Os dois desfazem o cenário e
    deixam os outros seguirem (FR-4612), mas só a recusa é a regra funcionando: o defeito sai como
    `ERRO`, com a pilha em `erros`, para que ninguém o leia como frase do domínio.
    """
    resultados = []
    plano = planejar(codigos, unidade)
    autoridade_id = None
    for cenario, decisao, motivos in plano:
        if decisao != "CRIAR":
            resultados.append((cenario, decisao, motivos))
            continue
        autoridade_id = autoridade_id or autoridade_vigente(unidade, autoridade)
        if saida is not None:
            saida.write(f"{cenario.codigo} — {cenario.nome}")
        try:
            manifesto = montar(
                cenario,
                unidade,
                rodada=_proxima_rodada(cenario, unidade),
                autoridade_id=autoridade_id,
                saida=saida,
                por=por,
                dias_atras=dias_atras,
            )
        except (DomainError, Recusa) as erro:
            resultados.append((cenario, "FALHOU", [_frase(erro)]))
            continue
        except Exception as erro:  # noqa: BLE001 — um defeito não impede os outros cenários
            if erros is not None:
                erros.write(f"{cenario.codigo}: " + "".join(traceback.format_exception(erro)))
            resultados.append(
                (
                    cenario,
                    "ERRO",
                    [
                        f"defeito do gerador ({erro.__class__.__name__}: {erro}); a pilha está "
                        "na saída de erros. Nada deste cenário foi gravado."
                    ],
                )
            )
            continue
        resultados.append(
            (
                cenario,
                "CRIADO",
                [f"rodada {manifesto.rodada}", manifesto.processo.institutional_code],
            )
        )
    return resultados


def _frase(erro):
    codigo = getattr(erro, "code", "") or erro.__class__.__name__
    detalhe = getattr(erro, "detail", None) or str(erro)
    return f"{codigo}: {detalhe}. Nada deste cenário foi gravado."


def plano_de_restauracao(codigo, unidade):
    """O que a restauração fará — e as recusas, antes de qualquer escrita (FR-4620 a FR-4623)."""
    cenario = escolher([codigo])[0]
    atual = situacao(cenario, unidade)
    if atual.manifesto is None:
        raise Recusa(
            f"{cenario.codigo} não tem rodada registrada nesta unidade: use "
            "carregar_cenarios_de_treinamento para criá-lo."
        )
    if atual.problemas:
        raise Recusa(
            f"{cenario.codigo}: a propriedade do Processo não se comprova — "
            + " ".join(atual.problemas)
            + " Nada foi alterado; examine o Processo antes de decidir."
        )
    rodada = _proxima_rodada(cenario, unidade)
    conflitos = conflitos_de_montagem(cenario, unidade, rodada, ano_local())
    if conflitos:
        raise Recusa(f"{cenario.codigo}: " + " ".join(conflitos))
    processo = atual.manifesto.processo
    editais = _editais_a_cancelar(processo)
    return {
        "cenario": cenario,
        "manifesto": atual.manifesto,
        "rodada_nova": rodada,
        "a_cancelar": editais,
        "processo_a_cancelar": processo
        if processo.status
        not in (ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO)
        else None,
        "mudancas": atual.mudancas,
        "designacoes_a_revogar": _designacoes_da_rodada(processo).count(),
    }


def _editais_a_cancelar(processo, *, travar=False):
    """Os Editais fora de estado final. Sob trava, o Processo primeiro e os Editais por id — a
    ordem dos comandos de finalização, para não abrir caminho a impasse com eles."""
    editais = Edital.objects.filter(processo=processo).exclude(
        status__in=[Edital.Status.ENCERRADO, Edital.Status.CANCELADO]
    )
    if travar:
        ProcessoSeletivo.objects.select_for_update().get(pk=processo.pk)
        editais = editais.select_for_update()
    return list(editais.order_by("id"))


def restaurar(plano, unidade, *, saida=None, por="linha de comando", autoridade=None, dias_atras=0):
    """A rodada nova e o cancelamento da anterior, na mesma transação (FR-4624, FR-4625).

    **Recebe o plano que o comando mostrou, e não o refaz.** O que muda entre mostrar e gravar é
    relido sob trava, dentro da transação: o manifesto, que outra restauração pode ter trocado, e
    os Editais a cancelar — um Edital que a equipe criasse no Processo depois da pré-visualização
    ficava fora da lista, e o cancelamento do Processo recusava a restauração inteira.
    """
    from processo_seletivo.processos.application.finalizacao import cancel_edital, cancel_process

    cenario, anterior = plano["cenario"], plano["manifesto"]
    autoridade_id = autoridade_vigente(unidade, autoridade)
    # **Só a rodada nova nasce atrasada.** O cancelamento da anterior é ato de agora: datado de
    # dias atrás, ele precederia o que a equipe fez nela ontem.
    with _correio_inerte(), transaction.atomic():
        # A anterior sai de PRONTO **antes** de a nova nascer: a constraint de uma rodada em uso por
        # cenário recusaria as duas juntas — e é ela que garante que nunca convivam. O filtro por
        # PRONTO é a trava otimista: se outra restauração passou na frente, nada muda aqui.
        trocadas = CenarioDeTreinamento.objects.filter(
            pk=anterior.pk, situacao=CenarioDeTreinamento.Situacao.PRONTO
        ).update(
            situacao=CenarioDeTreinamento.Situacao.SUBSTITUIDO,
            substituido_em=timezone.now(),
        )
        if trocadas != 1:
            raise Recusa(
                f"{cenario.codigo}: a rodada {anterior.rodada} deixou de ser a rodada em uso "
                "desde a pré-visualização. Nada foi alterado; rode a restauração de novo."
            )
        novo = montar(
            cenario,
            unidade,
            rodada=plano["rodada_nova"],
            autoridade_id=autoridade_id,
            saida=saida,
            por=por,
            dias_atras=dias_atras,
        )
        CenarioDeTreinamento.objects.filter(pk=anterior.pk).update(substituido_por=novo)
        gestor = ator(GESTAO, unidade)
        motivo = (
            f"Cenário de treinamento {cenario.codigo} restaurado: substituído pela rodada "
            f"{novo.rodada} ({novo.processo.institutional_code}). {MARCA}."
        )
        correlacao = f"{anterior.correlation_id}-substituida"
        a_cancelar = _editais_a_cancelar(anterior.processo, travar=True)
        _revogar_designacoes(anterior.processo, unidade, motivo, correlacao)
        for edital in a_cancelar:
            cancel_edital(
                actor=gestor,
                edital_id=edital.id,
                expected_revision=edital.revision,
                reason=motivo,
                idempotency_key=f"{correlacao}-edital-{edital.id.hex[:12]}",
                correlation_id=correlacao,
            )
        processo = ProcessoSeletivo.objects.get(pk=anterior.processo_id)
        if processo.status not in (
            ProcessoSeletivo.Status.ENCERRADO,
            ProcessoSeletivo.Status.CANCELADO,
        ):
            cancel_process(
                actor=gestor,
                processo_id=processo.id,
                expected_revision=processo.revision,
                reason=motivo,
                idempotency_key=f"{correlacao}-processo",
                correlation_id=correlacao,
            )
    return anterior, novo
