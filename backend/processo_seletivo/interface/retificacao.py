"""Composição de Retificação por diferença sobre o conteúdo vigente.

A Alteração Normativa do domínio é um caminho JSON Pointer com operação e valor novo. Pedir
isso a quem elabora um Edital seria transferir uma decisão de representação para quem tem um
problema administrativo. Aqui a pessoa edita o conteúdo que está vigorando, e a diferença entre
o que ela viu e o que ela deixou é traduzida nas alterações — que é o que US4 descreve como
"o conteúdo vigente ao lado da alteração proposta".

Além de alterar valores, é possível remover e acrescentar Perfis e Eventos. Isso já exigiu uma
coreografia: os REPLACE primeiro, com os índices do vigente; os REMOVE em ordem decrescente,
para que apagar um não movesse os seguintes; os ADD por último. **Ela não existe mais.** Cada
alteração nomeia a entidade de que fala, e nenhuma ordem de emissão muda o resultado.

Nada disso aparece na tela. O formulário identifica seus campos por uma **referência opaca** —
posição no formulário que o servidor acabou de gerar, não caminho normativo —, e é aqui que a
referência volta a ser caminho. Quem elabora um Edital tem um problema administrativo, não um
problema de representação (FR-019).
"""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from processo_seletivo.editais.domain import secoes as catalogo
from processo_seletivo.publicacoes.domain.changes import ABSENT, resolve_path
from processo_seletivo.shared.tempo import ZONA as ZONA_INSTITUCIONAL

# A zona institucional mora em `shared/tempo.py` desde a 018: a contagem do prazo recursal é
# domínio, e domínio não importa de `interface` (T-008).
ZONA = ZONA_INSTITUCIONAL
TEXTO, INTEIRO, INSTANTE = "texto", "inteiro", "instante"
# A `006` publicou Etapas, Seções e a Regra Normativa das modalidades, e a tela ficou para trás:
# o motor endereçava os três, a interface alcançava nenhum. Estes três tipos são o que faltava
# para descrevê-los — decimal canônico, texto longo e booleano.
DECIMAL, TEXTO_LONGO, BOOLEANO = "decimal", "texto_longo", "booleano"
# O Documento Exigido trouxe o primeiro campo que **não** é escalar digitado: `profileId` e
# `modalityId` referenciam entidades do próprio conteúdo, e `null` neles significa "sem restrição"
# (009, FR-009). Digitar UUID à mão faria um erro de digitação mudar em silêncio quem precisa
# enviar o quê — que é o que `documentos.aplicaveis` decide a partir destes dois campos.
REFERENCIA = "referencia"
# O Anexo trouxe o primeiro campo que **não é digitado nem escolhido**: o artefato é um arquivo, e
# o que a Alteração carrega é a identidade dele mais o resumo — os bytes nunca viajam dentro do ato
# (020, FR-035). O campo aparece como `<input type="file">`, e o valor que atravessa as duas fases
# do formulário é a identidade do artefato que o envio criou.
ARQUIVO = "arquivo"
# A identidade de uma linha acrescentada. Não é campo de digitar: nasce no fragmento, viaja em
# campo oculto e é o que torna a confirmação repetível (020).
OCULTO = "oculto"

# (sufixo do caminho, rótulo, tipo) — aplicado a cada Perfil e a cada Evento.
CAMPOS_PERFIL = [
    ("name", "Denominação", TEXTO),
    ("locality", "Localidade", TEXTO),
    # O que um Edital diz sobre a vaga também se corrige depois de publicado (FR-016). Sem estes
    # três, uma remuneração errada num Edital publicado exigiria chamada de API — o mesmo defeito
    # que o achado 03 da auditoria apontou para cotas, Etapas e seções.
    ("duties", "Atribuições", TEXTO_LONGO),
    ("workload", "Carga horária", TEXTO),
    ("compensation", "Remuneração", TEXTO),
    ("immediateVacancies", "Vagas imediatas", INTEIRO),
    ("reserveLimit", "Limite do Cadastro Reserva", INTEIRO),
]
CAMPOS_EVENTO = [
    ("description", "Descrição", TEXTO),
    ("startAt", "Início", INSTANTE),
    ("endAt", "Término", INSTANTE),
]
CAMPOS_RAIZ = [("title", "Título do Edital", TEXTO), ("description", "Descrição", TEXTO)]

