"""A conferência do que será congelado na submissão, lida do próprio conteúdo canônico.

A `006` acrescentou Etapas, modalidades e Seções ao conteúdo publicado, e a tela de Revisão
continuou mostrando Perfis e Cronograma — porque cada coleção era um bloco escrito à mão no
template, e alguém precisava lembrar de acrescentar o próximo. Quem submetia declarava ter lido
metade do Edital.

Aqui a fonte é `edital_snapshot`, o mesmo conteúdo que a submissão congela. Uma coleção nova
aparece na Revisão porque está no snapshot, e não porque foi lembrada — o que faz a classe de
defeito desaparecer em vez de ser corrigida uma vez.

**A promessa valia só para a raiz, e o defeito voltou uma camada abaixo.** O guardião comparava as
listas de entidades da raiz, e o método comum do sorteio (um dicionário) e os marcos (uma coleção
dentro do Perfil) escaparam dele por construção: a Revisão congelava a Classificação inteira sem
mostrá-la, enquanto a prévia do PDF, na mesma tela, a imprimia. Por isso a declaração passou a ser
**campo a campo**, em `LIDOS` e `NAO_MOSTRADOS`, na grafia do contrato de mutabilidade — cuja
completude a `026` já guarda contra o snapshot. Campo novo sem destino aqui reprova no dia em que
nasce.

**Não é o snapshot cru na tela.** Cada coleção tem uma leitura curta, no vocabulário de quem
elabora; o que este módulo garante é que nenhuma delas fique de fora.
"""

import re
from datetime import datetime

from processo_seletivo.editais.domain import marcos as regras_do_marco
from processo_seletivo.editais.domain import quadro
from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.editais.domain.documentos import denominacao_do_codigo
from processo_seletivo.editais.domain.mutabilidade import RAIZ
from processo_seletivo.editais.domain.perfis import CAMPOS_DO_METODO
from processo_seletivo.interface import origens
from processo_seletivo.interface.forms import ZONA
from processo_seletivo.interface.origens import Rotulada
from processo_seletivo.interface.templatetags.interface_extras import contagem, plural, pontuacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    criterio_com_a_ausencia,
    forma_de_convocacao_por_extenso,
    por_identificador,
)
from processo_seletivo.publicacoes.infrastructure import pdf

# **As frases do marco são as do documento, lidas do mesmo lugar.** Reescrevê-las aqui daria à
# conferência uma segunda grafia da regra — e é na primeira divergência entre as duas que quem
# submete confere uma coisa e publica outra. `divulgacao` já importa do PDF pela mesma razão.
from processo_seletivo.publicacoes.infrastructure.pdf import (
    FORMA_DA_ORDEM,
    NORMALIZACAO_DO_MARCO,
    TIPO_DO_FATO,
    _arredondamento,
    _combinacao,
    _continuacao_do_corte,
    _empate_no_corte,
    _enumerar,
    _habilitacao_ao_sorteio,
    _janela_recursal,
    _origem_do_metodo,
    _regra_de_corte,
    _valor_do_campo_do_metodo,
    teto_de_inscricoes,
)
from processo_seletivo.requerimentos.domain import nomes as nomes_do_requerimento

RESERVA = {"NONE": "não há", "LIMITED": "limitado", "UNLIMITED": "ilimitado"}

#: Onde as leituras acham o alcance dos gestos (051, FR-934). O snapshot chega a cada leitura por
#: `_cada`, e é ele que viaja; a chave vive numa cópia rasa feita em `blocos`, e nunca no conteúdo.
_ALCANCE = "__alcance_dos_gestos__"


def _alcance_dos_gestos(snapshot):
    return (snapshot or {}).get(_ALCANCE) or {}


CARATER = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _instante(valor):
    if not valor:
        return None
    return datetime.fromisoformat(str(valor)).astimezone(ZONA).strftime("%d/%m/%Y %H:%M")


