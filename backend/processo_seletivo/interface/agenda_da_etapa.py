"""As telas da agenda da Etapa na gestão: configurar e montar (167, entrega A, T-020, T-021).

**A porta é a da Distribuição**, `views._etapa_para_distribuir`, chamada daqui e não copiada
(T-021): o Edital fora do escopo é 404, sem a base da gestão da comissão é a recusa da gramática das
portas, e a Etapa ausente da versão vigente é 404. Os comandos repetem a base no domínio, porque a
tela não é a única porta (FR-7255).

**Servidor e htmx, nenhum JavaScript novo** (T-006, UX-767). O simulador da configuração é um
fragmento que o htmx pede a cada campo digitado, sem gravar; os atalhos, o "+ janela", o "+ dia" e o
"+ banca" devolvem o formulário acrescido, também sem gravar. Sem script, os mesmos botões enviam o
formulário inteiro e a página volta com o acréscimo — a tela continua funcionando.

**O htmx não troca resposta 4xx**: o fragmento recusado volta 200 com `HX-Retarget`. A página
inteira recusada volta com o status da recusa, como as telas de composição.

**A grade é o que se vê; o painel é onde se age** (04-redesign, decisão 5). Cada célula é um link
para a própria montagem com a pessoa ou o horário escolhido — que o htmx intercepta e troca só o
painel —, e o painel tem os formulários. Nenhum texto de ação se repete pela grade (UX-761), e tudo
se faz sem arrastar (UX-762).
"""

import re
from datetime import date, datetime, time
from uuid import UUID

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.agendamento.application import configurar as configurar_app
from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.application import montar as montar_app
from processo_seletivo.agendamento.domain import capacidade as capacidade_
from processo_seletivo.agendamento.domain.configuracao import problemas
from processo_seletivo.agendamento.domain.horarios import (
    Banca,
    Configuracao,
    derivar,
    dia_curto,
    dia_por_extenso,
    hora,
    periodo_por_extenso,
    zona,
)
from processo_seletivo.agendamento.domain.preenchimento import ORDEM
from processo_seletivo.agendamento.domain.recusas import (
    ConfiguracaoRecusada,
    completa,
    nao_participa_mais,
)
from processo_seletivo.interface import identidade
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada

MANHA_E_TARDE = (("08:00", "12:00"), ("13:00", "17:00"))
MENSAGEM = "mensagem_da_agenda"


def _porta(request, edital_id, etapa_id):
    from processo_seletivo.interface import views

    return views._etapa_para_distribuir(request, edital_id, etapa_id)


def _inexistente():
    """O 404 desta tela, num lugar só (inventário da `033`): a pessoa, o horário ou a Etapa que a
    rota nomeia e que não existe — ou que o domínio recusou como inexistente, sem dizer se existe
    noutro escopo. A autorização não passa por aqui: é a porta da Distribuição que a decide."""
    raise Http404


def _htmx(request):
    return request.headers.get("HX-Request") == "true"


# --- o formulário da configuração ----------------------------------------------------------------


def _numero(texto):
    try:
        return int((texto or "").strip())
    except ValueError:
        return None


def _hora(texto):
    try:
        return time.fromisoformat((texto or "").strip())
    except ValueError:
        return None


def _data(texto):
    try:
        return date.fromisoformat((texto or "").strip())
    except ValueError:
        return None