# A modalidade sem Regra Normativa não recebe os campos dela: o caminho não existiria no
# conteúdo, e endereçá-lo seria recusado por caminho inexistente. A tela oferece exatamente o
# que a gramática admite.
CAMPOS_MODALIDADE = [("name", "Denominação", TEXTO), ("description", "Descrição", TEXTO)]
CAMPOS_REGRA = [
    ("normativeRule/percentage", "Percentual (%)", DECIMAL),
    ("normativeRule/foundation", "Fundamento normativo", TEXTO),
    ("normativeRule/version", "Versão do fundamento", TEXTO),
]
# O marco não oferece `stages` nem `operation` como texto livre: a primeira é lista de identidades
# e a segunda é escolha entre formas que o motor sabe executar — retificá-las por caixa de texto
# publicaria regra que o cálculo não interpreta. O que a tela alcança aqui é o rótulo.
CAMPOS_MARCO = [("name", "Denominação do marco", TEXTO)]
# **O tipo do fato não está aqui, e a ausência é a regra.** Um fato declarado como data que virasse
# número não é o mesmo fato: reinterpretar o valor já congelado seria o sistema decidindo o que a
# pessoa quis dizer. Mudar o tipo é remover um fato e acrescentar outro, e o que foi congelado sob
# o primeiro permanece legível sob a norma que o governou (015, FR-058).
CAMPOS_FATO = [("label", "Rótulo exibido ao candidato", TEXTO)]
# **A ordem é o campo que importa retificar.** Ela é a norma: reordenar critérios é mudar a regra, e
# é por identidade que cada um é alcançado — substituir a lista inteira perderia os identificadores
# que a própria Retificação endereça (015, FR-015).
CAMPOS_CRITERIO = [("order", "Ordem de aplicação", INTEIRO)]
# **Todos** os campos normativos da Etapa, e não os que alguém lembrou de listar. A lista estava
# incompleta desde a 012 — `maximumScore` e `evaluationsPerRegistration` ficaram de fora —, e o
# custo disso é publicar regra que afeta direito e só se corrige pela API (D-008.10). Fica fora o
# que não é norma: `id` é identidade, `order` é insumo da progressão e `scheduleEventId` é vínculo
# endereçado pela coleção do Cronograma. `tests/contract/test_retificacoes_api.py` guarda a lista
# contra o próximo campo que nascer.
CAMPOS_ETAPA = [
    ("name", "Nome da Etapa", TEXTO),
    ("weight", "Peso", DECIMAL),
    ("minimumScore", "Nota mínima", DECIMAL),
    ("maximumScore", "Pontuação máxima", DECIMAL),
    ("evaluationsPerRegistration", "Avaliações por inscrição", INTEIRO),
    ("eliminatory", "Eliminatória", BOOLEANO),
    ("classificatory", "Classificatória", BOOLEANO),
    ("forma", "Forma da conclusão", TEXTO),
    ("rotuloFavoravel", "Rótulo do resultado favorável", TEXTO),
    ("rotuloDesfavoravel", "Rótulo do resultado desfavorável", TEXTO),
]
# Só o conteúdo. O catálogo de seções é fixo: título, ordem, tipo e origem divergentes são
# recusados pela verificação de topologia, e uma seção gerada nem campo de conteúdo tem.
CAMPOS_SECAO = [("content", "Texto da seção", TEXTO_LONGO)]
# O Anexo da `020`. Rótulo e ordem editorial são escalares; o artefato é arquivo. Não há campo de
# `artifactHash` para digitar: ele é derivado do artefato enviado, e oferecê-lo faria a tela pedir
# que alguém copiasse um SHA-256 à mão — e permitiria declarar um resumo que não é o dos bytes.
CAMPOS_ANEXO = [
    ("label", "Rótulo", TEXTO),
    ("order", "Ordem editorial", INTEIRO),
    ("artifactId", "Arquivo do anexo (PDF)", ARQUIVO),
]
# E2E-004. `key` fica de fora de propósito: é a identificação estável com que a inscrição já
# submetida nomeia o arquivo enviado, e trocá-la depois de publicado desligaria o documento do que
# os candidatos mandaram. O que se corrige aqui é o que a pessoa lê e a quem o documento se aplica.
CAMPOS_DOCUMENTO = [
    ("name", "Nome", TEXTO),
    ("instructions", "Instrução ao candidato", TEXTO_LONGO),
    ("required", "Obrigatório", BOOLEANO),
    ("order", "Ordem", INTEIRO),
    ("profileId", "Exigido apenas do Perfil", REFERENCIA),
    ("modalityId", "Exigido apenas da modalidade", REFERENCIA),
    # O modelo que o Edital fornece (020, FR-020). Sem este campo, remover um Anexo apontado por um
    # requisito seria irrealizável pelo canal do ator: a regra da referência pendurada recusaria o
    # ato, e a tela não ofereceria o campo que precisa mudar junto.
    ("attachmentId", "Modelo que o Edital fornece", REFERENCIA),
]