def _perfil(perfil, snapshot):
    linhas = [
        # **O total e o quadro na mesma linha** (027, FR-326, UX-043). A Revisão dizia
        # "2 vaga(s) imediata(s)" e nunca mencionava o quadro: quem submetia lia o número que o
        # Edital publica sem ver o que a apuração usaria, e os dois podiam não ter relação alguma.
        # Ler os dois juntos é o que torna a divergência visível no único momento em que corrigi-la
        # ainda é barato — depois da publicação, a mesma informação custa uma Retificação.
        _vagas_e_quadro(perfil),
        Rotulada(
            "Cadastro Reserva",
            RESERVA.get(perfil.get("reserveType"), "—")
            + (f" em {perfil['reserveLimit']}" if perfil.get("reserveLimit") is not None else ""),
        ),
    ]
    if perfil.get("locality"):
        linhas.append(Rotulada("Localidade", perfil["locality"]))
    # O que o documento imprime sobre a vaga e a conferência não lia. Impressos só quando
    # declarados, como no documento: ausência é "não declarou", e não um valor padrão.
    for rotulo, chave in (
        ("Descrição", "description"),
        ("Carga horária", "workload"),
        ("Remuneração", "compensation"),
        ("Atribuições", "duties"),
    ):
        if perfil.get(chave):
            linhas.append(Rotulada(rotulo, perfil[chave]))
    for requisito in perfil.get("requirements") or []:
        linhas.append(Rotulada("Requisito", requisito))
    for modalidade in perfil.get("competitionModalities") or []:
        regra = modalidade.get("normativeRule") or {}
        partes = [f"{modalidade.get('code', '')} — {modalidade.get('name', '')}"]
        if regra.get("percentage"):
            partes.append(f"{pontuacao(regra['percentage'])}%")
        if regra.get("foundation"):
            partes.append(regra["foundation"])
            if regra.get("version"):
                partes.append(f"versão {_versao(regra['version'])}")
        if regra.get("effectiveFrom"):
            # A data como foi declarada, sem conversão de fuso: vigência é dia, e levar
            # `2014-06-09T00:00Z` para o horário de Brasília a publicaria como 08/06.
            partes.append(f"vigente desde {_dia(regra['effectiveFrom'])}")
        # A descrição que só repete o nome não é informação: é o que o catálogo grava quando
        # ninguém escreveu outra, e imprimi-la dobraria a linha sem dizer nada.
        if modalidade.get("description") and modalidade["description"] != modalidade.get("name"):
            partes.append(modalidade["description"])
        # O arredondamento da reserva, quando declarado (051, FR-933): é ele que decide quantas
        # vagas a sugestão do quadro propõe, e não se corrige depois de publicado.
        if regra.get("rounding"):
            partes.append(f"arredondamento: {quadro.em_palavras(regra['rounding'])}")
        gesto = origens.gesto_da_modalidade(_alcance_dos_gestos(snapshot), perfil, modalidade)
        linhas.append(
            origens.com_origem(
                Rotulada("Modalidade", " · ".join(partes)),
                origens.frase_do_gesto(gesto) if gesto else "",
            )
        )
    if perfil.get("competitionModalities"):
        linhas.append(Rotulada("Ampla concorrência", _ampla(perfil)))
    # O quadro de vagas, na ordem declarada e com a linha geral primeiro. Quem submete precisa ver
    # os números que vai congelar — e o quadro é o que separa o certame de existir como documento.
    denominacoes = {
        str(modalidade.get("id")): f"{modalidade.get('name', '')} ({modalidade.get('code', '')})"
        for modalidade in perfil.get("competitionModalities") or []
        if modalidade.get("id")
    }
    for linha in perfil.get("vacancyTable") or []:
        recorte = (
            denominacoes.get(str(linha.get("modalityId")), "modalidade desconhecida")
            if linha.get("modalityId")
            else "Ampla concorrência"
        )
        modalidade_da_linha = next(
            (
                item
                for item in perfil.get("competitionModalities") or []
                if str(item.get("id")) == str(linha.get("modalityId"))
            ),
            None,
        )
        linhas.append(
            origens.com_origem(
                Rotulada(
                    "Quadro",
                    f"{recorte} — {contagem(linha.get('immediateVacancies', 0), 'vaga,vagas')}",
                ),
                origens.da_linha_do_quadro(
                    linha.get("immediateVacancies"), modalidade_da_linha, perfil
                )
                if modalidade_da_linha
                else "",
            )
        )
    sem_linha = _listas_sem_linha(perfil, denominacoes)
    if sem_linha:
        # Dito aqui, e não só na lista de pendências: quem lê o bloco do Perfil precisa ver, ao
        # lado dos números, qual recorte fica sem quantidade — e não descobrir na etapa seguinte
        # que uma das listas que ele declarou não terá o que apurar (FR-326).
        linhas.append(
            Rotulada(
                "Sem linha no quadro",
                ", ".join(sem_linha)
                + " — a ocupação e a convocação não terão quantidade a apurar "
                + plural(len(sem_linha), "nesse recorte,nesses recortes")
                + ".",
            )
        )
    # A reversão e a forma de comunicar a convocação: duas das declarações que mais pesam na
    # operação, e que depois da publicação só se corrigem por Retificação. A reversão só é dita
    # onde há lista reservada que pudesse reverter — num Perfil só de ampla, "não reverte" seria
    # resposta a uma pergunta que o Perfil não coloca.
    especie = (perfil.get("vacancyReversion") or {}).get("kind")
    if especie or set(denominacoes) - {str(perfil.get("generalCompetitionModalityId"))}:
        gesto = origens.gesto_do_campo(_alcance_dos_gestos(snapshot), perfil, "vacancyReversion")
        reversao = REVERSAO.get(especie, especie or "não")
        if especie and quadro.sem_vaga_imediata(perfil):
            # O documento não a imprime sem vaga imediata (067, ED-12, UX-192): dito aqui, quem
            # submete sabe que a declaração continua no conteúdo e fica fora do ato.
            reversao = f"{reversao} — não sai no documento: o Perfil não tem vaga imediata"
        linhas.append(
            origens.com_origem(
                Rotulada(
                    "Reverter vaga reservada não preenchida para a ampla concorrência", reversao
                ),
                origens.frase_do_gesto(gesto) if gesto else "",
            )
        )
    # A ausência é dita, e não omitida: a `019` recusa convocar quem não declarou a forma, e é
    # aqui que quem submete ainda pode declará-la sem Retificação.
    gesto = origens.gesto_do_campo(_alcance_dos_gestos(snapshot), perfil, "callForm")
    linhas.append(
        origens.com_origem(
            Rotulada(
                "Como a convocação é comunicada",
                forma_de_convocacao_por_extenso(perfil.get("callForm")),
            ),
            origens.frase_do_gesto(gesto)
            if gesto
            else origens.da_forma_de_convocacao(perfil, (snapshot or {}).get("profiles") or []),
        )
    )
    # Os fatos, com o código: é por ele que os critérios de desempate os alcançam, e é ele que
    # identifica o mesmo fato em dois Perfis.
    for fato in perfil.get("declaredFacts") or []:
        tipo = TIPO_DO_FATO.get(fato.get("type"), fato.get("type") or "")
        linhas.append(
            Rotulada(
                "Fato exigido do candidato",
                f"{fato.get('label') or fato.get('code', '')} "
                f"({tipo}, código {fato.get('code', '')})",
            )
        )
    return {"titulo": f"{perfil.get('code', '')} — {perfil.get('name', '')}", "linhas": linhas}


# A reversão na grafia das opções da composição, e não a do documento: a do documento é frase
# normativa inteira, e a conferência lê o que foi escolhido.
REVERSAO = {
    "ON_EXHAUSTION": "só quando a lista reservada esgota",
    "ON_BALANCE": "a quantidade que ficou sem preencher",
}


#: Os rótulos dos dois valores do Perfil que o controle do Edital aplica (051, FR-926) — os mesmos
#: com que `_perfil` os lê, para que a prévia e a conferência digam a mesma coisa.
ROTULO_DO_CAMPO_DO_PERFIL = {
    "callForm": "Como a convocação é comunicada",
    "vacancyReversion": "Reverter vaga reservada não preenchida para a ampla concorrência",
}


def arredondamento_da_reserva(rounding):
    """O arredondamento da regra normativa em palavras (051, FR-933)."""
    return quadro.em_palavras(rounding)


def _versao(valor):
    """A versão da norma, em dd/mm/aaaa quando ela é uma data (057, FR-1058).

    A versão é texto livre de quem declara a norma: "2014-06-09" é a forma que o catálogo grava, mas
    nada impede "2ª edição". Só a data reconhecível muda de grafia; o resto sai como está.
    """
    texto = str(valor)
    return _dia(texto) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto) else texto


def _dia(valor):
    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)