class Formulario:
    """O formulário como foi digitado, com os textos crus para voltar à tela, e a `Configuracao`.

    Os textos ficam crus porque a recusa devolve a tela com o que a pessoa escreveu, e não com o
    que o sistema conseguiu entender (UX-766). A `Configuracao` é o valor que o domínio julga.
    """

    def __init__(self, *, forma, duracao, intervalo, orientacoes, dias, bancas):
        self.forma = forma
        self.duracao = duracao
        self.intervalo = intervalo
        self.orientacoes = orientacoes
        self.dias = dias  # [{"dia": "2026-11-23", "janelas": [("08:00", "12:00"), …]}]
        self.bancas = bancas  # [{"id": "…", "nome": "…", "acesso": "…"}]

    @classmethod
    def do_post(cls, dados):
        indices_de_dia = sorted(
            {int(m.group(1)) for chave in dados if (m := re.fullmatch(r"dia-(\d+)", chave))}
        )
        dias = []
        for i in indices_de_dia:
            ks = sorted(
                {
                    int(m.group(1))
                    for chave in dados
                    if (m := re.fullmatch(rf"dia-{i}-janela-(\d+)-inicio", chave))
                }
            )
            dias.append(
                {
                    "dia": dados.get(f"dia-{i}", ""),
                    "janelas": [
                        (
                            dados.get(f"dia-{i}-janela-{k}-inicio", ""),
                            dados.get(f"dia-{i}-janela-{k}-fim", ""),
                        )
                        for k in ks
                    ],
                }
            )
        indices_de_banca = sorted(
            {int(m.group(1)) for chave in dados if (m := re.fullmatch(r"banca-(\d+)-nome", chave))}
        )
        bancas = [
            {
                "id": dados.get(f"banca-{j}-id", ""),
                "nome": dados.get(f"banca-{j}-nome", ""),
                "acesso": dados.get(f"banca-{j}-acesso", ""),
            }
            for j in indices_de_banca
        ]
        forma = dados.get("forma") if dados.get("forma") in ("REMOTA", "PRESENCIAL") else "REMOTA"
        return cls(
            forma=forma,
            duracao=dados.get("duracao", ""),
            intervalo=dados.get("intervalo", ""),
            orientacoes=dados.get("orientacoes", ""),
            dias=dias,
            bancas=bancas,
        )

    @classmethod
    def da_agenda(cls, agenda):
        configuracao = leitura.configuracao_da_agenda(agenda)
        return cls.da_configuracao(configuracao)

    @classmethod
    def da_configuracao(cls, configuracao):
        return cls(
            forma=configuracao.forma,
            duracao=str(configuracao.duracao or ""),
            intervalo=str(configuracao.intervalo if configuracao.intervalo is not None else ""),
            orientacoes=configuracao.orientacoes,
            dias=[
                {
                    "dia": dia.isoformat() if dia else "",
                    "janelas": [(f"{i:%H:%M}", f"{f:%H:%M}") for i, f in pares],
                }
                for dia, pares in configuracao.dias
            ],
            bancas=[
                {
                    "id": "" if str(b.id).startswith("nova-") else str(b.id),
                    "nome": b.nome,
                    "acesso": b.acesso,
                }
                for b in configuracao.bancas
            ],
        )

    @classmethod
    def sugerido(cls, periodo):
        """O ponto de partida do protótipo aprovado: um dia, manhã e tarde, uma banca."""
        return cls(
            forma="REMOTA",
            duracao="10",
            intervalo="5",
            orientacoes="",
            dias=[
                {
                    "dia": periodo[0].isoformat() if periodo else "",
                    "janelas": list(MANHA_E_TARDE),
                }
            ],
            bancas=[{"id": "", "nome": "Banca 1", "acesso": ""}],
        )

    def configuracao(self):
        return Configuracao(
            forma=self.forma,
            duracao=_numero(self.duracao),
            intervalo=_numero(self.intervalo) if (self.intervalo or "").strip() else 0,
            dias=tuple(
                (
                    _data(item["dia"]),
                    tuple(
                        (_hora(inicio), _hora(fim))
                        for inicio, fim in item["janelas"]
                        if (inicio or "").strip() or (fim or "").strip()
                    ),
                )
                for item in self.dias
                if (item["dia"] or "").strip()
            ),
            bancas=tuple(
                Banca(banca["id"] or f"nova-{j + 1}", banca["nome"], banca["acesso"], j + 1)
                for j, banca in enumerate(self.bancas)
            ),
            orientacoes=self.orientacoes,
        )

    def aplicar(self, acao, *, periodo, participantes):
        """O gesto que muda o formulário sem gravar: atalho, acréscimo, remoção."""
        if acao.startswith("atalho-"):
            atual = self.configuracao()
            codigo = acao.removeprefix("atalho-")
            if codigo == capacidade_.ACRESCENTAR_DIA:
                dia = capacidade_.proximo_dia(atual, periodo)
                if dia is not None:
                    modelo = self.dias[-1]["janelas"] if self.dias else list(MANHA_E_TARDE)
                    self.dias.append({"dia": dia.isoformat(), "janelas": list(modelo)})
            elif codigo == capacidade_.ACRESCENTAR_BANCA:
                nova = capacidade_.com_banca(atual).bancas[-1]
                self.bancas.append({"id": "", "nome": nova.nome, "acesso": ""})
            elif codigo == capacidade_.TIRAR_O_INTERVALO:
                self.intervalo = "0"
        elif acao == "acrescentar-dia":
            dia = capacidade_.proximo_dia(self.configuracao(), periodo)
            modelo = self.dias[-1]["janelas"] if self.dias else list(MANHA_E_TARDE)
            self.dias.append({"dia": dia.isoformat() if dia else "", "janelas": list(modelo)})
        elif acao == "acrescentar-banca":
            nova = capacidade_.com_banca(self.configuracao()).bancas[-1]
            self.bancas.append({"id": "", "nome": nova.nome, "acesso": ""})
        elif m := re.fullmatch(r"acrescentar-janela-(\d+)", acao):
            i = int(m.group(1))
            if i < len(self.dias):
                self.dias[i]["janelas"].append(("", ""))
        elif m := re.fullmatch(r"remover-janela-(\d+)-(\d+)", acao):
            i, k = int(m.group(1)), int(m.group(2))
            if i < len(self.dias) and k < len(self.dias[i]["janelas"]):
                del self.dias[i]["janelas"][k]
        elif m := re.fullmatch(r"remover-dia-(\d+)", acao):
            i = int(m.group(1))
            if i < len(self.dias):
                del self.dias[i]
        elif m := re.fullmatch(r"remover-banca-(\d+)", acao):
            j = int(m.group(1))
            if j < len(self.bancas):
                del self.bancas[j]

    def linhas_de_dia(self, configuracao):
        """Cada dia com o rótulo e quantos horários ele dá — o número ao lado da linha."""
        por_dia = {}
        for horario in derivar(configuracao):
            por_dia[horario.dia] = por_dia.get(horario.dia, 0) + 1
        linhas = []
        for i, item in enumerate(self.dias):
            dia = _data(item["dia"])
            linhas.append(
                {
                    "indice": i,
                    "dia": item["dia"],
                    "rotulo": dia_curto(dia) if dia else f"Dia {i + 1}",
                    "janelas": [
                        {"indice": k, "inicio": inicio, "fim": fim}
                        for k, (inicio, fim) in enumerate(item["janelas"])
                    ],
                    "horarios": por_dia.get(dia, 0) if dia else 0,
                }
            )
        return linhas