LISTA = "lista"
# Um Perfil ou Evento acrescentado entra no snapshot publicado; precisa nascer com a mesma
# forma que `edital_snapshot` produz, e não com um subconjunto que a consulta pública quebraria.
NOVO_PERFIL = [
    ("code", "Código", TEXTO),
    ("name", "Denominação", TEXTO),
    ("locality", "Localidade", TEXTO),
    ("description", "Descrição", TEXTO),
    ("duties", "Atribuições", TEXTO_LONGO),
    ("workload", "Carga horária", TEXTO),
    ("compensation", "Remuneração", TEXTO),
    ("immediateVacancies", "Vagas imediatas", INTEIRO),
    ("reserveLimit", "Limite do Cadastro Reserva", INTEIRO),
    ("requirements", "Requisitos", LISTA),
]
NOVO_EVENTO = [
    ("type", "Tipo", TEXTO),
    ("description", "Descrição", TEXTO),
    ("startAt", "Início", INSTANTE),
    ("endAt", "Término", INSTANTE),
]
# Um Anexo acrescentado por Retificação. O arquivo entra como os demais — enviado antes, citado
# pela identidade —, e o resumo é resolvido no servidor: nem aqui nem em lugar nenhum alguém digita
# um SHA-256 (020, FR-031, FR-035).
NOVO_ANEXO = [
    ("id", "", OCULTO),
    ("label", "Rótulo", TEXTO),
    ("order", "Ordem editorial", INTEIRO),
    ("artifactId", "Arquivo do anexo (PDF)", ARQUIVO),
]


def _ler(conteudo, caminho):
    """Valor em `caminho`, ou None quando ele não resolve.

    Delega ao próprio domínio: a resolução do seletor `id=` mora lá, e uma segunda cópia dela
    aqui divergiria da primeira no dia em que a gramática mudasse.
    """
    valor = resolve_path(conteudo, caminho)
    return None if valor is ABSENT else valor


def _valor(item, chave):
    """Valor de `chave`, que pode atravessar objetos — `normativeRule/percentage`.

    A Regra Normativa é objeto dentro da modalidade, e não item de lista: o caminho até ela é
    composto por nomes de chave, e é assim que a gramática já a endereça.
    """
    atual = item
    for parte in chave.split("/"):
        if not isinstance(atual, dict):
            return None
        atual = atual.get(parte)
    return atual


def _para_formulario(valor, tipo):
    if tipo == BOOLEANO:
        return "1" if valor else "0"
    if valor is None:
        return ""
    if tipo == INSTANTE:
        return datetime.fromisoformat(str(valor)).astimezone(ZONA).strftime("%Y-%m-%dT%H:%M")
    return str(valor)


def _descrever(descricao, identificador):
    """`autodeclaracao.pdf · 3 KB`, ou uma frase honesta quando não se sabe qual arquivo era."""
    if not identificador:
        return "—"
    dito = descricao(str(identificador)) if descricao else None
    return dito or "arquivo já publicado"


def _grupo(titulo, caminho, item, campos, *, removivel=True, opcoes=None):
    opcoes = opcoes or {}
    return {
        "titulo": titulo,
        "caminho": caminho,
        "removivel": removivel,
        "campos": [
            {
                "caminho": f"{caminho}/{chave}",
                "rotulo": rotulo,
                "tipo": tipo,
                "valor": _para_formulario(_valor(item, chave), tipo),
                # Vazia em todo campo escalar, e é o que faz o `select` existir só onde há o que
                # escolher. A mesma tupla que a tela lê é a que o POST confere.
                "opcoes": tuple(opcoes.get(chave, ())),
            }
            for chave, rotulo, tipo in campos
        ],
    }


def opcoes_de_aplicabilidade(conteudo):
    """A quem um Documento Exigido pode se restringir — lido do **conteúdo publicado**.

    Não de `edital.perfis`, que é a linha de elaboração: a Retificação sabe acrescentar Perfil ao
    conteúdo sem escrever de volta ali, e oferecer as opções da elaboração deixaria de fora
    justamente o Perfil que uma Retificação anterior criou. É a mesma razão pela qual a Inscrição
    guarda `profile_id` e não uma chave estrangeira.
    """
    perfis, modalidades = [], []
    for perfil in conteudo.get("profiles") or []:
        identificador = perfil.get("id")
        if not identificador:
            continue
        rotulo_do_perfil = f"{perfil.get('code', '')} — {perfil.get('name', '')}".strip(" —")
        perfis.append((identificador, rotulo_do_perfil))
        for modalidade in perfil.get("competitionModalities") or []:
            if not modalidade.get("id"):
                continue
            rotulo = f"{modalidade.get('code', '')} — {modalidade.get('name', '')}".strip(" —")
            modalidades.append((modalidade["id"], f"{rotulo_do_perfil} · {rotulo}"))
    anexos = [
        (anexo["id"], anexo.get("label") or "sem rótulo")
        for anexo in conteudo.get("attachments") or []
        if anexo.get("id")
    ]
    return {"profileId": perfis, "modalityId": modalidades, "attachmentId": anexos}