def _ampla(perfil):
    """Qual Modalidade é a ampla concorrência, com as palavras da composição (014, D-014)."""
    ampla = str(perfil.get("generalCompetitionModalityId") or "")
    for modalidade in perfil.get("competitionModalities") or []:
        if ampla and str(modalidade.get("id")) == ampla:
            return f"{modalidade.get('code', '')} — {modalidade.get('name', '')}"
    return "nenhuma Modalidade — a ampla concorrência é só a linha geral do quadro"


def _vagas_e_quadro(perfil):
    """O que o Edital publica e o que o quadro reparte, lado a lado (027, FR-326)."""
    publicadas = contagem(perfil.get("immediateVacancies", 0), "vaga imediata,vagas imediatas")
    linhas = [
        linha
        for linha in perfil.get("vacancyTable") or []
        if isinstance(linha, dict) and isinstance(linha.get("immediateVacancies"), int)
    ]
    if not linhas:
        # Acervo: publicado antes de o quadro existir. Ausência é "não declarou", e nunca zero — a
        # frase diz o que falta em vez de inventar um número que o Edital não tem.
        return f"{publicadas} · o quadro de vagas não é declarado"
    soma = sum(linha["immediateVacancies"] for linha in linhas)
    return f"{publicadas} · o quadro reparte {soma}"


def _listas_sem_linha(perfil, denominacoes):
    """As listas reservadas que o quadro não cobre, pelo nome com que a tela as mostra."""
    ampla = perfil.get("generalCompetitionModalityId")
    ampla = str(ampla) if ampla else None
    com_linha = {
        str(linha.get("modalityId"))
        for linha in perfil.get("vacancyTable") or []
        if isinstance(linha, dict) and linha.get("modalityId")
    }
    return sorted(
        nome
        for identidade, nome in denominacoes.items()
        if identidade != ampla and identidade not in com_linha
    )


def _evento(evento, _snapshot):
    periodo = _instante(evento.get("startAt")) or "—"
    if evento.get("endAt"):
        periodo += f" · Término: {_instante(evento['endAt'])}"
    linhas = [evento.get("description", ""), Rotulada("Início", periodo)]
    if evento.get("location"):
        linhas.append(Rotulada("Onde acontece", evento["location"]))
    # Decidido na etapa Inscrição, e dito aqui porque é propriedade do Evento no que se congela:
    # é por ela que o portal abre e fecha as inscrições.
    if evento.get("isRegistrationPeriod"):
        linhas.append("É o período de inscrições deste Edital")
    return {
        "titulo": f"{evento.get('order', '')}. {evento.get('type', '')}",
        "linhas": linhas,
    }


def _etapa(etapa, snapshot):
    caracteres = [rotulo for chave, rotulo in CARATER if etapa.get(chave)]
    linhas = [
        origens.com_origem(
            Rotulada("Caráter", " e ".join(caracteres) if caracteres else "não informado"),
            origens.da_etapa(etapa),
        )
    ]
    if etapa.get("weight") is not None:
        linhas.append(Rotulada("Peso", pontuacao(etapa["weight"])))
    if etapa.get("minimumScore") is not None:
        linhas.append(Rotulada("Nota mínima", pontuacao(etapa["minimumScore"])))
    # O incremento da `012`. Estavam no formulário e no documento publicado, e faltavam
    # justamente aqui — na tela cuja pergunta é "o que será congelado". Quem submetia congelava
    # dois campos que a conferência não mostrava, e a pontuação máxima é o teto contra o qual
    # cada avaliação da Etapa é validada depois. Impressos só quando declarados, como no
    # documento: ausência é "o Edital não declarou", e não "declarou o padrão".
    if etapa.get("maximumScore") is not None:
        linhas.append(Rotulada("Pontuação máxima", pontuacao(etapa["maximumScore"])))
    # A forma, e os rótulos só onde eles existem: quem revisa precisa ver que esta Etapa não pontua
    # antes de submeter, e não descobrir isso no documento publicado (D-008).
    if etapa.get("forma") == "DECISORIA":
        favoravel = etapa.get("rotuloFavoravel") or "—"
        desfavoravel = etapa.get("rotuloDesfavoravel") or "—"
        linhas.append(Rotulada("Conclusão", f"decisão, sem nota ({favoravel} / {desfavoravel})"))
    else:
        linhas.append(Rotulada("Conclusão", "com pontuação"))
    if etapa.get("evaluationsPerRegistration") is not None:
        linhas.append(Rotulada("Avaliações por inscrição", etapa["evaluationsPerRegistration"]))
    vinculado = next(
        (
            evento
            for evento in (snapshot.get("schedule") or [])
            if evento.get("id") == etapa.get("scheduleEventId")
        ),
        None,
    )
    if vinculado:
        linhas.append(
            Rotulada(
                f"Datas do Evento “{vinculado.get('type', '')}”",
                _instante(vinculado.get("startAt")),
            )
        )
    return {"titulo": f"{etapa.get('order', '')}. {etapa.get('name', '')}", "linhas": linhas}


def _nomes_do_alcance(snapshot):
    """Perfis e modalidades por identificador — o alcance é publicado por `id`, e lido por nome."""
    perfis, modalidades = {}, {}
    for perfil in snapshot.get("profiles") or []:
        perfis[perfil.get("id")] = perfil.get("name") or perfil.get("code", "")
        for modalidade in perfil.get("competitionModalities") or []:
            modalidades[modalidade.get("id")] = modalidade.get("name") or modalidade.get("code", "")
    return perfis, modalidades


def _alcance(documento, snapshot):
    """A quem o documento se aplica, nas cinco formas que a ausência dos campos produz (044).

    É a informação mais fácil de ler errado do bloco: um laudo exigido só de uma modalidade parece
    exigido de todo mundo quando a lista não diz de quem é. O documento publicado já resolve isso
    agrupando as alíneas por destinatário; aqui a mesma frase vem por item, porque a conferência é
    lista de itens e não tem grupos.
    """
    perfil_id, modalidade_id = documento.get("profileId"), documento.get("modalityId")
    if documento.get("modalityCode"):
        # A mesma frase do documento publicado (044, R-008), para a conferência dizer o que ele diz.
        denominacao = denominacao_do_codigo(snapshot, documento["modalityCode"])
        return f"candidatos concorrentes na modalidade {denominacao}, em todos os Perfis"
    if perfil_id is None and modalidade_id is None:
        return "todos os candidatos"
    perfis, modalidades = _nomes_do_alcance(snapshot)
    if modalidade_id is None:
        return f"candidatos ao perfil {perfis.get(perfil_id, '')}"
    if perfil_id is None:
        return f"candidatos concorrentes na modalidade {modalidades.get(modalidade_id, '')}"
    return (
        f"candidatos ao perfil {perfis.get(perfil_id, '')} concorrentes na modalidade "
        f"{modalidades.get(modalidade_id, '')}"
    )