def _simulador(edital, etapa_id, formulario, periodo, participacao):
    configuracao = formulario.configuracao()
    lista = problemas(configuracao, periodo=periodo)
    participantes = len(participacao.participantes)
    calculo = capacidade_.calcular(
        configuracao, participantes, lista_aberta=participacao.lista_aberta
    )
    return {
        "problemas": lista,
        "capacidade": calculo,
        "atalhos": [] if lista else capacidade_.atalhos(configuracao, participantes, periodo),
        "largura": f"largura-{calculo.taxa}",
    }


def _contexto_da_configuracao(edital, etapa, etapa_id, formulario, periodo, participacao, agenda):
    configuracao = formulario.configuracao()
    return {
        "edital": edital,
        "processo": edital.processo,
        "etapa": etapa,
        "etapa_id": etapa_id,
        "formulario": formulario,
        "dias": formulario.linhas_de_dia(configuracao),
        "periodo": periodo,
        "periodo_por_extenso": periodo_por_extenso(periodo) if periodo else "",
        "agenda": agenda,
        "remota": formulario.forma == "REMOTA",
        **_simulador(edital, etapa_id, formulario, periodo, participacao),
    }


@require_http_methods(["GET", "POST"])
def configurar(request, edital_id, etapa_id):
    """O formulário e o simulador (US1, UX-760, UX-766). POST grava ou recusa a lista inteira."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    periodo = leitura.periodo_da_etapa(edital, etapa)
    agenda = leitura.agenda_da_etapa(edital, etapa_id)
    participacao = leitura.participacao(edital, etapa_id)
    status = 200
    erro = None
    if request.method == "POST":
        formulario = Formulario.do_post(request.POST)
        acao = request.POST.get("acao", "")
        if acao and acao != "salvar":
            formulario.aplicar(acao, periodo=periodo, participantes=len(participacao.participantes))
        else:
            try:
                salva = configurar_app.salvar(
                    actor=ator,
                    edital=edital,
                    etapa_id=etapa_id,
                    configuracao=formulario.configuracao(),
                    correlation_id=getattr(request, "correlation_id", ""),
                )
            except ConfiguracaoRecusada as recusa:
                erro = recusa
                status = recusa.status
            except DomainError as recusa:
                if recusa.status == 404:
                    raise _inexistente() from recusa
                erro = recusa
                status = recusa.status
            else:
                request.session[MENSAGEM] = {"tipo": "sucesso", "texto": salva.frase}
                return redirect("interface:agenda-montar", edital.id, etapa_id)
    elif agenda is not None:
        formulario = Formulario.da_agenda(agenda)
    else:
        formulario = Formulario.sugerido(periodo)
    contexto = _contexto_da_configuracao(
        edital, etapa, etapa_id, formulario, periodo, participacao, agenda
    )
    contexto["erro"] = erro
    if _htmx(request):
        # O acréscimo sem gravar troca só o formulário: a página não pisca e o foco fica perto.
        return marcar_como_privada(
            render(request, "interface/_agenda_formulario.html", contexto, status=200)
        )
    return marcar_como_privada(
        render(request, "interface/agenda_configurar.html", contexto, status=status)
    )


@require_http_methods(["POST"])
def capacidade(request, edital_id, etapa_id):
    """O fragmento do simulador, a cada campo digitado. **Nunca grava** (FR-7205, UX-760)."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    periodo = leitura.periodo_da_etapa(edital, etapa)
    formulario = Formulario.do_post(request.POST)
    contexto = {
        "edital": edital,
        "etapa_id": etapa_id,
        **_simulador(edital, etapa_id, formulario, periodo, leitura.participacao(edital, etapa_id)),
    }
    resposta = render(request, "interface/_agenda_capacidade.html", contexto)
    if contexto["problemas"]:
        # A configuração recusada é a resposta, e não um erro de rede: 200, e o alvo dito (T-006).
        resposta["HX-Retarget"] = "#calculo"
    return marcar_como_privada(resposta)


