"""O conjunto de recortes de um marco, derivado num lugar só (034, FR-491).

**Recorte** é o par (Perfil, Modalidade de Concorrência) sobre o qual se ordena, se corta, se apura
e se convoca. O recorte **sem lista** é a ampla concorrência, e é a mesma grafia que `lista_id`
carrega em `AtoDeOrdenacao`, em `PosicaoNaOrdem`, em `ItemDoCorte` e em `ApuracaoDeOcupacao`.

**A Modalidade que o Perfil aponta como sendo a ampla não é recorte.** A quantidade dela mora na
linha geral do Quadro de Vagas; dar-lhe recorte próprio declararia duas vezes o mesmo número — e
emitiria uma ordem que a apuração não tem linha para consumir, que é um ato publicado que não leva a
lugar nenhum.

**Por que este módulo existe, e por que aqui.** A medição da `034` encontrou o mesmo fato tratado de
**três** maneiras em três módulos: a ocupação a exclui, o corte a aceita como **apelido** da linha
geral, e o sorteio lhe dá recorte próprio. Duas listas iguais hoje e derivadas em dois lugares
divergem na primeira Retificação — e foi por isso que a `FR-491` obrigou um lugar só para a
classificação e para a ocupação, que são os dois lados do mesmo ato: quem emite e quem apura.

A regra adotada é a da **ocupação**, e a escolha é verificável: é a cauda que consome a ordem.

**O sorteio ficou de fora na `034`**, com a divergência registrada em `FR-491a`, porque retirar o
recorte excedente obrigava a responder como os atos já emitidos nele continuam alcançáveis. **A
`122` é essa resposta** (FR-3893): o sorteio, a divulgação, a condução, a Supervisão e o relatório
passam a perguntar aqui, e o acervo que o sorteio produziu antes fica preservado e explicado. O
**papel** de um recorte é uma pergunta feita à versão, e não uma marca gravada no registro (a
decisão de não gravar é a D-002 da `122`).

**Vive no domínio** porque `editais/domain/validation.py` também o consome, e domínio não importa
aplicação. É a mesma direção que a `032` registrou ao colocar `emite_ordem_no_recorte` aqui.
"""

from processo_seletivo.shared.api.problems import DomainError

ROTULO_DA_AMPLA = "Ampla concorrência (linha geral do quadro)"

# **Os três papéis de um recorte numa versão** (122, `data-model.md`). Excedente é a Modalidade que
# o Perfil aponta como a ampla — e só o apontamento decide (FR-3894): o nome e o código da
# Modalidade não dizem nada, e um Edital pode ter uma "AC" que não é a ampla.
OPERACIONAL = "OPERACIONAL"
EXCEDENTE = "EXCEDENTE"
AUSENTE = "AUSENTE"

# As duas origens de um registro excedente (122, FR-3903). A frase de um sai da versão que ele cita.
NASCIDO = "NASCIDO"
TORNADO = "TORNADO"

CODIGO_DA_RECUSA = "list_is_general_competition_alias"


def frase_da_recusa(nome):
    """A frase única da recusa (122, D-003): os três comandos e as telas dizem a mesma coisa."""
    return (
        f"A Modalidade «{nome}» é a que este Perfil aponta como a ampla concorrência, e não tem "
        "recorte próprio: a ampla já reúne todos os inscritos, inclusive quem a declarou. Use o "
        "recorte da ampla concorrência."
    )


FRASE_DA_MODALIDADE_APONTADA = (
    "A Modalidade «{nome}», que este Perfil aponta como a ampla concorrência, não tem sorteio "
    "próprio: a ampla concorrência já reúne todos os inscritos, inclusive quem a declarou."
)

FRASE_DO_NASCIDO = (
    "Produzido quando o sorteio dava lista própria à Modalidade apontada como a ampla "
    "concorrência. A ocupação das vagas não usa esta lista, e ela fica preservada como foi feita."
)


def frase_do_tornado(numero):
    """A frase do registro que uma Retificação tirou da operação (122, FR-3903)."""
    retificacao = f"A Retificação nº {numero}" if numero else "Uma Retificação"
    return (
        f"Produzido quando esta Modalidade tinha recorte próprio. {retificacao} passou a apontá-la "
        "como a ampla concorrência, e desde então a ocupação das vagas não usa esta lista. O "
        "registro fica preservado como foi feito."
    )


def frase_do_papel_mudado(numero):
    """A causa de obsolescência do ato cujo recorte mudou de papel (122, FR-3912, contrato §3)."""
    retificacao = f"na Retificação nº {numero}" if numero else "numa Retificação"
    return (
        f"O papel deste recorte mudou {retificacao}: o ato foi produzido para outro universo e não "
        "vale para o recorte de hoje."
    )