def _documento(documento, snapshot):
    linhas = [
        Rotulada("Exigência", "obrigatória" if documento.get("required", True) else "facultativa"),
        Rotulada("Aplica-se a", _alcance(documento, snapshot)),
    ]
    if documento.get("instructions"):
        linhas.append(Rotulada("Instruções", documento["instructions"]))
    return {
        "titulo": f"{documento.get('order', '')}. {documento.get('name', '')}",
        "linhas": linhas,
    }


def _secao(secao, numeros):
    if secao.get("type") == catalogo.GERADA:
        origem = {
            "profiles": "Perfis",
            "schedule": "Cronograma",
            "stages": "Etapas",
            "documentRequirements": "Documentos Exigidos",
            # A conferência de quem homologa lia "Composta a partir de attachments". O anexo é a
            # única coleção do catálogo que não tinha nome em português aqui.
            "attachments": "Anexos",
        }
        nome_da_origem = origem.get(secao.get("source"), secao.get("source"))
        detalhe = f"Composta a partir de {nome_da_origem}."
        # A gerada que não sai diz **por quê**: a coleção de origem está vazia. "Vazia" sozinho
        # não distingue texto a transcrever de dado a cadastrar, e é essa a pergunta de quem
        # homologa diante da seção que falta (code review do PR 233).
        vazia = f"Nada cadastrado em {nome_da_origem} — não sai no documento."
    else:
        detalhe = secao.get("content", "")
        vazia = "Vazia — não sai no documento."
    # **O número é o do documento** (054, FR-985), e não a ordem do catálogo: com 22 seções e as
    # textuais vazias, a ordem diria "16" onde o documento imprime "9", e quem homologa confere a
    # prévia contra o original pela numeração (E10 = B).
    numero = numeros.get(secao.get("key"))
    titulo = str(secao.get("title", ""))
    if numero is None:
        return {"titulo": titulo, "linhas": [vazia]}
    if numero == 0:
        return {"titulo": f"{titulo} (preâmbulo, sem número)", "linhas": [detalhe]}
    return {"titulo": f"{numero}. {titulo}", "linhas": [detalhe]}


def _anexo(anexo, snapshot):
    """O Anexo na conferência, **com o caminho para abrir os bytes** (020, FR-018).

    Conferir bytes que não se pode abrir não é conferir: quem homologa precisa ver o formulário que
    o Edital vai publicar, e não a linha que diz que ele existe. O identificador viaja para que o
    template monte o endereço do rascunho, que não é público.

    A linha nomeia os requisitos que apontam este Anexo como modelo. Sem ela, a tela mostraria duas
    listas sem relação — os anexos de um lado, os documentos exigidos do outro — e quem homologa
    teria de cruzá-las de cabeça.
    """
    identidade = str(anexo.get("id", ""))
    modelos = [
        documento.get("name", "")
        for documento in snapshot.get("documentRequirements") or []
        if str(documento.get("attachmentId") or "") == identidade
    ]
    return {
        "titulo": anexo.get("label") or "sem rótulo",
        "linhas": [
            Rotulada("modelo de", ", ".join(modelos))
            if modelos
            else "não é modelo de nenhum requisito",
        ],
        "anexo_id": identidade,
    }


