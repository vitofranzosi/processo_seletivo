"""Como cada campo do requerimento se chama, e como cada valor se lê — dito **uma vez**.

**Dois canais leem a mesma coisa, e por isso os rótulos não moram em nenhum dos dois.** O candidato
preenche *"Faixa de renda"* no portal; quem conduz lê o valor declarado no dossiê. Se cada canal
escrevesse o seu rótulo, os dois divergiriam na primeira correção — e a divergência apareceria
justamente numa conversa em que as duas pessoas estão olhando telas diferentes do mesmo dado.

**Por que isto é domínio e não apresentação.** O rótulo da faixa de renda **é normativo**: ele diz,
por extenso, que a faixa mede a **soma da família**, enquanto a coluna de destino significa valor
por pessoa. A divergência é conhecida e decidida (`FR-412`, `R-7`), e escrever só "Renda familiar"
propagaria por ambiguidade de redação aquilo que a decisão existe para conter. Um rótulo que carrega
regra não é decoração.

**O que este módulo não tem**: largura, tipo de controle, `autocomplete`, ordem de tabulação. Isso é
de cada canal, e mora com ele — em `portal/requerimento.py` para quem preenche.

**A lista é fechada, e o Edital não a configura.** Ele liga e agenda (`D-002`); quais campos existem
é decisão de domínio, escrita em spec. A ausência de qualquer mecanismo de configuração aqui é o que
mantém essa recusa real.
"""

from processo_seletivo.requerimentos.domain import nomes

# --- Rótulos de campo ---------------------------------------------------------------------------
ROTULOS = {
    "data_de_nascimento": "Data de nascimento",
    "municipio_natal": "Município onde nasceu",
    "uf_natal": "UF onde nasceu",
    "nacionalidade": "Nacionalidade",
    "sexo": "Sexo",
    "cor_raca": "Cor ou raça",
    "estado_civil": "Estado civil",
    "nome_da_mae": "Nome da mãe",
    "nome_do_pai": "Nome do pai",
    "rg": "Número do documento de identidade",
    "rg_orgao_emissor": "Órgão emissor",
    "rg_expedido_em": "Data de expedição",
    "telefone_celular": "Telefone celular",
    "necessidade_especifica": "Necessidade específica de atendimento",
    # **O rótulo diz o que a faixa mede.** Ver a razão no topo do módulo.
    "renda_familiar_faixa": "Faixa de renda somada da família",
    "cep": "CEP",
    "logradouro": "Rua, avenida ou logradouro",
    "numero": "Número",
    "complemento": "Complemento",
    "bairro": "Bairro",
    "municipio": "Município",
    "uf": "UF",
    "codigo_ibge": "Código IBGE do município",
}

# --- Rótulos de valor ---------------------------------------------------------------------------
# **`NAO_DECLARADA` aparece como *"prefiro não declarar"* para quem preenche e como *"não
# declarada"* para quem lê.** São a mesma coisa ditas do lado certo: a primeira é uma escolha que se
# oferece; a segunda, um fato que se registra. Oferecer "não declarada" soaria a formulário
# incompleto; registrar "prefiro não declarar" poria na boca da pessoa uma frase que ela não disse.
SEXO = {nomes.FEMININO: "Feminino", nomes.MASCULINO: "Masculino"}

COR_RACA = {
    nomes.BRANCA: "Branca",
    nomes.PRETA: "Preta",
    nomes.PARDA: "Parda",
    nomes.AMARELA: "Amarela",
    nomes.INDIGENA: "Indígena",
    nomes.COR_NAO_DECLARADA: "Não declarada",
}

ESTADO_CIVIL = {
    nomes.SOLTEIRO: "Solteiro(a)",
    nomes.CASADO: "Casado(a)",
    nomes.DIVORCIADO: "Divorciado(a)",
    nomes.VIUVO: "Viúvo(a)",
}

# **Em salários mínimos, e da família inteira.** São as sete faixas do formulário institucional, na
# grafia que ele usa — mudá-las aqui tornaria incomparável o que já foi coletado em papel.
RENDA = {
    nomes.ATE_MEIO: "Até meio salário mínimo",
    nomes.DE_MEIO_A_UM: "De meio a 1 salário mínimo",
    nomes.DE_UM_A_UM_E_MEIO: "De 1 a 1,5 salário mínimo",
    nomes.DE_UM_E_MEIO_A_DOIS_E_MEIO: "De 1,5 a 2,5 salários mínimos",
    nomes.DE_DOIS_E_MEIO_A_TRES_E_MEIO: "De 2,5 a 3,5 salários mínimos",
    nomes.ACIMA_DE_TRES_E_MEIO: "Acima de 3,5 salários mínimos",
    nomes.RENDA_NAO_DECLARADA: "Não declarada",
}

VALORES = {
    "sexo": SEXO,
    "cor_raca": COR_RACA,
    "estado_civil": ESTADO_CIVIL,
    "renda_familiar_faixa": RENDA,
}

# --- Os grupos, na ordem em que se pergunta e em que se lê --------------------------------------
# **Os títulos servem aos dois canais**, e por isso são neutros: *"Dados pessoais"* funciona para
# quem preenche e para quem lê o dossiê. *"Sobre você"* — que o formulário usa no primeiro grupo —
# é do canal de quem preenche, e não caberia numa tela em que outra pessoa lê a declaração.
# **A mesma ordem nos dois canais**, e é isso que permite a quem conduz e a quem preencheu falarem
# do mesmo campo sem procurá-lo. O código IBGE fecha o endereço: ele não é digitado, e quem lê o
# dossiê precisa saber se o CEP foi reconhecido.
GRUPOS = (
    (
        "Dados pessoais",
        (
            "data_de_nascimento",
            "municipio_natal",
            "uf_natal",
            "nacionalidade",
            "sexo",
            "cor_raca",
            "estado_civil",
        ),
    ),
    ("Filiação", ("nome_da_mae", "nome_do_pai")),
    ("Documento de identidade", ("rg", "rg_orgao_emissor", "rg_expedido_em")),
    ("Contato", ("telefone_celular",)),
    ("Atendimento durante o curso", ("necessidade_especifica",)),
    ("Renda", ("renda_familiar_faixa",)),
    (
        "Endereço",
        (
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "municipio",
            "uf",
            "codigo_ibge",
        ),
    ),
)


def legivel(campo: str, valor) -> str:
    """O valor como uma pessoa o lê — nunca o código guardado.

    **Vazio vira `""`, e quem exibe decide o que dizer.** Devolver aqui *"não informado"* obrigaria
    as duas telas à mesma frase, e elas têm públicos diferentes: no dossiê, um campo em branco é
    informação sobre a declaração; no portal, é um campo que a pessoa ainda pode preencher.
    """
    if valor in (None, ""):
        return ""
    if campo in VALORES:
        return VALORES[campo].get(valor, valor)
    # **Data em dd/mm/aaaa, e não em ISO.** O formato ISO é o que o controle `<input type="date">`
    # consome, e quem monta o formulário o obtém de outro lugar; aqui é texto que uma pessoa lê, dos
    # dois lados do balcão. `1994-07-12` numa tela em português é data que se lê duas vezes.
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    if campo == "cep":
        # O CEP é guardado sem pontuação (`FR-387`) e **lido** com ela: a forma única é da coluna,
        # e não da leitura.
        return f"{valor[:5]}-{valor[5:]}" if len(valor) == 8 else valor
    return str(valor)