def _referenciar(grupos):
    """Dá a cada grupo e a cada campo o nome pelo qual o formulário os chama.

    A referência é a posição no formulário — `g2c3` —, e não o caminho normativo. É a primeira
    das duas condições de FR-019: o HTML entregue não contém caminho algum. Ela vale só para o
    par requisição/resposta que a gerou, porque o POST reconstrói os mesmos grupos a partir da
    mesma versão base.
    """
    for ordem_grupo, grupo in enumerate(grupos, 1):
        grupo["referencia"] = f"g{ordem_grupo}"
        # A tela precisa saber se a linha pode ser removida sem precisar olhar o caminho — que
        # é justamente o que ela não deve receber. Seção não é removível: o catálogo é fixo, e
        # oferecer a marcação seria oferecer o que a publicação recusa.
        grupo["removivel"] = grupo["removivel"] and bool(grupo["caminho"])
        for ordem_campo, campo in enumerate(grupo["campos"], 1):
            campo["referencia"] = f"g{ordem_grupo}c{ordem_campo}"
    return grupos


def campos_editaveis(conteudo):
    """Campos que uma Retificação pode alterar, agrupados como a pessoa os enxerga.

    Cobre tudo o que o conteúdo publicado carrega e a gramática endereça. A `006` publicou
    Etapas, Seções e a Regra Normativa e não trouxe nenhuma das três para cá; corrigir uma cota
    depois de publicada exigia chamada de API, o que a Constituição não admite como jornada
    concluída.
    """
    grupos = [_grupo("Edital", "", conteudo, CAMPOS_RAIZ, removivel=False)]

    for perfil in conteudo.get("profiles") or []:
        caminho = f"/profiles/id={perfil.get('id', '')}"
        grupos.append(
            _grupo(
                f"Perfil {perfil.get('code', '')} — {perfil.get('name', '')}",
                caminho,
                perfil,
                CAMPOS_PERFIL,
            )
        )
        for modalidade in perfil.get("competitionModalities") or []:
            campos = CAMPOS_MODALIDADE + (
                CAMPOS_REGRA if isinstance(modalidade.get("normativeRule"), dict) else []
            )
            grupos.append(
                _grupo(
                    f"Modalidade {modalidade.get('code', '')} — {perfil.get('code', '')}",
                    f"{caminho}/competitionModalities/id={modalidade.get('id', '')}",
                    modalidade,
                    campos,
                )
            )
        for fato in perfil.get("declaredFacts") or []:
            grupos.append(
                _grupo(
                    f"Fato {fato.get('code', '')} — {perfil.get('code', '')}",
                    f"{caminho}/declaredFacts/id={fato.get('id', '')}",
                    fato,
                    CAMPOS_FATO,
                )
            )
        for marco in perfil.get("classificationMilestones") or []:
            base_do_marco = f"{caminho}/classificationMilestones/id={marco.get('id', '')}"
            grupos.append(
                _grupo(
                    f"Marco {marco.get('code', '')} — {perfil.get('code', '')}",
                    base_do_marco,
                    marco,
                    CAMPOS_MARCO,
                )
            )
            for criterio in marco.get("tiebreakers") or []:
                grupos.append(
                    _grupo(
                        f"Critério {criterio.get('order', '')} — marco {marco.get('code', '')}",
                        f"{base_do_marco}/tiebreakers/id={criterio.get('id', '')}",
                        criterio,
                        CAMPOS_CRITERIO,
                    )
                )

    for evento in conteudo.get("schedule") or []:
        grupos.append(
            _grupo(
                f"Evento {evento.get('order', '')} — {evento.get('type', '')}",
                f"/schedule/id={evento.get('id', '')}",
                evento,
                CAMPOS_EVENTO,
            )
        )

    for etapa in conteudo.get("stages") or []:
        grupos.append(
            _grupo(
                f"Etapa {etapa.get('order', '')} — {etapa.get('name', '')}",
                f"/stages/id={etapa.get('id', '')}",
                etapa,
                CAMPOS_ETAPA,
            )
        )

    aplicabilidade = opcoes_de_aplicabilidade(conteudo)
    for documento in conteudo.get("documentRequirements") or []:
        grupos.append(
            _grupo(
                f"Documento {documento.get('order', '')} — {documento.get('name', '')}",
                f"/documentRequirements/id={documento.get('id', '')}",
                documento,
                CAMPOS_DOCUMENTO,
                # Acrescentar e remover Documento Exigido ficam fora: acrescentar um obrigatório
                # depois de publicado torna incompleta a inscrição de quem já enviou tudo o que se
                # pedia, e o que fazer com essas pessoas é decisão normativa, não de tela.
                removivel=False,
                opcoes=aplicabilidade,
            )
        )

    for anexo in conteudo.get("attachments") or []:
        grupos.append(
            _grupo(
                # **Sem prefixo de posição.** O rótulo já é a identificação editorial completa, e
                # `Anexo 1 — ANEXO I — …` além de gaguejar introduzia um número que o sistema
                # calcula — exatamente o que a D-006 decidiu não fazer. Se a ordem mudar, o prefixo
                # mudaria e passaria a divergir do número impresso dentro do PDF.
                anexo.get("label") or "Anexo sem rótulo",
                f"/attachments/id={anexo.get('id', '')}",
                anexo,
                CAMPOS_ANEXO,
                # Removível, ao contrário do Documento Exigido: tirar um anexo da versão futura não
                # torna incompleta a inscrição de ninguém — o que ele fornecia era a **forma**, e
                # quem já enviou já enviou. Quem fica sem modelo é o requisito, e ele sobrevive
                # sem um (020, D-008, FR-024).
                removivel=True,
            )
        )

    for secao in conteudo.get("sections") or []:
        # Seção gerada não tem conteúdo próprio: ela é composta a partir do dado que a origina,
        # e é lá que se corrige.
        if secao.get("type") == catalogo.GERADA:
            continue
        grupos.append(
            _grupo(
                f"Seção {secao.get('order', '')} — {secao.get('title', '')}",
                f"/sections/id={secao.get('id', '')}",
                secao,
                CAMPOS_SECAO,
                removivel=False,
            )
        )

    return _referenciar(grupos)


