"""Os campos do Requerimento de Matrícula, do jeito que a tela precisa deles.

**Isto não é um construtor de formulários, e a distinção importa.** A lista abaixo é fixa: o Edital
decide **se** pede o requerimento e **quando** (`FR-368`), e não *quais* campos ele tem. Quem quiser
outro campo escreve spec, não configuração — é a decisão registrada na `D-002`, e este módulo existe
para descrevê-la uma vez, não para torná-la editável.

**Por que um descritor, e não vinte blocos no template.** Vinte repetições de `<div class="campo">`
divergem: uma esquece o `for`, outra o `aria-describedby`, e a rubrica de acessibilidade só acusa a
que ficar sem rótulo. Um laço sobre esta lista faz a marcação ser a mesma nos vinte.

**Os rótulos vêm do domínio, e não daqui.** `requerimentos/domain/rotulos.py` os guarda porque os
**dois** canais os leem: o candidato preenche *"Faixa de renda somada da família"* e quem conduz lê
o valor declarado sob o mesmo nome. Escrevê-los duas vezes os faria divergir na primeira correção —
e a divergência apareceria justamente numa conversa em que as duas pessoas olham telas diferentes do
mesmo dado. O que mora aqui é o que é **só desta tela**: tipo de controle, largura, `autocomplete` e
o que fecha quando o CEP é reconhecido.
"""

from dataclasses import dataclass, field

from processo_seletivo.requerimentos.domain import nomes, rotulos

TEXTO = "texto"
DATA = "data"
ESCOLHA = "escolha"
TELEFONE = "telefone"
LONGO = "longo"


@dataclass(frozen=True)
class Campo:
    nome: str
    rotulo: str
    tipo: str = TEXTO
    opcoes: tuple = ()
    # **Texto permanente abaixo do campo, e ele é caro.** Cada linha aqui empurra tudo o que vem
    # depois para baixo, e num formulário de vinte campos isso é tela de rolagem. A régua: só
    # sobrevive o que muda uma **decisão** — não o que ensina a digitar, que vai para `exemplo`.
    ajuda: str = ""
    # O exemplo de formato, **dentro** do campo. `placeholder` curto, porque 375px o corta no meio —
    # é a lição que `_consulta.html` já registra, junto com a de que ele não repete o rótulo.
    exemplo: str = ""
    # Três valores, e os três existem na folha do portal: `""` é uma coluna da grade, `curto`
    # encolhe dentro dela, e `largo` toma a linha inteira. Inventar um quarto quebraria a varredura
    # de classes órfãs — ela confere que toda classe citada tem regra escrita.
    #
    # **`largo` é para o que não cabe em meia coluna sem cortar o que a pessoa digitou**: nome
    # completo de mãe e pai, logradouro, e as opções de renda, que são frases.
    largura: str = ""
    autocomplete: str = ""
    # Somente leitura **enquanto o CEP for reconhecido** (T030). Não é o mesmo que derivado: o
    # código IBGE nunca é editável, e estes voltam a abrir quando a referência não responde.
    fecha_com_o_cep: bool = False


@dataclass(frozen=True)
class Grupo:
    titulo: str
    campos: tuple
    nota: str = ""
    campos_extras: tuple = field(default=())


def _opcoes(valores, rotulos):
    """Os pares `(valor, rótulo)` na ordem da lista fechada do domínio."""
    return tuple((valor, rotulos[valor]) for valor in valores)


SEXO = _opcoes(nomes.SEXOS, rotulos.SEXO)
NACIONALIDADE = _opcoes(nomes.NACIONALIDADES, rotulos.NACIONALIDADE)
ESTADO_CIVIL = _opcoes(nomes.ESTADOS_CIVIS, rotulos.ESTADO_CIVIL)
UF = tuple((sigla, sigla) for sigla in nomes.UFS)

# **Duas opções são ditas do lado de quem escolhe.** No dossiê, `NAO_DECLARADA` se lê *"não
# declarada"* — um fato registrado. Aqui ela é uma **escolha que se oferece**, e oferecer "não
# declarada" soaria a formulário incompleto. É a única divergência deliberada entre os dois canais,
# e ela está escrita nos dois lugares.
COR_RACA = _opcoes(
    nomes.CORES, {**rotulos.COR_RACA, nomes.COR_NAO_DECLARADA: "Prefiro não declarar"}
)
RENDA = _opcoes(
    nomes.FAIXAS_DE_RENDA, {**rotulos.RENDA, nomes.RENDA_NAO_DECLARADA: "Prefiro não declarar"}
)


def _campo(nome, **extras):
    """Um campo com o rótulo que o domínio dá a ele."""
    return Campo(nome, rotulos.ROTULOS[nome], **extras)