def recortes_do_perfil(conteudo, *, perfil_id):
    """`[(lista_id, rótulo)]` — a ampla primeiro, as reservadas na ordem em que o Perfil as declara.

    **A ordem é estável, e isso é obrigação de contrato.** Ordem instável faria a navegação entre
    recortes trocar de lugar entre dois cliques.

    **O rótulo diz o que o recorte é.** O da ampla nomeia a linha geral; cada reservada carrega o
    código que o Edital publica. É a lição que a `021` pagou: num Edital que declara uma Modalidade
    chamada "Ampla concorrência", a tela mostrava dois blocos homônimos e quem conduz o certame não
    sabia em qual agir.

    Perfil inexistente devolve **só a ampla**, e não recusa: quem precisa de 404 pergunta pelo
    marco, e a ampla é o recorte que todo Perfil tem.
    """
    perfil = _perfil(conteudo, perfil_id)
    ampla_declarada = perfil.get("generalCompetitionModalityId")
    ampla_declarada = str(ampla_declarada) if ampla_declarada else None
    recortes = [(None, ROTULO_DA_AMPLA)]
    for modalidade in perfil.get("competitionModalities") or []:
        if not isinstance(modalidade, dict) or not modalidade.get("id"):
            continue
        identidade = str(modalidade["id"])
        if ampla_declarada and identidade == ampla_declarada:
            continue
        nome = modalidade.get("name") or identidade
        recortes.append((identidade, f"{nome} ({modalidade.get('code')})"))
    return recortes


def normalizar_recorte(conteudo, *, perfil_id, lista_id):
    """O recorte pedido, reduzido à grafia canônica — ou `not_found` quando ele não existe.

    Três respostas, e as três importam:

    - **nulo** para quem não pede recorte algum, que é a ampla concorrência;
    - **nulo também** para quem pede a Modalidade que o Perfil aponta como sendo a ampla. É a
      grafia-armadilha, e tratá-la como recorte próprio emitiria um ato que a ocupação não consome.
      Aceitar o apelido e nunca oferecê-lo é o que `classificacao/application/corte.py` já faz com a
      linha do quadro, e criar uma segunda gramática para a mesma coisa é o que a `FR-491` proíbe;
    - **recusa** para o identificador que não corresponde a Modalidade alguma do Perfil (`FR-499`).
      Recorte inexistente e recorte vazio são coisas diferentes: confundi-las esconde erro de
      digitação, e a `FR-492a` fez da ordem vazia um estado legítimo justamente para que a distinção
      exista.

    **A recusa é aqui, e não só na tela.** A porta do comando também chega a este ponto, e fechar só
    a view deixaria a emissão alcançável por quem tivesse o formulário antigo aberto — o mesmo
    raciocínio que `_recusar_marco_de_sorteio` registra.
    """
    if not lista_id:
        return None
    alvo = str(lista_id)
    perfil = _perfil(conteudo, perfil_id)
    ampla_declarada = perfil.get("generalCompetitionModalityId")
    if ampla_declarada and alvo == str(ampla_declarada):
        return None
    for lista, _ in recortes_do_perfil(conteudo, perfil_id=perfil_id):
        if lista == alvo:
            return alvo
    raise DomainError("not_found", "Recurso não encontrado.", 404)


def papel_do_recorte(conteudo, *, perfil_id, lista_id):
    """`OPERACIONAL`, `EXCEDENTE` ou `AUSENTE` — o papel daquele recorte **naquela** versão (122).

    Operacional é estar em `recortes_do_perfil`, e a definição é essa de propósito: as duas
    perguntas não podem divergir. A ampla (lista nula) é sempre operacional.
    """
    if not lista_id:
        return OPERACIONAL
    alvo = str(lista_id)
    ampla_declarada = _perfil(conteudo, perfil_id).get("generalCompetitionModalityId")
    if ampla_declarada and alvo == str(ampla_declarada):
        return EXCEDENTE
    if any(lista == alvo for lista, _ in recortes_do_perfil(conteudo, perfil_id=perfil_id)):
        return OPERACIONAL
    return AUSENTE


