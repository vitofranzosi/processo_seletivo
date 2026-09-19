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

**O sorteio fica como está** (`D-004`), com a divergência registrada em `FR-491a`. A `021` construiu
sobre o recorte por lista decisões, telas, relações publicadas, verificadores e cadeias históricas,
e retirar o recorte excedente obriga a responder como os atos já emitidos nele continuam
alcançáveis. Ato publicado não se apaga: é desenho, e é spec própria.

**Vive no domínio** porque `editais/domain/validation.py` também o consome, e domínio não importa
aplicação. É a mesma direção que a `032` registrou ao colocar `emite_ordem_no_recorte` aqui.
"""

from processo_seletivo.shared.api.problems import DomainError

ROTULO_DA_AMPLA = "Ampla concorrência (linha geral do quadro)"


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
    "ROTULO_DA_AMPLA",
    "normalizar_recorte",
    "recortes_do_perfil",
    "rotulo_do_recorte",
]