# --- a montagem ----------------------------------------------------------------------------------


def _chave_do_horario(texto):
    """`<banca>@<início ISO>` → `(banca, instante)`, ou `None`."""
    banca, _, inicio = (texto or "").partition("@")
    try:
        return (str(UUID(banca)), datetime.fromisoformat(inicio))
    except ValueError:
        return None


def _texto_do_horario(horario):
    return f"{horario.banca_id}@{horario.inicio.isoformat()}"


def _grade(montagem, dia, *, escolhido=None):
    """As linhas da grade do dia: uma por início, uma célula por banca (UX-761)."""
    bancas = list(montagem.agenda.bancas_em_ordem)
    nomes = {str(banca.id): banca.nome for banca in bancas}
    linhas = {}
    for horario in montagem.horarios_no_dia(dia):
        ocupante = montagem.ocupados.get(horario.chave)
        linhas.setdefault(horario.inicio, []).append(
            {
                "horario": horario,
                "chave": _texto_do_horario(horario),
                "banca": nomes.get(horario.banca_id, ""),
                "agendamento": ocupante,
                "nao_participa": ocupante is not None
                and str(ocupante.inscricao_id) not in montagem.participacao.participantes,
                "escolhido": escolhido is not None and escolhido == horario.chave,
            }
        )
    return [
        {"hora": hora(inicio), "celulas": celulas} for inicio, celulas in sorted(linhas.items())
    ]