def _leitura_do_marco(marco, perfil, snapshot):
    """Os pares `(rótulo, valor)` que um marco declara, na ordem em que o documento os imprime.

    **A frase é a do documento** (`_combinacao`, `_regra_de_corte`, `_janela_recursal`,
    `_empate_no_corte`, `_continuacao_do_corte`, `_habilitacao_ao_sorteio`): é a mesma regra, e
    duas redações dela seriam duas normas. O empate, a continuação e a habilitação tinham aqui
    redação própria enquanto o documento os calava; o documento passou a imprimi-los, e as frases
    moram lá. O que a conferência ainda acrescenta é o silêncio dito como silêncio ("nada
    declarado") e a Etapa que o corte alimenta quando não há nenhuma — que o documento cala de
    propósito, e quem submete precisa ver.

    **Sem a denominação e sem o código**, que viajam à parte: os dois nascem do Perfil (030,
    FR-420), e deixá-los aqui faria dois marcos com a mesma regra parecerem diferentes só porque
    moram em Perfis diferentes — que é justamente o que o agrupamento existe para não fazer.
    """
    etapas = por_identificador(snapshot.get("stages"))
    fatos = por_identificador(perfil.get("declaredFacts"))
    # A mesma pergunta que a tela e a validação fazem, com o método comum resolvido: um marco que
    # referencia o método do Edital sorteia, e quem lesse só a chave dele diria que não.
    sorteia = regras_do_marco.marco_ordena_por_sorteio(
        snapshot, perfil_id=perfil.get("id"), marco_id=marco.get("id")
    )
    pares = []
    if FORMA_DA_ORDEM.get(marco.get("orderProduction")):
        pares.append(("Ordem", FORMA_DA_ORDEM[marco["orderProduction"]]))
    if not sorteia:
        # Sob sorteio a combinação não é impressa, e pela razão do documento (032, FR-468): a
        # ordem não vem de nota, e mostrá-la afirmaria um método que o marco não usa.
        pares.append(("Combinação", _combinacao(marco, etapas) or "nenhuma Etapa enumerada"))
        if NORMALIZACAO_DO_MARCO.get(marco.get("normalization")):
            pares.append(("Normalização", NORMALIZACAO_DO_MARCO[marco["normalization"]]))
    # O arredondamento e o empate seguem a forma **declarada**, que é a do documento (067, D-004):
    # a Revisão mostra o que o documento vai imprimir. A combinação e o bloco do sorteio continuam
    # pela forma resolvida, como antes.
    declara_sorteio = regras_do_marco.declara_sorteio(marco)
    if not declara_sorteio and (arredondamento := _arredondamento(marco)):
        pares.append(
            (
                "Arredondamento",
                origens.com_origem(arredondamento, origens.do_arredondamento_do_marco(marco)),
            )
        )
    if sorteia:
        pares.append(("Sorteio", f"método {_origem_do_metodo(snapshot, marco)}"))
        proprio = marco.get("drawMethod") or {}
        # Só o método **próprio**: o comum já está no alto do bloco, uma vez. E só com ele
        # declarado — o instante vazio sai do PDF como "—", que é verdadeiro e passaria pelo
        # filtro, imprimindo "Quando: —" em todo marco que referencia o comum.
        if proprio:
            pares.extend(
                (f"Sorteio — {rotulo}", _com_origem_do_metodo(campo, valor, proprio, snapshot))
                for campo, _, rotulo in CAMPOS_DO_METODO
                if (valor := _valor_do_campo_do_metodo(campo, proprio))
            )
        pares.append(
            (
                "Habilitação",
                _habilitacao_ao_sorteio(snapshot, perfil, marco, etapas)
                or "Etapa declarada que não existe neste Edital",
            )
        )
    # "deste marco" no lugar do nome (067, D-012): a denominação está na linha de cima, e com o nome
    # na frase cada Perfil seria um grupo — o que a nota abaixo, sobre a denominação, já recusa.
    pares.append(("Recurso", _janela_recursal(marco, objeto="deste marco") or "nada declarado"))
    regra = marco.get("cutRule")
    if isinstance(regra, dict):
        # A regra sem alvo não publica, e a pendência o diz; aqui a linha não sai vazia.
        pares.append(
            (
                "Corte",
                origens.com_origem(
                    _regra_de_corte(marco, etapas) or "declarado sem alvo", origens.do_corte(regra)
                ),
            )
        )
        # Logo depois do corte, e sem par quando não declarados: "essa quantidade" é a que ele
        # acabou de dizer, e a ausência impede a publicação (FR-182, FR-226) — "nada declarado"
        # aqui leria como o silêncio legítimo do recurso, que não é.
        if not declara_sorteio and (empate := _empate_no_corte(marco)):
            pares.append(("Empate no corte", empate))
        if continuacao := _continuacao_do_corte(marco):
            pares.append(("Continuação", continuacao))
        if regra.get("governedStage") == "NONE":
            pares.append(("Etapa que o corte alimenta", "nenhuma"))
    else:
        pares.append(("Corte", "este marco não corta"))
    criterios = sorted(marco.get("tiebreakers") or [], key=lambda item: item.get("order") or 0)
    pares.extend(
        (f"Desempate, {indice}º", criterio_com_a_ausencia(criterio, etapas, fatos))
        for indice, criterio in enumerate(criterios, start=1)
    )
    return tuple(pares)


def _com_origem_do_metodo(campo, valor, metodo, snapshot):
    """O campo do método com a origem, quando ela é derivada: o Evento, ou a frase da regra."""
    if campo == "occurrenceAt":
        return origens.com_origem(
            valor, origens.do_instante(metodo.get("occurrenceAt"), (snapshot or {}).get("schedule"))
        )
    if campo in ("normalization", "substitutionRule"):
        return origens.com_origem(valor, origens.da_prosa(metodo.get(campo)))
    return valor


def _quem(codigos):
    if len(codigos) == 1:
        return f"Perfil {codigos[0]}"
    return f"{len(codigos)} Perfis: {_enumerar(codigos)}"


def _denominacao(grupo):
    """A denominação do grupo, dita uma vez quando ela é a mesma, ou quando segue a derivada.

    A derivada (030, FR-420) repete o nome do Perfil — "Classificação final — Professor de
    Matemática" —, e listá-la Perfil a Perfil devolveria à tela o muro que o agrupamento tirou.
    """
    nomes = [nome for _, nome, _ in grupo["membros"]]
    if len(set(nomes)) == 1:
        return nomes[0] or "—"
    if all(nome == derivada for _, nome, derivada in grupo["membros"]):
        return "Classificação final — o nome de cada Perfil"
    return "; ".join(f"{codigo}: {nome or '—'}" for codigo, nome, _ in grupo["membros"])


def _marcos_agrupados(snapshot):
    """Os marcos, agrupados pelo que declaram — e o que diverge, dito como divergência.

    **Por que agrupar.** Num Edital de 16 Perfis são 16 marcos, e em quase todos a regra é a mesma:
    ler 16 vezes o mesmo corte não é conferir, é procurar a diferença a olho. O agrupamento faz o
    que a Revisão já faz com Evento e Etapa, que são do Edital e aparecem uma vez: o que é igual
    aparece uma vez, com os Perfis a que se aplica.

    **O que diverge é nomeado, e não só separado.** O grupo mais numeroso de cada posição é a
    referência; cada outro diz em que rótulos difere dela. Um grupo à parte, sem essa linha,
    mandaria quem confere comparar duas listas de dez linhas para achar a única que mudou.

    **Por posição, e não pelo Edital inteiro.** Um Perfil com dois marcos — o que corta para a
    entrevista e o que classifica ao final — tem dois marcos que não se comparam entre si; o
    primeiro de um Perfil se compara com o primeiro dos outros.
    """
    grupos = {}
    for perfil in snapshot.get("profiles") or []:
        _, derivada = regras_do_marco.identidade_derivada(
            codigo_do_perfil=perfil.get("code"), nome_do_perfil=perfil.get("name")
        )
        for posicao, marco in enumerate(perfil.get("classificationMilestones") or []):
            pares = _leitura_do_marco(marco, perfil, snapshot)
            grupo = grupos.setdefault(
                (posicao, pares), {"posicao": posicao, "pares": pares, "membros": []}
            )
            grupo["membros"].append((perfil.get("code", ""), marco.get("name", ""), derivada))
            gesto = origens.gesto_do_marco(_alcance_dos_gestos(snapshot), perfil)
            if gesto is not None:
                grupo.setdefault("gestos", {}).setdefault(gesto.pk, (gesto, []))[1].append(
                    perfil.get("code", "")
                )
    varios = any(grupo["posicao"] for grupo in grupos.values())
    itens = []
    for posicao in sorted({grupo["posicao"] for grupo in grupos.values()}):
        da_posicao = [grupo for grupo in grupos.values() if grupo["posicao"] == posicao]
        # `sorted` é estável: no empate de tamanho, vale a ordem dos Perfis.
        da_posicao.sort(key=lambda grupo: -len(grupo["membros"]))
        referencia = da_posicao[0]
        for grupo in da_posicao:
            codigos = [codigo for codigo, _, _ in grupo["membros"]]
            titulo = _quem(codigos)
            if varios:
                titulo = f"{posicao + 1}º marco — {titulo}"
            item = {
                "titulo": titulo,
                "linhas": [Rotulada("Denominação", _denominacao(grupo))]
                + [Rotulada(rotulo, valor) for rotulo, valor in grupo["pares"]]
                # A origem do materializado (051, FR-934, FR-935): quem o gesto alcançou e ainda
                # tem o valor que ele gravou. O que foi editado depois não aparece aqui.
                + [
                    Rotulada("Origem", f"{_enumerar(codigos)} — {origens.frase_do_gesto(gesto)}")
                    for gesto, codigos in (grupo.get("gestos") or {}).values()
                ],
            }
            if grupo is not referencia:
                diferentes = _divergencias(grupo["pares"], referencia["pares"])
                quantos = len(referencia["membros"])
                de_quem = (
                    f"do marco de {quantos} Perfis"
                    if quantos > 1
                    else f"do marco do Perfil {referencia['membros'][0][0]}"
                )
                item["diverge"] = f"Diverge {de_quem} em: {_enumerar(diferentes)}."
            itens.append(item)
    return itens