def reexibir(grupos, dados):
    """Devolve os grupos com o que a pessoa digitou, para o formulário voltar como ela o deixou.

    Resolver isto aqui — e não com um filtro repetido em cada controle do template — é o que
    permite que a tela trate texto, número, instante, decimal, texto longo e booleano pelo mesmo
    caminho. O booleano é o que obriga: um `checkbox` desmarcado não é enviado, e a reexibição
    por filtro não teria como distinguir "desmarcado" de "ausente".
    """
    if dados is None:
        return grupos
    for grupo in grupos:
        grupo["marcado_para_remover"] = bool(dados.get(f"remover:{grupo['referencia']}"))
        for campo in grupo["campos"]:
            enviado = dados.get(f"campo:{campo['referencia']}")
            if enviado is not None:
                campo["valor"] = enviado
    return grupos


def _converter(bruto, tipo, rotulo, opcoes=()):
    bruto = (bruto or "").strip()
    if tipo == BOOLEANO:
        return bruto == "1"
    if bruto == "":
        return None
    if tipo == OCULTO:
        return bruto
    if tipo == ARQUIVO:
        # A identidade do artefato que o envio criou. Não há o que converter nem o que validar
        # aqui: quem a produziu foi a view, gravando os bytes que ela mesma conferiu.
        return bruto
    if tipo == REFERENCIA:
        # A tela oferece um `select`, e o `select` não é fronteira: um POST fabricado traria
        # qualquer UUID, e a verificação de publicação o aceitaria — ela confere **forma**, e um
        # UUID que não endereça Perfil algum tem a forma certa. O documento passaria a se aplicar
        # a ninguém, sem recusa em lugar nenhum (Princípio IV).
        if bruto not in {identificador for identificador, _ in opcoes}:
            raise ValueError(f"{rotulo}: a opção escolhida não existe neste Edital.")
        return bruto
    if tipo == DECIMAL:
        # **A forma canônica não é escolha de apresentação.** O conteúdo publicado materializa
        # decimais com quatro casas e sem zero à esquerda, e a verificação de publicação recusa
        # qualquer outra forma. Escrever "2" aqui produziria um conteúdo que a própria
        # Publicação rejeita — e, onde não rejeitasse, faria uma Retificação semanticamente nula
        # alterar o hash. Formatar para leitura humana é assunto da materialização, não daqui.
        try:
            return f"{Decimal(bruto.replace(',', '.')):.4f}"
        except InvalidOperation as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é um número válido.") from exc
    if tipo == INTEIRO:
        try:
            return int(bruto)
        except ValueError as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é um número inteiro.") from exc
    if tipo == INSTANTE:
        try:
            # O snapshot guarda instantes em UTC; converter mantém a comparação honesta.
            return datetime.fromisoformat(bruto).replace(tzinfo=ZONA).astimezone(UTC).isoformat()
        except ValueError as exc:
            raise ValueError(f"{rotulo}: '{bruto}' não é uma data e hora válidas.") from exc
    return bruto


def _exibir(valor, campo):
    """O que o resumo mostra — e, na referência, o rótulo, nunca o identificador.

    O resumo é o que a pessoa confirma antes de submeter a Retificação. Exibir
    `f4c1…-…` no lugar de "Todos os Perfis → AC — Ampla Concorrência" pediria que ela
    conferisse um UUID de cor, que é o mesmo que não conferir.
    """
    if campo["tipo"] != REFERENCIA:
        return _para_formulario(valor, campo["tipo"])
    if valor is None:
        return "sem restrição"
    for identificador, rotulo in campo.get("opcoes", ()):
        if identificador == valor:
            return rotulo
    return str(valor)


