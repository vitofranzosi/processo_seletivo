"""A conferência antes de publicar a agenda (167, US3, FR-7220 a FR-7223, T-010).

```text
exigir_base_de_comissao(ator, processo)    # sem a base, nada se lê (FR-7255)
  ↓
a Etapa e o período do Evento, relidos     # o cronograma vigente, e não o do dia da configuração
  ↓
a montagem: participação × agendamentos    # a mesma leitura da tela de montar
  ↓
impedimentos (contracts/recusas.md §4)     # cada um com o caminho de corrigir (UX-766)
  ↓
fatos, conteúdo público, mensagem, autoridades, assinatura
```

**Nada aqui grava, envia ou reserva** (FR-7220): a conferência é a resposta do próprio pedido, como
a da `140`. Recarregá-la recompõe tudo; nenhuma chave de idempotência é consumida.

**A publicação chama esta mesma função sob a trava** (`publicar.py`): os impedimentos e a
assinatura que ela confere são os que esta tela mostrou, calculados pelo mesmo código — e por isso
a conferência nunca diz "pode publicar" sobre o que a publicação recusaria.

**A assinatura** (T-010) é o resumo de `{revision, configuração, pares, participantes}`. A
`revision` sozinha não vê a participação que mudou sem tocar a agenda — um recurso deferido entre a
conferência e a confirmação —, e a configuração entra inteira, com o acesso e as orientações,
porque a mensagem que a tela mostra os leva.
"""

from dataclasses import dataclass, field

from django.utils import timezone

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.application.configurar import etapa_e_periodo
from processo_seletivo.agendamento.domain import conteudo as conteudo_
from processo_seletivo.agendamento.domain import mensagem, nomes, recusas
from processo_seletivo.agendamento.domain.configuracao import problemas
from processo_seletivo.agendamento.domain.horarios import (
    dia_por_extenso,
    periodo_por_extenso,
    zona,
)
from processo_seletivo.comissoes.application import exigir_base_de_comissao
from processo_seletivo.editais.domain.alcance import restrita
from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.unidades.application import selectors as unidades


@dataclass
class Prontidao:
    """Uma das quatro linhas do topo (04-redesign, decisão 2): `True`, `False` ou `None`."""

    pronta: bool | None
    texto: str

    @property
    def classe(self):
        return {True: "pronto", False: "pendente", None: "a-fazer"}[self.pronta]


@dataclass
class Conferencia:
    agenda: object
    etapa: dict
    montagem: object
    periodo: tuple | None
    impedimentos: list
    avisos: list
    fatos: list
    conteudo: dict
    mensagem_de_exemplo: dict | None
    autoridades: list
    assinatura: str
    prontidao: list = field(default_factory=list)

    @property
    def pode_publicar(self):
        return not self.impedimentos


def rotulo_do_edital(edital):
    return f"Edital {edital.number}/{edital.year}"


def _assinatura(agenda, configuracao, montagem):
    return canonical_sha256(
        {
            "revision": agenda.revision,
            "configuracao": {
                "forma": configuracao.forma,
                "duracao": configuracao.duracao,
                "intervalo": configuracao.intervalo,
                "dias": [
                    [dia.isoformat(), [[f"{i:%H:%M}", f"{f:%H:%M}"] for i, f in pares]]
                    for dia, pares in configuracao.dias
                ],
                "bancas": [
                    [banca.id, banca.nome, banca.acesso, banca.ordem]
                    for banca in configuracao.bancas
                ],
                "orientacoes": configuracao.orientacoes,
            },
            "pares": sorted(
                [str(item.inscricao_id), str(item.banca_id), item.inicio.isoformat()]
                for item in montagem.por_inscricao.values()
            ),
            "participantes": sorted(montagem.participacao.participantes),
        }
    )


def _impedimentos(agenda, configuracao, montagem, periodo, autoridades):
    lista = []
    if montagem.sem_horario:
        lista.append(recusas.participantes_sem_horario(montagem.sem_horario))
    for item, motivo in montagem.nao_participam:
        pessoa = leitura.pessoa_do_agendamento(item)
        lista.append(recusas.agendado_que_nao_participa(pessoa.nome, pessoa.protocolo, motivo))
    relidos = problemas(configuracao, periodo=periodo)
    if relidos:
        lista.append(recusas.configuracao_invalida(relidos))
    for banca in agenda.bancas_em_ordem:
        if not (banca.acesso or "").strip():
            lista.append(recusas.banca_sem_local(banca.nome, agenda.forma))
    if not autoridades:
        lista.append(recusas.sem_autoridade_vigente())
    return lista


def _fatos(etapa, agenda, configuracao, montagem, periodo):
    bancas = len(agenda.bancas_em_ordem)
    forma = "por videoconferência" if agenda.forma == nomes.REMOTA else "presencial"
    livres = len(montagem.livres)
    return [
        ("Etapa", etapa.get("name") or ""),
        (
            "Período no cronograma",
            periodo_por_extenso(periodo) if periodo else "sem período publicado",
        ),
        ("Dias da agenda", ", ".join(dia_por_extenso(dia) for dia, _ in configuracao.dias)),
        (
            "Atendimento",
            f"{agenda.duracao_minutos} minutos, com {agenda.intervalo_minutos} de intervalo · "
            f"{recusas.plural(bancas, 'banca', 'bancas')} · {forma}",
        ),
        (
            "Pessoas",
            f"{montagem.com_horario} de {montagem.participantes} com horário · "
            f"{recusas.plural(len(montagem.horarios), 'horário', 'horários')}, "
            f"{livres} {'fica livre' if livres == 1 else 'ficam livres'}",
        ),
    ]