def _divergencias(pares, referencia):
    """Os rótulos cujo valor difere entre as duas leituras, ou que só uma delas tem."""
    proprios, outros = dict(pares), dict(referencia)
    return [
        rotulo
        for rotulo in dict.fromkeys([*proprios, *outros])
        if proprios.get(rotulo) != outros.get(rotulo)
    ]


def _classificacao(snapshot):
    """O método comum do sorteio, os marcos de cada Perfil e os Perfis que não têm marco.

    Não é coleção-raiz, e é por isso que escapou: o método comum é um dicionário da raiz, e os
    marcos moram dentro de cada Perfil. O bloco existe porque a etapa existe — é na
    `classificacao` que tudo isto se corrige.
    """
    itens = []
    comum = snapshot.get("drawMethod")
    if isinstance(comum, dict) and comum:
        itens.append(
            {
                "titulo": "Método do sorteio comum a este Edital",
                "linhas": [
                    Rotulada(rotulo, _com_origem_do_metodo(campo, valor, comum, snapshot))
                    for campo, _, rotulo in CAMPOS_DO_METODO
                    if (valor := _valor_do_campo_do_metodo(campo, comum))
                ],
            }
        )
    itens.extend(_marcos_agrupados(snapshot))
    sem_marco = [
        perfil.get("code", "")
        for perfil in snapshot.get("profiles") or []
        if not perfil.get("classificationMilestones")
    ]
    if sem_marco:
        itens.append(
            {
                "titulo": "Sem marco classificatório",
                "linhas": [
                    f"{_quem(sem_marco)} — "
                    + ("não produz" if len(sem_marco) == 1 else "não produzem")
                    + " ordem, e não há o que ocupar."
                ],
            }
        )
    return itens


def _secoes_do_documento(snapshot):
    """As seções com o número do documento, calculado uma vez para todas (054, FR-985)."""
    numeros = pdf.numeracao(snapshot)
    return [_secao(secao, numeros) for secao in snapshot.get("sections") or []]


def _cada(chave, leitura):
    """A leitura item a item de uma coleção-raiz."""
    return lambda snapshot: [leitura(item, snapshot) for item in snapshot.get(chave) or []]


# Bloco da conferência → como se lê, e onde se corrige. A ordem é a do assistente.
BLOCOS = (
    ("Perfis de Vaga", "perfis", _cada("profiles", _perfil)),
    ("Cronograma", "cronograma", _cada("schedule", _evento)),
    ("Etapas de Avaliação", "etapas", _cada("stages", _etapa)),
    # Depois das Etapas porque é a ordem do assistente: o marco enumera Etapas, e é na etapa
    # `classificacao` que ele se corrige.
    ("Classificação", "classificacao", _classificacao),
    # Estava no snapshot que a submissão congela e não estava aqui: quem revisava homologava
    # sem ver o que o Edital exigiria do candidato. Entre Etapas e Conteúdo porque é a ordem
    # do assistente, e a etapa é `inscricao` — é lá que se corrige.
    ("Documentos Exigidos", "inscricao", _cada("documentRequirements", _documento)),
    # Depois dos Documentos Exigidos pela mesma razão: no assistente, Anexos vem logo após
    # Inscrição, e é o Anexo que serve de modelo ao requisito — não o contrário.
    ("Anexos do Edital", "anexos", _cada("attachments", _anexo)),
    ("Conteúdo do Edital", "conteudo", _secoes_do_documento),
)