def _abas(montagem, dia_atual):
    return [
        {
            "dia": dia.isoformat(),
            "rotulo": dia_curto(dia),
            "ocupados": montagem.ocupados_no_dia(dia),
            "total": len(montagem.horarios_no_dia(dia)),
            "atual": dia == dia_atual,
        }
        for dia in montagem.dias
    ]


def _seletor(montagem, dia_pedido):
    """O seletor de horário: dia em botões, horários livres por banca (04-redesign, decisão 6)."""
    livres = montagem.livres
    por_dia = {}
    for horario in livres:
        por_dia.setdefault(horario.dia, []).append(horario)
    dias = sorted(por_dia)
    if not dias:
        return None
    dia = dia_pedido if dia_pedido in por_dia else dias[0]
    bancas = list(montagem.agenda.bancas_em_ordem)
    grupos = []
    for banca in bancas:
        opcoes = [h for h in por_dia[dia] if h.banca_id == str(banca.id)]
        if opcoes:
            grupos.append(
                {
                    "nome": banca.nome if len(bancas) > 1 else "Horários livres",
                    "opcoes": [
                        {"valor": _texto_do_horario(h), "hora": hora(h.inicio)} for h in opcoes
                    ],
                }
            )
    return {
        "dias": [
            {
                "dia": d.isoformat(),
                "rotulo": dia_curto(d),
                "livres": len(por_dia[d]),
                "atual": d == dia,
            }
            for d in dias
        ],
        "grupos": grupos,
        "dia": dia,
    }


def _painel(request, edital, etapa_id, montagem, *, previa=None, erro_da_previa=None):
    """O estado do painel de ação: a pessoa, o horário livre, a prévia, ou a lista (UX-762)."""
    dia_do_seletor = _data(request.GET.get("seletor") or "")
    if previa is not None:
        return _contexto_da_previa(montagem, previa, erro_da_previa)
    pessoa_id = request.GET.get("pessoa")
    if pessoa_id:
        try:
            UUID(pessoa_id)
        except ValueError:
            raise _inexistente() from None
        agendamento = montagem.por_inscricao.get(pessoa_id)
        if agendamento is not None:
            pessoa = leitura.pessoa_do_agendamento(agendamento)
        else:
            pessoa = next((p for p in montagem.sem_horario if p.inscricao_id == pessoa_id), None)
        if pessoa is None:
            raise _inexistente()
        motivo = (
            montagem.participacao.motivo(pessoa_id)
            if pessoa_id not in montagem.participacao.participantes
            else ""
        )
        return {
            "tipo": "pessoa",
            "pessoa": pessoa,
            "agendamento": agendamento,
            "agora": _rotulo_longo(agendamento.inicio, agendamento.banca.nome, montagem)
            if agendamento
            else "",
            "motivo": motivo,
            "seletor": None
            if motivo
            else _seletor(
                montagem,
                dia_do_seletor
                or (agendamento.inicio.astimezone(zona()).date() if agendamento else None),
            ),
        }
    horario_texto = request.GET.get("horario")
    if horario_texto:
        chave = _chave_do_horario(horario_texto)
        horario = next((h for h in montagem.horarios if chave and h.chave == chave), None)
        if horario is None or horario.chave in montagem.ocupados:
            # O horário sumiu ou foi ocupado nesse meio-tempo: o painel volta à lista, e a grade o
            # mostra como está.
            return _contexto_da_lista(request, montagem)
        busca = (request.GET.get("busca") or "").strip()
        nomes = {str(banca.id): banca.nome for banca in montagem.agenda.bancas_em_ordem}
        return {
            "tipo": "horario",
            "horario": horario,
            "valor": _texto_do_horario(horario),
            "titulo": f"{hora(horario.inicio)} · {dia_curto(horario.dia)}",
            "banca": nomes.get(horario.banca_id, ""),
            "fim": hora(horario.fim),
            "busca": busca,
            "pessoas": _filtrar(montagem.sem_horario, busca),
            "ha_sem_horario": bool(montagem.sem_horario),
        }
    return _contexto_da_lista(request, montagem)