def _mesmo_instante(anterior, novo):
    """O campo `datetime-local` tem precisão de minuto; o snapshot guarda segundos.

    Comparar com precisão total acusava alteração em todo Evento cujo instante não terminasse
    em zero segundos: abrir a tela e não tocar em nada listava quatro mudanças inexistentes.
    Diferença abaixo de um minuto não foi a pessoa que fez — ela não tem como fazê-la.
    """
    if anterior is None or novo is None:
        return anterior == novo

    def ao_minuto(valor):
        return datetime.fromisoformat(str(valor)).replace(second=0, microsecond=0)

    return ao_minuto(anterior) == ao_minuto(novo)


def _marcados_para_remover(dados, grupos):
    """Caminhos que a pessoa marcou para remover.

    Sem ordem nenhuma: cada caminho nomeia a entidade, e apagar um não move os outros. Era
    exatamente essa a razão de a ordem decrescente existir.
    """
    return [
        grupo
        for grupo in grupos
        if grupo["removivel"] and dados.get(f"remover:{grupo['referencia']}")
    ]


def _indices_novos(dados, prefixo):
    return sorted(
        {
            chave.split("-")[2]
            for chave in dados
            if chave.startswith(f"novo-{prefixo}-") and chave.count("-") >= 3
        }
    )


def novas_para_formulario(dados, prefixo, campos):
    """Linhas acrescentadas com o que foi digitado, para reexibir depois do POST.

    Sem isto, ver o resumo devolvia um formulário sem as linhas novas e sem as marcações de
    remoção: a pessoa lia "vai remover e acrescentar" e confirmava um conjunto vazio.
    """
    return [
        {
            "indice": indice,
            "campos": [
                {
                    "chave": chave,
                    "rotulo": rotulo,
                    "tipo": tipo,
                    "valor": dados.get(f"novo-{prefixo}-{indice}-{chave}") or "",
                }
                for chave, rotulo, tipo in campos
            ],
        }
        for indice in _indices_novos(dados, prefixo)
    ]


def _linhas_novas(dados, prefixo, campos):
    """Linhas acrescentadas, agrupadas pelo índice que o servidor deu a cada uma."""
    indices = _indices_novos(dados, prefixo)
    linhas = []
    for indice in indices:
        valores = {}
        vazia = True
        for chave, rotulo, tipo in campos:
            bruto = (dados.get(f"novo-{prefixo}-{indice}-{chave}") or "").strip()
            if bruto:
                vazia = False
            if tipo == LISTA:
                valores[chave] = [linha.strip() for linha in bruto.splitlines() if linha.strip()]
            else:
                valores[chave] = _converter(bruto, tipo, rotulo)
        # Linha em branco é a que a pessoa acrescentou e desistiu de preencher.
        if not vazia:
            linhas.append(valores)
    return linhas


def _perfil_completo(valores):
    """Forma que `edital_snapshot` produz — um subconjunto quebraria a consulta pública."""
    return {
        "id": str(uuid4()),
        "code": valores.get("code") or "",
        "name": valores.get("name") or "",
        "description": valores.get("description") or "",
        "requirements": valores.get("requirements") or [],
        "immediateVacancies": valores.get("immediateVacancies") or 0,
        "reserveType": "NONE",
        "reserveLimit": valores.get("reserveLimit"),
        "locality": valores.get("locality") or "",
        # Os três **precisam** estar aqui, ainda que vazios: a forma tem de ser a que
        # `edital_snapshot` produz, e um Perfil acrescentado por Retificação sem estas chaves seria
        # conteúdo de versão 3 incompleto — exatamente o que o docstring acima existe para impedir.
        "duties": valores.get("duties") or "",
        "workload": valores.get("workload") or "",
        "compensation": valores.get("compensation") or "",
        "classificationInformation": {},
        "callInformation": {},
        "competitionModalities": [],
        # As duas da versão 7, pelo mesmo motivo do comentário acima: um Perfil acrescentado por
        # Retificação sem elas nasceria com a forma da versão 6, e o guarda de
        # `test_perfil_acrescentado_nasce_com_a_forma_do_snapshot` é justamente quem impede isso.
        "declaredFacts": [],
        "classificationMilestones": [],
    }


def _evento_completo(valores, ordem):
    return {
        "id": str(uuid4()),
        "type": valores.get("type") or "",
        "description": valores.get("description") or "",
        "startAt": valores.get("startAt"),
        "endAt": valores.get("endAt"),
        "order": ordem,
        "status": "PLANEJADO",
    }