def exigir_recorte_operacional(conteudo, *, perfil_id, lista_id):
    """Recusa o recorte excedente na versão dada (122, FR-3897 a FR-3899).

    **A recusa é do comando, e não da tela**: a porta do comando é alcançada por formulário antigo e
    por chamada direta, e esconder o botão sozinho deixaria a lista nascer do mesmo jeito. Só o
    excedente é recusado aqui; o recorte ausente segue o que cada comando já fazia com ele, porque
    esta feature não o mede (`Registrado, sem desenvolver`, na spec).
    """
    if papel_do_recorte(conteudo, perfil_id=perfil_id, lista_id=lista_id) != EXCEDENTE:
        return
    raise DomainError(
        CODIGO_DA_RECUSA,
        frase_da_recusa(_nome_da_modalidade(conteudo, perfil_id, lista_id)),
        422,
    )


def origem_do_registro(versoes, *, perfil_id, lista_id, versao_do_registro):
    """`(NASCIDO, None)` ou `(TORNADO, numero)` para um registro excedente (122, FR-3903, FR-3911).

    `versoes` são as versões do Edital **em ordem de vigência**, como `(identidade, conteudo,
    numero)`, até a vigente; quem chama as lê uma vez para todos os registros. A frase de um
    registro depende só da versão dele e das posteriores — nunca de estado de sessão.

    O tornado nomeia a **primeira** Retificação que o tirou da operação, e não a última: um
    apontamento retirado e refeito não reescreve a história do registro (T5 da `research.md`).
    """
    alvo = str(versao_do_registro)
    vistas = list(versoes)
    indice = next((i for i, (ident, _, _) in enumerate(vistas) if str(ident) == alvo), None)
    if indice is None:
        return NASCIDO, None
    _, conteudo_de_origem, _ = vistas[indice]
    if papel_do_recorte(conteudo_de_origem, perfil_id=perfil_id, lista_id=lista_id) == EXCEDENTE:
        return NASCIDO, None
    for _, conteudo, numero in vistas[indice + 1 :]:
        if papel_do_recorte(conteudo, perfil_id=perfil_id, lista_id=lista_id) == EXCEDENTE:
            return TORNADO, numero
    return TORNADO, None


def frase_da_origem(origem, numero=None):
    return FRASE_DO_NASCIDO if origem == NASCIDO else frase_do_tornado(numero)


def retificacao_que_mudou_o_papel(versoes, *, perfil_id, lista_id, versao_do_registro):
    """O número da primeira versão posterior à do registro em que o papel do recorte mudou."""
    alvo = str(versao_do_registro)
    vistas = list(versoes)
    indice = next((i for i, (ident, _, _) in enumerate(vistas) if str(ident) == alvo), None)
    if indice is None:
        return None
    _, conteudo_de_origem, _ = vistas[indice]
    papel = papel_do_recorte(conteudo_de_origem, perfil_id=perfil_id, lista_id=lista_id)
    for _, conteudo, numero in vistas[indice + 1 :]:
        if papel_do_recorte(conteudo, perfil_id=perfil_id, lista_id=lista_id) != papel:
            return numero
    return None


def _nome_da_modalidade(conteudo, perfil_id, lista_id):
    alvo = str(lista_id)
    for modalidade in _perfil(conteudo, perfil_id).get("competitionModalities") or []:
        if isinstance(modalidade, dict) and str(modalidade.get("id")) == alvo:
            nome = modalidade.get("name") or ""
            codigo = modalidade.get("code")
            return f"{nome} ({codigo})" if codigo else nome
    return alvo


def rotulo_do_recorte(conteudo, *, perfil_id, lista_id):
    """O rótulo publicado daquele recorte, pela mesma derivação que os oferece."""
    alvo = str(lista_id) if lista_id else None
    for lista, rotulo in recortes_do_perfil(conteudo, perfil_id=perfil_id):
        if lista == alvo:
            return rotulo
    return ""


def _perfil(conteudo, perfil_id):
    alvo = str(perfil_id)
    for perfil in (conteudo or {}).get("profiles") or []:
        if isinstance(perfil, dict) and str(perfil.get("id")) == alvo:
            return perfil
    return {}


__all__ = [
    "AUSENTE",
    "CODIGO_DA_RECUSA",
    "EXCEDENTE",
    "FRASE_DA_MODALIDADE_APONTADA",
    "FRASE_DO_NASCIDO",
    "NASCIDO",
    "OPERACIONAL",
    "ROTULO_DA_AMPLA",
    "TORNADO",
    "exigir_recorte_operacional",
    "frase_da_origem",
    "frase_da_recusa",
    "frase_do_papel_mudado",
    "frase_do_tornado",
    "normalizar_recorte",
    "origem_do_registro",
    "papel_do_recorte",
    "recortes_do_perfil",
    "retificacao_que_mudou_o_papel",
    "rotulo_do_recorte",
]