# **O que a conferência lê, campo a campo**, na grafia `(coleção, caminho)` do contrato de
# mutabilidade. Com `NAO_MOSTRADOS`, é uma partição do contrato — e o contrato, a `026` já o
# prende ao snapshot. É assim que um campo novo reprova aqui no dia em que nasce, e não quando
# alguém nota que a tela não o mostra.
#
# **"Lido" é "a conferência o mostra ou o resolve"**: `stages` do marco não aparece como lista,
# e sim na combinação, com o nome e o peso de cada Etapa — e, sob sorteio, nem assim, como no
# documento (032, FR-468); `scheduleEventId` aparece nas datas do Evento.
_METODO_LIDO = (
    "algorithm",
    "source",
    "occurrence",
    "occurrenceAt",
    "derivation",
    "normalization/text",
    "substitutionRule/text",
)
_LIDOS_POR_COLECAO = {
    RAIZ: (
        "number",
        "year",
        "title",
        "description",
        "processoCode",
        "processoTitle",
        "maxInscricoesPorCandidato",
        "matriculationRequest/moment",
        "matriculationRequest/declarationText",
        *(f"drawMethod/{campo}" for campo in _METODO_LIDO),
    ),
    "profiles": (
        "code",
        "name",
        "description",
        "requirements",
        "immediateVacancies",
        "reserveType",
        "reserveLimit",
        "locality",
        "duties",
        "workload",
        "compensation",
        "generalCompetitionModalityId",
        "vacancyReversion/kind",
        "callForm",
    ),
    "competitionModalities": (
        "code",
        "name",
        "description",
        "normativeRule/foundation",
        "normativeRule/version",
        "normativeRule/percentage",
        "normativeRule/effectiveFrom",
    ),
    "vacancyTable": ("modalityId", "immediateVacancies"),
    "declaredFacts": ("code", "label", "type"),
    "classificationMilestones": (
        "name",
        "orderProduction",
        "stages",
        "operation",
        "normalization",
        "rounding/scale",
        "rounding/mode",
        "appealWindow/admits",
        "appealWindow/durationDays",
        # A frase diz "dias corridos", e é a única contagem que a validação admite.
        "appealWindow/unit",
        *(f"drawMethod/{campo}" for campo in _METODO_LIDO),
        "drawMethod/qualifyingStageId",
        "cutRule/targetKind",
        "cutRule/targetCount",
        "cutRule/surplusCount",
        "cutRule/tieOutcome",
        "cutRule/governedStage",
        "cutRule/continuation",
    ),
    "tiebreakers": (
        "order",
        "type",
        "parameters/stageId",
        "parameters/factId",
        "whenMissing",
    ),
    "schedule": (
        "type",
        "description",
        "startAt",
        "endAt",
        "order",
        "location",
        "isRegistrationPeriod",
    ),
    "stages": (
        "order",
        "scheduleEventId",
        "name",
        "weight",
        "minimumScore",
        "maximumScore",
        "evaluationsPerRegistration",
        "eliminatory",
        "classificatory",
        "forma",
        "rotuloFavoravel",
        "rotuloDesfavoravel",
    ),
    "sections": ("title", "order", "type", "content", "source"),
    # A ordem é a da lista: o conteúdo publica os Anexos na ordem editorial, e a conferência os
    # mostra nela.
    "attachments": ("label", "order"),
    "documentRequirements": (
        "name",
        "instructions",
        "required",
        "order",
        "profileId",
        "modalityId",
        "attachmentId",
        "modalityCode",
    ),
}
LIDOS = frozenset(
    (colecao, caminho) for colecao, caminhos in _LIDOS_POR_COLECAO.items() for caminho in caminhos
)

_IDENTIDADE = (
    "identidade: é o que as outras declarações referenciam, e a conferência a mostra resolvida no "
    "nome de quem é referenciado"
)
_REGRA_DO_METODO = (
    "o identificador que a máquina aplica; a conferência mostra a frase publicada (`text`), que "
    "é o que o documento imprime e o que a pessoa lê"
)
_SEM_CONSUMIDOR = (
    "a composição não o pede e nenhum consumidor o lê; decide-se na spec que o consumiria (ordem "
    "adotada em 27/09, passos 1 e 3)"
)
_OPACO = (
    "objeto opaco (026): a composição não o escreve, só o preserva, e o documento não o imprime"
)

#: O que a conferência **não** mostra, e por quê. Cada entrada é decisão escrita: "esqueci" não
#: cabe numa razão.
NAO_MOSTRADOS = {
    (RAIZ, "schemaVersion"): (
        "a versão do formato canônico diz como o conteúdo se lê, e não o que o Edital declara"
    ),
    (RAIZ, "editalId"): _IDENTIDADE,
    (RAIZ, "processoId"): _IDENTIDADE,
    (RAIZ, "drawMethod/normalization/rule"): _REGRA_DO_METODO,
    (RAIZ, "drawMethod/substitutionRule/rule"): _REGRA_DO_METODO,
    ("profiles", "id"): _IDENTIDADE,
    ("profiles", "classificationInformation"): _OPACO,
    ("profiles", "callInformation"): _OPACO,
    ("competitionModalities", "id"): _IDENTIDADE,
    ("competitionModalities", "normativeRule/id"): _IDENTIDADE,
    ("competitionModalities", "normativeRule/calculation"): _SEM_CONSUMIDOR,
    ("competitionModalities", "normativeRule/rounding"): _SEM_CONSUMIDOR,
    ("competitionModalities", "normativeRule/distribution"): _SEM_CONSUMIDOR,
    ("competitionModalities", "normativeRule/callRules"): _SEM_CONSUMIDOR,
    ("vacancyTable", "id"): _IDENTIDADE,
    ("declaredFacts", "id"): _IDENTIDADE,
    ("classificationMilestones", "id"): _IDENTIDADE,
    ("classificationMilestones", "code"): (
        "nasce do código do Perfil (030, FR-420), e a conferência agrupa os marcos pelo Perfil a "
        "que pertencem"
    ),
    ("classificationMilestones", "drawMethod/normalization/rule"): _REGRA_DO_METODO,
    ("classificationMilestones", "drawMethod/substitutionRule/rule"): _REGRA_DO_METODO,
    ("tiebreakers", "id"): _IDENTIDADE,
    ("schedule", "id"): _IDENTIDADE,
    ("schedule", "status"): (
        "derivado das datas e do instante corrente (045, D-001); a conferência mostra as datas, "
        "que são a declaração"
    ),
    ("stages", "id"): _IDENTIDADE,
    ("sections", "id"): _IDENTIDADE,
    ("sections", "key"): "identidade da seção no catálogo; a conferência mostra o título",
    ("attachments", "id"): _IDENTIDADE,
    ("attachments", "artifactId"): (
        "o endereço dos bytes, que a conferência entrega pelo caminho de abrir o arquivo (020, "
        "FR-018), e não imprime"
    ),
    ("attachments", "artifactHash"): (
        "o resumo dos bytes, derivado deles: conferir é abrir o arquivo, e não ler o resumo"
    ),
    ("documentRequirements", "id"): _IDENTIDADE,
    ("documentRequirements", "key"): (
        "identidade do documento exigido; a conferência mostra o nome"
    ),
}


# Os dois momentos, ditos como quem revisa precisa lê-los. **Não é o código**: `AT_ENROLLMENT` não
# diz nada a quem confere um Edital antes de publicá-lo.
_QUANDO = {
    nomes_do_requerimento.NA_INSCRICAO: "no ato da inscrição",
    nomes_do_requerimento.NA_CONVOCACAO: "quando o candidato for convocado",
}