def _anexo_completo(valores, resumo_do_artefato):
    """Forma que `edital_snapshot` produz. Um subconjunto quebraria a validação da coleção.

    O resumo vem do artefato, e não do formulário: é a mesma razão da substituição — ninguém digita
    SHA-256, e permitir declará-lo deixaria alguém afirmar bytes que não são os enviados.
    """
    artefato = str(valores.get("artifactId") or "")
    conferido = resumo_do_artefato(artefato) if artefato and resumo_do_artefato else None
    if not conferido:
        raise ValueError(
            "Arquivo do anexo (PDF): envie o arquivo do Anexo que está sendo acrescentado."
        )
    return {
        # **Nasce no fragmento e atravessa as duas fases.** Gerar aqui produziria identidade nova a
        # cada chamada de `diferencas`, e reenviar a confirmação — o duplo clique, o F5 — mudaria o
        # payload sob a mesma chave de idempotência: a segunda tentativa seria recusada por
        # conflito em vez de devolver a primeira.
        "id": str(valores.get("id") or uuid4()),
        "label": valores.get("label") or "",
        "order": valores.get("order") or 0,
        "artifactId": artefato,
        "artifactHash": conferido,
    }


def diferencas(conteudo, dados, *, resumo_do_artefato=None, descricao_do_artefato=None):
    """Alterações Normativas derivadas do que mudou entre o vigente e o que foi submetido.

    **A ordem de emissão deixou de ser a garantia de correção.** Cada alteração nomeia a
    entidade de que fala, então remover um Perfil não move os outros e nenhuma sequência produz
    resultado diferente de outra. A ordem abaixo é a que fica legível no resumo, e só isso.

    `resumo_do_artefato` é uma **função**, e não um dicionário, e a diferença é o defeito que ela
    corrige. O formulário tem duas fases — conferir e confirmar —, e o arquivo só existe na
    primeira: um mapa montado no envio volta vazio na confirmação, e a Alteração seria gravada com
    resumo em branco, para ser recusada na publicação pela própria verificação de integridade.
    Resolver por função faz o resumo ser lido do artefato nas duas fases, **no servidor**, e nunca
    trafegar por campo oculto — que o navegador poderia trocar.

    `descricao_do_artefato` é outra função, pela mesma razão, e serve ao resumo: sem ela a linha
    dizia "arquivo anterior → arquivo novo", que não permite a ninguém notar que escolheu o arquivo
    errado — e a conferência existe exatamente para isso (POLISH020-005).

    Substituir o artefato emite **duas** alterações — identidade e resumo —, porque o conteúdo
    publicado carrega as duas e uma sem a outra deixaria a versão afirmando bytes que não são os
    que ela entrega (020, FR-034, FR-035).
    """
    alteracoes, resumo = [], []
    grupos = campos_editaveis(conteudo)
    grupos_removidos = _marcados_para_remover(dados, grupos)
    removidos = [grupo["caminho"] for grupo in grupos_removidos]

    def dentro_de_removido(caminho):
        """Remover um Perfil leva junto as modalidades dele: alterá-las não teria efeito."""
        return any(
            caminho == removido or caminho.startswith(f"{removido}/") for removido in removidos
        )

    for grupo in grupos:
        # Alterar campo de linha que será removida não tem efeito e confundiria o resumo.
        if grupo["caminho"] and dentro_de_removido(grupo["caminho"]):
            continue
        for campo in grupo["campos"]:
            enviado = dados.get(f"campo:{campo['referencia']}")
            if enviado is None:
                continue
            novo_valor = _converter(
                enviado, campo["tipo"], campo["rotulo"], campo.get("opcoes", ())
            )
            anterior = _ler(conteudo, campo["caminho"])
            if campo["tipo"] == ARQUIVO:
                if not novo_valor or str(anterior) == str(novo_valor):
                    continue
                alteracoes.append(
                    {
                        "targetPath": campo["caminho"],
                        "operation": "REPLACE",
                        "newValue": str(novo_valor),
                    }
                )
                resumo_novo = resumo_do_artefato(str(novo_valor)) if resumo_do_artefato else None
                if not resumo_novo:
                    raise ValueError(
                        f"{campo['rotulo']}: o arquivo enviado não foi encontrado. Envie-o "
                        "novamente."
                    )
                alteracoes.append(
                    {
                        "targetPath": campo["caminho"].replace("/artifactId", "/artifactHash"),
                        "operation": "REPLACE",
                        "newValue": resumo_novo,
                    }
                )
                resumo.append(
                    {
                        "grupo": grupo["titulo"],
                        "rotulo": campo["rotulo"],
                        # O nome e o tamanho dos dois, e não "anterior/novo": a conferência é onde
                        # um arquivo trocado por engano deveria aparecer, e era a única etapa que
                        # não permitia notá-lo (POLISH020-005).
                        "antes": _descrever(descricao_do_artefato, anterior),
                        "depois": _descrever(descricao_do_artefato, novo_valor),
                    }
                )
                continue
            if campo["tipo"] == INSTANTE:
                if _mesmo_instante(anterior, novo_valor):
                    continue
            elif str(anterior if anterior is not None else "") == str(
                novo_valor if novo_valor is not None else ""
            ):
                continue
            alteracoes.append(
                {"targetPath": campo["caminho"], "operation": "REPLACE", "newValue": novo_valor}
            )
            resumo.append(
                {
                    "grupo": grupo["titulo"],
                    "rotulo": campo["rotulo"],
                    "antes": _exibir(anterior, campo) or "—",
                    "depois": _exibir(novo_valor, campo) or "—",
                }
            )

    for grupo in grupos_removidos:
        atual = _ler(conteudo, grupo["caminho"]) or {}
        nome = atual.get("name") or atual.get("type") or atual.get("code")
        alteracoes.append({"targetPath": grupo["caminho"], "operation": "REMOVE"})
        resumo.append(
            {
                # O título do grupo já nomeia a entidade em qualquer coleção; derivar o rótulo
                # do prefixo do caminho errava para modalidade, que também começa em /profiles.
                "grupo": grupo["titulo"],
                "rotulo": "Remoção",
                "antes": nome or "—",
                "depois": "removido do Edital",
            }
        )

    for valores in _linhas_novas(dados, "perfil", NOVO_PERFIL):
        alteracoes.append(
            {
                "targetPath": "/profiles/-",
                "operation": "ADD",
                "newValue": _perfil_completo(valores),
            }
        )
        resumo.append(
            {
                "grupo": f"Perfil {valores.get('code') or ''}".strip(),
                "rotulo": "Acréscimo",
                "antes": "—",
                "depois": valores.get("name") or "novo Perfil",
            }
        )

    for valores in _linhas_novas(dados, "anexo", NOVO_ANEXO):
        alteracoes.append(
            {
                "targetPath": "/attachments/-",
                "operation": "ADD",
                "newValue": _anexo_completo(valores, resumo_do_artefato),
            }
        )
        resumo.append(
            {
                "grupo": f"Anexo {valores.get('order') or ''}".strip(),
                "rotulo": "Acréscimo",
                "antes": "—",
                "depois": valores.get("label") or "novo Anexo",
            }
        )

    # **O vínculo não sobrevive ao alvo** (020, FR-022). Remover o Anexo sem desfazer a referência
    # deixaria o conteúdo com um requisito apontando o que aquela versão não publica, e a validação
    # recusaria o ato inteiro — a pessoa veria a recusa e não teria como resolvê-la, porque tirar o
    # anexo e soltar o vínculo são coisas que ela faria no mesmo lugar.
    #
    # A alteração é emitida **e aparece no resumo**: desfazer em silêncio seria o sistema decidindo
    # conteúdo normativo sem dizer.
    #
    # **E só quando ninguém já decidiu por aquele caminho.** A T065 pôs o vínculo na tela, então a
    # pessoa pode remover o Anexo A e escolher o B no mesmo ato — e as duas alterações cairiam
    # sobre o mesmo caminho, com a automática por último, apagando a escolha. Quem decide é quem
    # compõe; o automático existe para o caso em que ninguém decidiu.
    ja_endereçados = {alteracao["targetPath"] for alteracao in alteracoes}
    anexos_removidos = {
        caminho.split("id=", 1)[-1]
        for caminho in removidos
        if caminho.startswith("/attachments/id=")
    }
    for documento in conteudo.get("documentRequirements") or []:
        vinculo = str(documento.get("attachmentId") or "")
        caminho_do_vinculo = f"/documentRequirements/id={documento.get('id', '')}/attachmentId"
        if caminho_do_vinculo in ja_endereçados:
            continue
        if vinculo and vinculo in anexos_removidos:
            alteracoes.append(
                {
                    "targetPath": caminho_do_vinculo,
                    "operation": "REPLACE",
                    "newValue": None,
                }
            )
            resumo.append(
                {
                    "grupo": f"Documento {documento.get('name', '')}".strip(),
                    "rotulo": "Modelo que o Edital fornece",
                    "antes": "o Anexo removido",
                    "depois": "não fornece modelo",
                }
            )

    eventos_removidos = [caminho for caminho in removidos if caminho.startswith("/schedule/")]
    proxima_ordem = len(conteudo.get("schedule") or []) - len(eventos_removidos)
    for deslocamento, valores in enumerate(_linhas_novas(dados, "evento", NOVO_EVENTO)):
        alteracoes.append(
            {
                "targetPath": "/schedule/-",
                "operation": "ADD",
                "newValue": _evento_completo(valores, proxima_ordem + deslocamento + 1),
            }
        )
        resumo.append(
            {
                "grupo": f"Evento {valores.get('type') or ''}".strip(),
                "rotulo": "Acréscimo",
                "antes": "—",
                "depois": valores.get("description") or "novo Evento",
            }
        )

    return alteracoes, resumo