GRUPOS = (
    Grupo(
        "Sobre você",
        (
            _campo("data_de_nascimento", tipo=DATA, largura="curto", autocomplete="bday"),
            _campo("municipio_natal"),
            _campo("uf_natal", tipo=ESCOLHA, opcoes=UF, largura="curto"),
            # **Lista, e não mais texto livre** (`031`, `D-008`). O exemplo *"Brasileira"* que
            # estava aqui é justamente o que a lista fechada elimina: ele produzia *"Brasileira"*,
            # *"Brasil"* e *"BRASIL"* na mesma coluna.
            _campo("nacionalidade", tipo=ESCOLHA, opcoes=NACIONALIDADE, largura="curto"),
            _campo("sexo", tipo=ESCOLHA, opcoes=SEXO, largura="curto"),
            # Sem ajuda: *"as categorias são as do IBGE"* é curiosidade, e *"declarar é opcional"*
            # já está dito pela opção **Prefiro não declarar**, que a pessoa lê ao abrir a lista.
            _campo("cor_raca", tipo=ESCOLHA, opcoes=COR_RACA),
            _campo("estado_civil", tipo=ESCOLHA, opcoes=ESTADO_CIVIL, largura="curto"),
        ),
    ),
    Grupo(
        "Filiação",
        (
            _campo("nome_da_mae", largura="largo", autocomplete="off"),
            _campo("nome_do_pai", largura="largo", autocomplete="off"),
        ),
        # **A ausência é a regra, e não a exceção** (`FR-384`). Dizê-lo aqui evita que a pessoa
        # procure um documento que não existe, ou invente um nome para passar da tela.
        nota="Deixe em branco o que não constar do seu registro de nascimento.",
    ),
    Grupo(
        "Documento de identidade",
        (
            _campo("rg", largura="curto"),
            _campo("rg_orgao_emissor", largura="curto", exemplo="SSP"),
            _campo("rg_expedido_em", tipo=DATA, largura="curto"),
            # **Os três eleitorais** (`031`, `D-007`). `curto` nos três: são números de até doze
            # dígitos, e um campo de linha inteira para quatro dígitos convida a digitar outra
            # coisa. O exemplo mostra a pontuação que a pessoa vê no cartão — ela é aceita e
            # descartada na gravação, porque o que se guarda é uma forma só (`FR-387`).
            _campo("titulo_eleitoral", largura="curto", exemplo="0123 4567 8901"),
            _campo("zona_eleitoral", largura="curto", exemplo="034"),
            _campo("secao_eleitoral", largura="curto", exemplo="0128"),
        ),
        # **Nem toda pessoa tem o título em mãos, e nenhum Edital o exige para matricular.** Dizê-lo
        # aqui evita que alguém pare o preenchimento para procurar o documento.
        nota="Deixe em branco se não tiver o título de eleitor em mãos.",
    ),
    Grupo(
        "Contato",
        (_campo("telefone_celular", tipo=TELEFONE, largura="curto", autocomplete="tel"),),
    ),
    Grupo(
        "Atendimento durante o curso",
        (_campo("necessidade_especifica", tipo=LONGO, largura="largo"),),
        # **Distinto da cota de pessoa com deficiência** (`FR-385`). Colapsar os dois faria quem
        # precisa de acessibilidade achar que está declarando cota — e quem concorre pela cota
        # achar que já pediu atendimento.
        # **A única nota que cresce em vez de encolher, e a razão é o custo do mal-entendido.** Sem
        # ela, alguém declara aqui achando que está pedindo a cota — e descobre tarde demais, quando
        # a concorrência já foi decidida por outro critério. As demais notas economizam rolagem;
        # esta economiza um recurso.
        nota="Não é a cota para pessoa com deficiência, e não muda a sua concorrência: é para a "
        "instituição se preparar para receber você.",
    ),
    Grupo(
        "Renda",
        (_campo("renda_familiar_faixa", tipo=ESCOLHA, opcoes=RENDA, largura="largo"),),
        # O rótulo do campo já diz *somada da família*; o que a nota acrescenta é **inclusive a
        # sua** — que é onde a conta erra.
        nota="Some a renda de todas as pessoas do domicílio, inclusive a sua.",
    ),
    Grupo(
        "Endereço",
        (
            _campo("cep", largura="curto", autocomplete="postal-code"),
            _campo("logradouro", largura="largo", autocomplete="address-line1"),
            _campo("numero", largura="curto", exemplo="s/n"),
            _campo("complemento", largura="curto"),
            _campo("bairro"),
            _campo("municipio", fecha_com_o_cep=True),
            _campo("uf", tipo=ESCOLHA, opcoes=UF, largura="curto", fecha_com_o_cep=True),
        ),
    ),
)

CAMPOS = tuple(campo for grupo in GRUPOS for campo in grupo.campos)
POR_NOME = {campo.nome: campo for campo in CAMPOS}