def _filtrar(pessoas, busca):
    from processo_seletivo.shared.texto import dobrar

    if not busca:
        return list(pessoas)
    alvo = dobrar(busca)
    return [p for p in pessoas if alvo in dobrar(p.nome) or alvo in dobrar(p.protocolo)]


def _contexto_da_lista(request, montagem):
    busca = (request.GET.get("busca") or "").strip()
    return {
        "tipo": "lista",
        "busca": busca,
        "pessoas": _filtrar(montagem.sem_horario, busca),
        "sem_horario": len(montagem.sem_horario),
        "nao_participam": [
            {
                "pessoa": leitura.pessoa_do_agendamento(item),
                "frase": nao_participa_mais(leitura.pessoa_do_agendamento(item).nome, motivo),
                "horario": _rotulo_longo(item.inicio, item.banca.nome, montagem),
            }
            for item, motivo in montagem.nao_participam
        ],
        "completa": completa(montagem.participantes)
        if montagem.participantes and not montagem.sem_horario
        else "",
    }


def _rotulo_longo(inicio, banca, montagem):
    local = inicio.astimezone(zona())
    texto = f"{dia_por_extenso(local.date())}, {hora(local)}"
    return f"{texto} · {banca}" if len(montagem.agenda.bancas_em_ordem) > 1 else texto


def _contexto_da_previa(montagem, previa, erro):
    proposta = previa.proposta
    bancas = list(montagem.agenda.bancas_em_ordem)
    dias = sorted({dia for dia, _ in proposta.por_dia_e_banca})
    nomes = {str(banca.id): banca.nome for banca in bancas}
    return {
        "tipo": "previa",
        "erro": erro,
        "proposta": proposta,
        "assinatura": previa.assinatura,
        "bancas": [banca.nome for banca in bancas],
        "tabela": [
            {
                "dia": dia_curto(dia),
                "numeros": [proposta.por_dia_e_banca.get((dia, str(b.id)), 0) for b in bancas],
            }
            for dia in dias
        ],
        "livres": len(proposta.livres),
        "ordem": ORDEM,
        "relacao": [
            {
                "horario": f"{dia_curto(h.dia)}, {hora(h.inicio)}"
                + (f" · {nomes.get(h.banca_id, '')}" if len(bancas) > 1 else ""),
                "nome": pessoa.nome,
                "protocolo": pessoa.protocolo,
            }
            for pessoa, h in proposta.pares
        ],
    }


def _resumo(montagem):
    participantes = montagem.participantes
    com_horario = montagem.com_horario
    horarios = len(montagem.horarios)
    taxa = 100 if not participantes else min(100, round(100 * com_horario / participantes))
    return {
        "participantes": participantes,
        "com_horario": com_horario,
        "sem_horario": len(montagem.sem_horario),
        "horarios": horarios,
        "falta": max(participantes - horarios, 0),
        "sobra": max(horarios - participantes, 0),
        "taxa": taxa,
        "largura": f"largura-{taxa}",
        "completo": participantes > 0 and not montagem.sem_horario,
        "livres": len(montagem.livres),
    }


def _contexto_da_montagem(request, edital, etapa, etapa_id, montagem, *, painel=None):
    dia = leitura.dia_valido(request.GET.get("dia"), montagem.dias)
    painel = painel or _painel(request, edital, etapa_id, montagem)
    escolhido = None
    if painel["tipo"] == "pessoa" and painel["agendamento"] is not None:
        escolhido = (str(painel["agendamento"].banca_id), painel["agendamento"].inicio)
    elif painel["tipo"] == "horario":
        escolhido = painel["horario"].chave
    resumo = _resumo(montagem)
    return {
        "edital": edital,
        "processo": edital.processo,
        "etapa": etapa,
        "etapa_id": etapa_id,
        "montagem": montagem,
        "resumo": resumo,
        "dia": dia,
        "dia_por_extenso": dia_por_extenso(dia) if dia else "",
        "abas": _abas(montagem, dia),
        "bancas": [banca.nome for banca in montagem.agenda.bancas_em_ordem],
        "varias_bancas": len(montagem.agenda.bancas_em_ordem) > 1,
        "grade": _grade(montagem, dia, escolhido=escolhido) if dia else [],
        "painel": painel,
        # UX-764: a ação principal é a que falta fazer, e nenhuma aparece duas vezes.
        "pode_preencher": bool(montagem.sem_horario) and bool(montagem.livres),
        "devolvidos": leitura.devolvidos_pela_ultima_configuracao(montagem.agenda, montagem),
        "mensagem": request.session.pop(MENSAGEM, None),
    }