def _prontidao(montagem, configuracao, periodo, agenda, autoridades):
    sem_local = any(not (banca.acesso or "").strip() for banca in agenda.bancas_em_ordem)
    falta = "endereço de sala" if agenda.forma == nomes.REMOTA else "local"
    dias_validos = not problemas(configuracao, periodo=periodo)
    return [
        Prontidao(
            not montagem.sem_horario and not montagem.nao_participam,
            f"{montagem.com_horario} de {montagem.participantes} com horário",
        ),
        Prontidao(
            dias_validos if periodo is not None else None,
            "Dias dentro do período do cronograma"
            if periodo is not None
            else "Etapa sem período no cronograma",
        ),
        Prontidao(not sem_local, f"Toda banca com {falta}"),
        Prontidao(
            None if autoridades else False,
            "Autoridade signatária, escolhida no fim da página"
            if autoridades
            else "Nenhuma autoridade signatária vigente",
        ),
    ]


def itens_publicos(montagem):
    """Os agendamentos de quem participa, como o conteúdo público os recebe: nome e protocolo."""
    nomes_das_bancas = {str(banca.id): banca.nome for banca in montagem.agenda.bancas_em_ordem}
    return [
        conteudo_.Item(
            inicio=item.inicio,
            fim=item.fim,
            banca=nomes_das_bancas.get(str(item.banca_id), item.banca.nome),
            nome=item.inscricao.nome or item.inscricao.protocolo or "",
            protocolo=item.inscricao.protocolo or "",
        )
        for item in montagem.por_inscricao.values()
        if str(item.inscricao_id) in montagem.participacao.participantes
    ]


def compor_conteudo(edital, etapa, agenda, montagem, *, publicado_em, signatario, veiculo, unidade):
    """O conteúdo público da agenda, para a prévia e para o ato — a mesma chamada (FR-7222)."""
    return conteudo_.compor(
        unidade=unidade,
        edital=rotulo_do_edital(edital),
        etapa=etapa.get("name") or "",
        publicado_em=publicado_em,
        signatario=signatario,
        veiculo=veiculo,
        forma=agenda.forma,
        duracao=agenda.duracao_minutos,
        bancas=[(banca.nome, banca.acesso) for banca in agenda.bancas_em_ordem],
        itens=itens_publicos(montagem),
        restrita=restrita(etapa),
    )


def _unidade(unidade):
    if unidade is None:
        return None
    return {
        "cabecalho": list(unidade.cabecalho),
        "local": unidade.local,
        "sigla": unidade.sigla,
        "nome": unidade.nome,
    }


def _mensagem_de_exemplo(edital, etapa, agenda, montagem):
    """A mensagem da primeira pessoa da agenda, como sairá (FR-7222): a do horário mais cedo."""
    primeiro = next(
        (
            item
            for item in sorted(
                montagem.por_inscricao.values(), key=lambda i: (i.inicio, i.banca.ordem)
            )
            if str(item.inscricao_id) in montagem.participacao.participantes
        ),
        None,
    )
    if primeiro is None:
        return None
    nome_da_etapa = etapa.get("name") or "Etapa"
    return {
        "assunto": mensagem.assunto(nome_da_etapa, rotulo_do_edital(edital)),
        "corpo": mensagem.corpo(
            nome=primeiro.inscricao.nome or "",
            protocolo=primeiro.inscricao.protocolo or "",
            etapa=nome_da_etapa,
            edital=rotulo_do_edital(edital),
            inicio=primeiro.inicio,
            duracao=agenda.duracao_minutos,
            banca=primeiro.banca.nome,
            forma=agenda.forma,
            acesso=primeiro.banca.acesso,
            orientacoes=agenda.orientacoes,
            varias=len(agenda.bancas_em_ordem) > 1,
        ),
    }


def conferencia_sob(edital, etapa_id, agenda, *, agora=None):
    """A conferência de uma agenda já lida — e, na publicação, já travada."""
    agora = agora or timezone.now()
    etapa, periodo = etapa_e_periodo(edital, etapa_id)
    configuracao = leitura.configuracao_da_agenda(agenda)
    montagem = leitura.montagem(edital, etapa_id, agenda)
    unidade = unidades.unidade(edital.institution_scope)
    autoridades = (
        unidades.autoridades_vigentes(unidade.codigo, agora.astimezone(zona()).date())
        if unidade is not None
        else []
    )
    conteudo = compor_conteudo(
        edital,
        etapa,
        agenda,
        montagem,
        publicado_em=None,
        signatario=None,
        veiculo="",
        unidade=_unidade(unidade),
    )
    return Conferencia(
        agenda=agenda,
        etapa=etapa,
        montagem=montagem,
        periodo=periodo,
        impedimentos=_impedimentos(agenda, configuracao, montagem, periodo, autoridades),
        avisos=[] if periodo is not None else [recusas.ETAPA_SEM_EVENTO],
        fatos=_fatos(etapa, agenda, configuracao, montagem, periodo),
        conteudo=conteudo,
        mensagem_de_exemplo=_mensagem_de_exemplo(edital, etapa, agenda, montagem),
        autoridades=autoridades,
        assinatura=_assinatura(agenda, configuracao, montagem),
        prontidao=_prontidao(montagem, configuracao, periodo, agenda, autoridades),
    )


def conferencia(*, actor, edital, etapa_id):
    """A conferência, sem gravar nada (FR-7220). Sem agenda, a recusa da montagem."""
    exigir_base_de_comissao(actor=actor, processo_id=edital.processo_id)
    agenda = leitura.agenda_da_etapa(edital, etapa_id)
    if agenda is None:
        raise recusas.sem_configuracao()
    return conferencia_sob(edital, etapa_id, agenda)
