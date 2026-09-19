"""Apresentação de valores do domínio. Nenhuma regra aqui — só como o dado é lido."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django import template
from django.http import QueryDict
from django.utils import timezone

register = template.Library()

# Edital e Processo usam a forma masculina; Retificação, a feminina. Sem as duas, a trilha
# de auditoria mistura "Em revisão → HOMOLOGADA" com o código cru na tela.
SITUACOES = {
    "EM_ELABORACAO": "Em elaboração",
    "EM_REVISAO": "Em revisão",
    "HOMOLOGADO": "Homologado",
    "HOMOLOGADA": "Homologada",
    "PUBLICADO": "Publicado",
    "PUBLICADA": "Publicada",
    "ENCERRADO": "Encerrado",
    "CANCELADO": "Cancelado",
    "CANCELADA": "Cancelada",
    "ATIVO": "Ativo",
}


@register.filter
def situacao(valor):
    return SITUACOES.get(valor, valor)


@register.simple_tag
def recusa_de(recusas, prefixo, indice, campo, sub=None):
    """A mensagem de recusa daquele controle, ou vazio.

    Existe como tag, e não como filtro, porque o `id` do controle é composto de três partes —
    `perfil-3-reserveLimit` — e `{% include ... with alvo="perfil-{{ indice }}-..." %}` não
    interpola: dentro de uma tag, `{{ }}` é texto literal, e o alvo nunca casaria.

    `sub` é a quarta parte, e existe para as coleções aninhadas no Perfil, cujo controle se chama
    `linha-3-1-immediateVacancies`. Sem ela, a recusa que o domínio ancora na **linha** só teria
    onde aparecer no resumo, e quem compõe um Edital de sete polos teria de procurar em qual deles
    o número não fecha (025, E2E25-003).
    """
    partes = [prefixo, str(indice)] + ([str(sub)] if sub is not None else []) + [campo]
    return (recusas or {}).get("-".join(partes), "")


@register.filter
def dicionario_simples(dados, chave):
    """Valor de uma chave — o que o template não consegue fazer sozinho.

    Existe para `_recusa.html` ler a mensagem daquele campo entre as recusas da tela.
    """
    return (dados or {}).get(chave, "")


@register.filter
def rotulo_do_ato(chave):
    """O nome humano do ato praticado, lido da tabela que já o declara.

    A faixa dizia "Ato registrado: submeter." porque passava a chave pelo filtro `situacao`, que
    mapeia **situações** — `submeter` não está lá, e o filtro devolve o que não conhece. A trilha
    de auditoria, ao lado, sempre escreveu "Submissão para revisão" corretamente: o rótulo existia
    e não era consultado.
    """
    from processo_seletivo.interface import atos, atos_processo, atos_retificacao

    for tabela in (atos.ATOS, atos_retificacao.ATOS, atos_processo.ATOS):
        ato = tabela.get(valor := str(chave))
        if ato is not None:
            return ato.rotulo
    return SITUACOES.get(valor, valor)


@register.filter
def dicionario(dados, referencia):
    """Lê `campo:<referência>` do que foi enviado, para reexibir sem perder o digitado.

    A referência é a posição do campo no formulário, não o caminho normativo: a tela de
    Retificação não expõe representação a quem elabora (FR-019).
    """
    return dados.get(f"campo:{referencia}", "") if dados else ""


@register.filter
def plural(quantidade, formas):
    """Plural em português não se resolve com sufixo: Edital vira Editais, não Editalis."""
    singular, _, plural_ = str(formas).partition(",")
    return singular if quantidade == 1 else (plural_ or singular)


@register.filter
def marcado(dados, referencia):
    """A marcação de remoção precisa voltar marcada depois do POST, como os campos digitados."""
    return bool(dados and dados.get(f"remover:{referencia}"))


BASES_DE_AUTORIZACAO = {
    "comissao:presidir": "presidência desta comissão",
    "comissao:gerir": "permissão de gerir comissões",
}


@register.filter
def base_de_autorizacao(permissao):
    """O nome humano da base que autorizou o ato (011, FR-016).

    A trilha guarda o codename porque é ele que identifica a base sem ambiguidade; quem lê a
    tela precisa da frase. Permissão desconhecida cai no próprio codename, que é melhor do que
    esconder de onde veio a autorização.
    """
    return BASES_DE_AUTORIZACAO.get(permissao, permissao)


@register.simple_tag(takes_context=True)
def pagina_seguinte(context, cursor):
    """O endereço da próxima página **carregando os filtros da atual**.

    Um link que leva só o cursor descarta o filtro no primeiro clique: a pessoa filtra por
    avaliador, folheia, e a segunda página traz a trilha inteira sob o rótulo do filtro que ela
    escolheu. Mostrar atos de terceiros sob um filtro é pior que não paginar.
    """
    pedido = context.get("request")
    parametros = pedido.GET.copy() if pedido is not None else QueryDict(mutable=True)
    parametros["cursor"] = cursor
    return f"?{parametros.urlencode()}"


@register.filter
def pontuacao(valor):
    """A nota como uma pessoa a escreve: `60`, `87,5`, `60,005`.

    O campo guarda quatro casas porque a norma pode exigi-las, e a tela mostrava `60.0000` — que é
    o valor certo apresentado como saída de máquina. Zeros à direita não informam nada e ainda
    fazem a coluna parecer mais precisa do que a nota é; o ponto decimal em português é vírgula.

    Nada é arredondado: o que sai é exatamente o que está gravado, sem os zeros que não dizem nada.
    """
    if valor in (None, ""):
        return "—"
    try:
        exato = Decimal(str(valor)).normalize()
    except (TypeError, ValueError, InvalidOperation):
        return valor
    # `normalize()` transforma 100.0000 em 1E+2; `quantize` desfaz isso sem reintroduzir zeros.
    if exato == exato.to_integral_value():
        exato = exato.quantize(Decimal(1))
    return f"{exato:f}".replace(".", ",")


@register.filter
def instante(valor):
    """O instante que vem do conteúdo publicado, lido no fuso institucional.

    O snapshot materializa cada instante como texto ISO em UTC, e é assim que ele chega ao
    template: `2026-09-06T18:43:10.761405+00:00`, na tabela de proveniência que sustenta a
    resposta a um recurso. O filtro `date` do Django não o alcança — ele espera um `datetime`, e
    diante de texto devolve vazio —, então a data ficava crua, em UTC e em notação de máquina, na
    mesma tela em que todas as outras já saem em `06/09/2026 15:43` (E2E17-003).

    Só apresentação: nada aqui decide fuso institucional por conta própria — `localtime` lê o que
    as configurações declaram, como o resto do sistema.
    """
    if valor in (None, ""):
        return ""
    momento = valor
    if not isinstance(momento, datetime):
        try:
            momento = datetime.fromisoformat(str(valor))
        except (TypeError, ValueError):
            return valor
    if timezone.is_aware(momento):
        momento = timezone.localtime(momento)
    return momento.strftime("%d/%m/%Y %H:%M")


@register.filter
def declarou(dados, prefixo):
    """Se alguma chave com este prefixo tem valor — "este bloco foi preenchido".

    Existe para o disclosure progressivo do marco classificatório: um bloco fechado sobre conteúdo
    já declarado é uma armadilha — quem reabre o Edital não veria o corte que alguém publicou —, e
    a alternativa em template seria um `{% if %}` de dez termos repetido em cada bloco, que se
    desatualiza na primeira coluna nova sem que nada avise.

    O prefixo, e não a lista de campos, **porque o achatamento já usa prefixo**: `_metodo_para_
    exibicao` devolve `drawAlgorithm`, `drawSource`, e assim por diante. Campo novo no método entra
    aqui sem que ninguém precise lembrar.
    """
    return any(
        valor not in (None, "", [], {})
        for chave, valor in (dados or {}).items()
        if chave.startswith(prefixo)
    )


@register.filter
def ordena_por_sorteio(marco):
    """Este marco, como a tela o tem agora, ordena por sorteio? (030, FR-414)

    A **regra** mora em `editais/domain/marcos`, e não aqui: ela é a mesma que a validação e os
    serializers aplicam, e duplicá-la no template seria a segunda resposta para a pergunta que a
    FR-413 existe para tornar única. O que este filtro faz é traduzir a forma do formulário — em
    que o método viaja achatado, `drawAlgorithm` e companhia — para os dois argumentos da regra.
    """
    from processo_seletivo.editais.domain import marcos

    return marcos.ordena_por_sorteio(
        (marco or {}).get("orderProduction") or "",
        metodo_declarado=declarou(marco, "draw"),
    )


@register.filter
def pergunta_a_combinacao(marco):
    """A tela pergunta como as pontuações se combinam? Só com duas ou mais Etapas (FR-415)."""
    from processo_seletivo.editais.domain import marcos

    return marcos.pergunta_a_combinacao((marco or {}).get("etapas"))


@register.filter
def combinacao_efetiva(marco):
    """`{"operation": …, "normalization": …}` — o que este marco aplica agora (030, FR-416).

    Existe para os campos ocultos que carregam a combinação quando a tela deixa de perguntá-la: o
    valor precisa ser o declarado, quando há, e o derivado quando não há. A regra está em
    `editais/domain/marcos`; aqui só se lê o marco do formulário.
    """
    from processo_seletivo.editais.domain import marcos

    marco = marco or {}
    return marcos.combinacao_efetiva(
        operacao=marco.get("operation") or "",
        normalizacao=marco.get("normalization") or "",
        etapas=marco.get("etapas"),
    )


@register.filter
def pontuacao_e_a_da_etapa(marco):
    """A frase de FR-416 é verdadeira sobre este marco?"""
    from processo_seletivo.editais.domain import marcos

    efetiva = combinacao_efetiva(marco)
    return marcos.pontuacao_combinada_e_a_da_etapa(
        operacao=efetiva["operation"], normalizacao=efetiva["normalization"]
    )


@register.simple_tag
def escolhas_do_metodo(campo, declarado):
    """As opções de um campo fechado do método, e o valor que veio da origem (035, FR-511).

    **Existe como tag, e não como contexto de view, porque são três telas que desenham o método** —
    o passo da Classificação, o fragmento que acrescenta um marco e o fragmento que o recompõe — e
    um quarto ponto de renderização apareceria sem as listas, com os `select` vazios. Foi o que a
    `030` registrou ao acrescentar `etapas_classificatorias` aos fragmentos: *"sem as listas, a
    linha nova nasceria com os selects vazios"*. Aqui o esquecimento não é possível, porque a lista
    é pedida pelo próprio template que a usa.

    A origem do vocabulário é **uma só** — `forms.opcoes_do_metodo`, que a Retificação também lê.

    **O valor de fora do vocabulário entra na lista, selecionado** (`FR-511`). O caminho por onde
    ele chega é o rascunho criado a partir de Edital anterior: se o vocabulário encolheu desde a
    publicação de origem, um `select` que só oferecesse o de hoje faria o campo parecer **vazio**
    num Edital que o declarou — e a gravação seguinte publicaria a ausência como se alguém a
    tivesse escolhido.

    **E ele entra SEM `disabled`, que foi a primeira tentativa e estava errada.** Medido no
    navegador: um `<option selected disabled>` dá `select.value == "HERDADO"` e
    `new FormData(form).get(campo) == null` — o valor **não é submetido**. Desabilitar para impedir
    a escolha teria produzido exatamente a perda que a `FR-511` existe para impedir, e nenhum teste
    de Python a pegaria: eles afirmam sobre o HTML renderizado, e não sobre o que o navegador envia.
    É a mesma armadilha que `test_round_trip_do_rascunho.py` já registrou por escrito — *"campo
    `disabled` não é submetido pelo navegador: seria a perda que este contrato impede"*.

    **O que impede que ele seja escolha válida é outra coisa, e ela já existia**: o rótulo diz que
    o sistema não o executa, e `_validar_algoritmo_publicado` recusa ao gravar. O valor sobrevive à
    travessia, e quem o mantiver lê por que ele não serve.
    """
    from processo_seletivo.interface.forms import opcoes_do_metodo

    publicadas = opcoes_do_metodo().get(campo, ())
    declarado = str(declarado or "")
    escolhas = [
        {
            "valor": valor,
            "rotulo": rotulo,
            "selecionado": valor == declarado,
            "de_origem": False,
        }
        for valor, rotulo in publicadas
    ]
    if declarado and declarado not in {valor for valor, _ in publicadas}:
        escolhas.append(
            {
                "valor": declarado,
                "rotulo": f"{declarado} — veio do Edital de origem, e este sistema não o executa",
                "selecionado": True,
                "de_origem": True,
            }
        )
    return escolhas


@register.filter
def enumeradas_sem_peso(etapas_classificatorias, marco):
    """As Etapas que **este** marco enumera e que ainda não declaram peso (037, `FR-551`).

    **Filtro, e não campo pronto no contexto**, porque o cruzamento depende de dois lados que
    mudam em tempos diferentes: a lista de Etapas é do Edital e vem da view; a seleção é do marco
    e vem do formulário, reconstruída a cada mudança pelo fragmento recomposto. Montar o
    cruzamento na view obrigaria os **quatro** pontos que servem a lista a repeti-lo, e o que a
    `034` mediu é que três se lembram e um esquece.

    A pergunta "tem peso?" não é respondida aqui: ela chega pronta, como `tem_peso`, de quem lê a
    Etapa. Este filtro só cruza — e por isso não há segunda verdade sobre o peso.

    **Lista vazia não escreve nada**, e é isso que faz a frase do cartão ser aviso derivado do
    estado e não ajuda instrucional (`FR-554a`): declarado o peso, a cobrança some sozinha.
    """
    enumeradas = {str(identidade) for identidade in (marco or {}).get("etapas") or []}
    return [
        etapa
        for etapa in (etapas_classificatorias or [])
        if str(etapa.get("id")) in enumeradas and not etapa.get("tem_peso")
    ]


@register.filter
def conducao_da_lista(itens):
    """A condução comum a estas pendências, para ser dita **uma vez** (037, `FR-542`).

    **O dado é por item, e a fala é da lista.** Quem monta as pendências responde, item a item, se
    quem lê consegue resolver aquela — e a resposta é a mesma para todas, porque o predicado é do
    par Edital×ator. Impressa dentro do laço, a mesma frase saía três vezes seguidas na Revisão,
    que é ruído exatamente na tela que a auditoria já acusa de densa.

    **Colher em vez de recalcular** é o que mantém a derivação única: a condição de quando falar
    continua sendo a de quem montou a lista — só as pendências que têm onde se resolver a carregam
    —, e este filtro não a reescreve.
    """
    for item in itens or []:
        if item.get("conducao"):
            return item["conducao"]
    return ""