def _montagem_ou_configurar(edital, etapa_id):
    agenda = leitura.agenda_da_etapa(edital, etapa_id)
    if agenda is None:
        return None
    return leitura.montagem(edital, etapa_id, agenda)


@require_http_methods(["GET"])
def montar(request, edital_id, etapa_id):
    """O espaço de trabalho: resumo, abas, grade e painel (US2, UX-761 a UX-764)."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    montagem = _montagem_ou_configurar(edital, etapa_id)
    if montagem is None:
        return redirect("interface:agenda-configurar", edital.id, etapa_id)
    contexto = _contexto_da_montagem(request, edital, etapa, etapa_id, montagem)
    return marcar_como_privada(render(request, "interface/agenda_montar.html", contexto))


@require_http_methods(["GET"])
def painel(request, edital_id, etapa_id):
    """Só o painel, para o htmx: a pessoa, o horário livre ou a lista (UX-762)."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    montagem = _montagem_ou_configurar(edital, etapa_id)
    if montagem is None:
        return redirect("interface:agenda-configurar", edital.id, etapa_id)
    contexto = _contexto_da_montagem(request, edital, etapa, etapa_id, montagem)
    return marcar_como_privada(render(request, "interface/_agenda_painel.html", contexto))


def _recusa_da_montagem(request, edital, etapa, etapa_id, recusa, *, previa=None):
    """A recusa na tela inteira, com o status dela e a grade relida (contracts/recusas.md §3)."""
    if recusa.status == 404:
        raise _inexistente() from recusa
    montagem = _montagem_ou_configurar(edital, etapa_id)
    if montagem is None:
        request.session[MENSAGEM] = {"tipo": "erro", "texto": recusa.detail}
        return redirect("interface:agenda-configurar", edital.id, etapa_id)
    painel_ = (
        _contexto_da_previa(montagem, previa, recusa.detail)
        if previa is not None
        else _contexto_da_lista(request, montagem)
    )
    contexto = _contexto_da_montagem(request, edital, etapa, etapa_id, montagem, painel=painel_)
    if previa is None:
        contexto["mensagem"] = {"tipo": "erro", "texto": recusa.detail}
    if _htmx(request):
        resposta = render(request, "interface/_agenda_painel.html", contexto)
        resposta["HX-Retarget"] = "#painel"
        return marcar_como_privada(resposta)
    return marcar_como_privada(
        render(request, "interface/agenda_montar.html", contexto, status=recusa.status)
    )


def _de_volta(edital, etapa_id, *, dia=None):
    destino = reverse("interface:agenda-montar", args=[edital.id, etapa_id])
    return f"{destino}?dia={dia.isoformat()}" if dia else destino