def _requerimento_de_matricula(snapshot):
    """O que o Edital passou a exigir do candidato — e o texto que ele vai aceitar (029, T046).

    **Quem revisa antes de publicar um ato imutável precisa ver isto.** Sem o bloco, a única
    confirmação do texto da declaração seria a tela onde ele foi digitado: quem conferisse o Edital
    na Revisão publicaria sem nunca reler o que o candidato vai ter de aceitar — e depois da
    publicação a correção não é digitar de novo, e sim Retificar.

    **O bloco some quando o Edital não declara**, e é o certo: uma linha dizendo *"não exige"* em
    todo Edital do acervo seria ruído numa tela que já é longa. A ausência de exigência é o padrão.

    **O texto aparece por extenso, e não resumido.** É norma que vai ao conteúdo publicado; cortá-lo
    com reticências faria a conferência confirmar o que ninguém leu.
    """
    declaracao = snapshot.get("matriculationRequest") or {}
    momento = declaracao.get("moment") or ""
    if not momento:
        return []
    return [
        {
            "titulo": "Requerimento de Matrícula",
            "etapa": "inscricao",
            "itens": [
                {
                    "titulo": f"Exigido {_QUANDO.get(momento, momento)}",
                    "linhas": [
                        declaracao.get("declarationText")
                        or "sem o texto da declaração — a publicação será recusada",
                    ],
                }
            ],
        }
    ]


def _identificacao(snapshot):
    linhas = [
        snapshot.get("title") or "—",
        snapshot.get("description") or "sem descrição",
    ]
    if snapshot.get("processoCode") or snapshot.get("processoTitle"):
        codigo = snapshot.get("processoCode") or "—"
        linhas.append(f"Processo {codigo} — {snapshot.get('processoTitle') or '—'}")
    return linhas


def _teto_de_inscricoes(snapshot):
    """Quantas inscrições cada candidato pode enviar, na frase do documento (RC-12).

    **Na etapa Inscrição, e não na Identificação.** Era lá que a linha morava enquanto o teto não
    tinha campo na composição, e o caminho de volta levava a uma tela onde ele não se corrigia.
    Desde que se declara junto do período, o bloco leva para lá.

    **A frase é a do PDF**, e não um rótulo com o número: quem confere antes de publicar lê o que o
    candidato vai ler. O bloco some sem teto, como o do Requerimento de Matrícula — sem limite é o
    padrão, e o documento também não diz nada.
    """
    frase = teto_de_inscricoes(snapshot)
    if frase is None:
        return []
    return [
        {
            "titulo": "Inscrições por candidato",
            "etapa": "inscricao",
            "itens": [{"titulo": frase, "linhas": []}],
        }
    ]


def blocos(snapshot, registros=None):
    """O Edital inteiro, na ordem em que se elabora, com o caminho de volta para cada etapa.

    `registros` são as linhas `APLICAR_A_TODOS` da trilha deste Edital, em ordem de ocorrência
    (051): é delas que sai a origem do que um gesto materializou.
    """
    if registros:
        snapshot = {**snapshot, _ALCANCE: origens.gestos_por_destino(registros)}
    conferencia = [
        {
            "titulo": "Identificação",
            "etapa": "identificacao",
            "itens": [
                {
                    "titulo": f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}",
                    "linhas": _identificacao(snapshot),
                }
            ],
        }
    ]
    conferencia.extend(_teto_de_inscricoes(snapshot))
    conferencia.extend(_requerimento_de_matricula(snapshot))
    for titulo, etapa, leitura in BLOCOS:
        conferencia.append({"titulo": titulo, "etapa": etapa, "itens": leitura(snapshot)})
    return conferencia


# ---- o que não se corrige depois de publicado (051, FR-936, a DP-19) ----------------------------

_ESPECIE_DO_ALVO = {
    "FIXED": "uma quantidade fixa",
    "FROM_VACANCY_TABLE": "quantas vagas o quadro publicar",
}
_CONTINUACAO = {
    "ALLOWED": "admite continuar além da faixa publicada",
    "NONE": "a faixa é o que foi publicado",
}
_TIPO_DO_CRITERIO = {
    "MAIOR_PONTUACAO_NA_ETAPA": "a maior pontuação numa Etapa",
    "MAIOR_VALOR_DE_FATO": "o maior valor de um fato",
    "MENOR_VALOR_DE_FATO": "o menor valor de um fato",
}
_QUANDO_FALTA = {
    "ULTIMO_NO_CRITERIO": "fica por último no critério",
    "CRITERIO_NAO_SE_APLICA": "o critério não se aplica",
}


def _valor_definitivo(colecao, caminho, valor, snapshot):
    """O valor de um campo definitivo como quem confere o lê — nunca o enum, nunca a identidade."""
    etapas = por_identificador(snapshot.get("stages"))

    def etapa(identidade):
        return (etapas.get(str(identidade)) or {}).get("name") or "Etapa que não existe"

    if caminho == "matriculationRequest/moment":
        return _QUANDO.get(valor, str(valor))
    if (colecao, caminho) == ("profiles", "reserveType"):
        return RESERVA.get(valor, str(valor))
    if caminho == "normativeRule/rounding":
        return quadro.em_palavras(valor)
    if (colecao, caminho) == ("declaredFacts", "type"):
        return TIPO_DO_FATO.get(valor, str(valor))
    if (colecao, caminho) == ("classificationMilestones", "stages"):
        return ", ".join(etapa(item) for item in valor) or "nenhuma"
    if caminho == "cutRule/targetKind":
        return _ESPECIE_DO_ALVO.get(valor, str(valor))
    if caminho == "cutRule/governedStage":
        return "nenhuma" if valor == "NONE" else etapa(valor)
    if caminho == "cutRule/continuation":
        return _CONTINUACAO.get(valor, str(valor))
    if (colecao, caminho) == ("tiebreakers", "type"):
        return _TIPO_DO_CRITERIO.get(valor, str(valor))
    if caminho == "parameters/stageId":
        return etapa(valor)
    if caminho == "parameters/factId":
        for perfil in snapshot.get("profiles") or []:
            for fato in perfil.get("declaredFacts") or []:
                if str(fato.get("id")) == str(valor):
                    return fato.get("code") or "—"
        return "fato que não existe"
    if caminho == "whenMissing":
        return _QUANDO_FALTA.get(valor, str(valor))
    return str(valor)


def definitivos(snapshot):
    """Os campos que este Edital declara e que não se corrigem depois de publicados (FR-936)."""
    from processo_seletivo.interface.retificacao import ROTULO_DO_EXCLUIDO

    return origens.campos_definitivos(
        snapshot, rotulos=ROTULO_DO_EXCLUIDO, em_palavras=_valor_definitivo
    )