@require_http_methods(["POST"])
def preencher(request, edital_id, etapa_id):
    """Sem `assinatura`, a prévia no painel; com ela, a aplicação (FR-7214, FR-7215)."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    assinatura = request.POST.get("assinatura", "")
    try:
        if not assinatura:
            montagem = _montagem_ou_configurar(edital, etapa_id)
            if montagem is None:
                return redirect("interface:agenda-configurar", edital.id, etapa_id)
            previa = montar_app.previa_do_preenchimento(
                actor=ator, edital=edital, etapa_id=etapa_id, montagem_=montagem
            )
            painel_ = _contexto_da_previa(montagem, previa, None)
            contexto = _contexto_da_montagem(
                request, edital, etapa, etapa_id, montagem, painel=painel_
            )
            template = (
                "interface/_agenda_painel.html"
                if _htmx(request)
                else "interface/agenda_montar.html"
            )
            return marcar_como_privada(render(request, template, contexto))
        frase = montar_app.aplicar_preenchimento(
            actor=ator,
            edital=edital,
            etapa_id=etapa_id,
            assinatura=assinatura,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except montar_app.MudouDesdeAPrevia as mudou:
        return _recusa_da_montagem(
            request, edital, etapa, etapa_id, mudou.recusa, previa=mudou.previa
        )
    except DomainError as recusa:
        return _recusa_da_montagem(request, edital, etapa, etapa_id, recusa)
    request.session[MENSAGEM] = {"tipo": "sucesso", "texto": frase}
    return _redirecionar(request, _de_volta(edital, etapa_id))


def _redirecionar(request, destino):
    """Depois de gravar, a página inteira volta — a grade, o resumo e o painel mudaram juntos."""
    if _htmx(request):
        resposta = HttpResponse(status=204)
        resposta["HX-Redirect"] = destino
        return resposta
    return redirect(destino)


@require_http_methods(["POST"])
def agendar(request, edital_id, etapa_id):
    """Agenda ou muda uma pessoa (`inscricao`, `horario`); `mudanca` vem do painel da pessoa."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    chave = _chave_do_horario(request.POST.get("horario"))
    inscricao = request.POST.get("inscricao") or ""
    try:
        if chave is None:
            raise DomainError(
                "horario_nao_escolhido", "Escolha um horário livre antes de confirmar.", 422
            )
        if not inscricao:
            raise DomainError(
                "pessoa_nao_escolhida",
                "Escolha quem vai para este horário antes de confirmar.",
                422,
            )
        try:
            UUID(inscricao)
        except ValueError:
            raise _inexistente() from None
        frase = montar_app.agendar(
            actor=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao,
            banca_id=chave[0],
            inicio=chave[1],
            mudanca=request.POST.get("mudanca") == "1",
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        return _recusa_da_montagem(request, edital, etapa, etapa_id, recusa)
    request.session[MENSAGEM] = {"tipo": "sucesso", "texto": frase}
    return _redirecionar(
        request, _de_volta(edital, etapa_id, dia=chave[1].astimezone(zona()).date())
    )


@require_http_methods(["POST"])
def liberar(request, edital_id, etapa_id):
    """Libera o horário de uma pessoa antes da publicação (FR-7212)."""
    ator, edital, etapa = _porta(request, edital_id, etapa_id)
    if ator is None:
        return identidade.pedir_identificacao(request)
    inscricao = request.POST.get("inscricao") or ""
    try:
        UUID(inscricao)
    except ValueError:
        raise _inexistente() from None
    try:
        frase = montar_app.liberar(
            actor=ator,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id=inscricao,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        return _recusa_da_montagem(request, edital, etapa, etapa_id, recusa)
    request.session[MENSAGEM] = {"tipo": "sucesso", "texto": frase}
    dia = _data(request.POST.get("dia") or "")
    return _redirecionar(request, _de_volta(edital, etapa_id, dia=dia))


# --- a seção da página da Etapa ------------------------------------------------------------------


def resumo_para_a_etapa(edital, etapa_id, participantes):
    """A seção "Agenda" da Distribuição (UX-765): vazia que ensina, ou o estado e o caminho.

    Uma consulta para a agenda e duas para a configuração, e o número de agendados numa quarta; a
    participação vem da Distribuição, que já a contou (`resumo.inscricoes`).
    """
    agenda = leitura.agenda_da_etapa(edital, etapa_id)
    if agenda is None:
        return {"existe": False}
    horarios = len(derivar(leitura.configuracao_da_agenda(agenda)))
    com_horario = agenda.agendamentos.count()
    return {
        "existe": True,
        "horarios": horarios,
        "com_horario": com_horario,
        "participantes": participantes,
        "falta": max(participantes - horarios, 0),
        "dias": len({janela.dia for janela in agenda.janelas_em_ordem}),
        "bancas": len(agenda.bancas_em_ordem),
    }
