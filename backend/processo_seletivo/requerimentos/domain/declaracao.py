"""O que a pessoa declara, saneado e conferido — **antes** de encostar no banco.

**Por que isto existe.** `gravar` atribuía o `POST` cru aos campos do modelo, e o Django **não**
valida `choices` em `save()`: `sexo="X"` gravava, `uf="ZZ"` gravava, e um município com três
espaços passava por preenchido em `faltando_para_enviar`, que só olhava veracidade. O primeiro
chegava ao Registro Acadêmico como sexo inexistente; o último, como endereço em branco num
documento de matrícula.

E o que o banco recusava, recusava tarde e feio: um valor maior que a coluna virava `DataError` —
erro 500 para quem preenchia, em vez da frase que diz o que corrigir.

**Onde a regra mora.** Aqui, e não na tela: *"Validações no frontend PODEM melhorar a experiência,
mas NÃO são fronteira de segurança"* (Princípio IV). Um `POST` montado à mão encontra esta camada.

**Três conferências, e elas são de naturezas diferentes.**

`lista fechada` — o valor pertence ao vocabulário ou não existe. É a que o Django deixou passar.
`tamanho`      — a coluna tem limite, e estourá-lo é recusa legível, nunca erro de servidor.
`data`         — texto que não é data é recusa de campo, e não exceção subindo pela pilha.

**Espaço em branco é ausência.** Um nome de mãe com um espaço não é um nome; guardá-lo faria a
`FR-384` — pai não declarado é situação legítima — virar mentira, porque o campo pareceria
preenchido a quem lesse o dossiê.
"""

from datetime import date

from processo_seletivo.requerimentos.domain import endereco, nomes
from processo_seletivo.shared.api.problems import DomainError

# Campo → vocabulário fechado. **A UF entra porque é lista**, ainda que a tela a ofereça como
# escolha: a tela não é fronteira.
LISTAS = {
    "sexo": (nomes.SEXOS, "o sexo"),
    "cor_raca": (nomes.CORES, "a cor ou raça"),
    "estado_civil": (nomes.ESTADOS_CIVIS, "o estado civil"),
    "renda_familiar_faixa": (nomes.FAIXAS_DE_RENDA, "a faixa de renda"),
    "uf": (nomes.UFS, "a UF"),
    "uf_natal": (nomes.UFS, "a UF de nascimento"),
}

DATAS = {
    "data_de_nascimento": "a data de nascimento",
    "rg_expedido_em": "a data de expedição do documento",
}

# **O ano mínimo não é esmero.** `0001-01-01` é data válida para o Python e absurda para uma pessoa;
# gravá-la produz um requerimento que nenhuma conferência humana aceita e que nenhuma restrição de
# banco recusa.
ANO_MINIMO = 1900


def _texto(valor) -> str:
    return "" if valor is None else str(valor).strip()


def _conferir_tamanho(modelo, campo, valor, rotulo):
    limite = modelo._meta.get_field(campo).max_length
    if limite and len(valor) > limite:
        raise DomainError(
            "field_constraint_violated",
            f"{rotulo.capitalize()} admite no máximo {limite} caracteres.",
            422,
            campo=campo,
        )


def _conferir_lista(campo, valor, admitidos, rotulo):
    if valor and valor not in admitidos:
        # A mensagem **não repete o valor recusado** (`FR-401`): ele veio de quem preencheu, e
        # mensagem de erro é copiada e colada em chamado de suporte.
        raise DomainError(
            "field_constraint_violated",
            f"Escolha {rotulo} entre as opções oferecidas.",
            422,
            campo=campo,
        )


def _conferir_data(campo, valor, rotulo):
    """A data como `date`, ou recusa legível. Nunca uma exceção subindo pela pilha."""
    if valor in (None, ""):
        return None
    if isinstance(valor, date):
        lida = valor
    else:
        try:
            lida = date.fromisoformat(str(valor).strip())
        except ValueError as erro:
            raise DomainError(
                "field_constraint_violated",
                f"Informe {rotulo} no formato dia/mês/ano.",
                422,
                campo=campo,
            ) from erro
    if lida.year < ANO_MINIMO:
        raise DomainError(
            "field_constraint_violated",
            f"Confira {rotulo}: o ano informado não parece correto.",
            422,
            campo=campo,
        )
    return lida


def sanear(modelo, dados: dict, campos) -> dict:
    """Os valores prontos para gravar, ou a primeira recusa legível.

    **Recusa na primeira, e não a lista inteira.** A tela ancora a recusa no campo que a causou
    (`FR-033`), e devolver seis de uma vez faria a âncora apontar para uma delas e esconder as
    outras — que é pior do que corrigir uma por vez.
    """
    saneados = {}
    for campo in campos:
        if campo not in dados:
            continue
        if campo in DATAS:
            saneados[campo] = _conferir_data(campo, dados[campo], DATAS[campo])
            continue
        valor = _texto(dados[campo])
        if campo in LISTAS:
            admitidos, rotulo = LISTAS[campo]
            _conferir_lista(campo, valor, admitidos, rotulo)
        elif campo == "cep":
            # **Normalizado aqui, e guardado normalizado** (`FR-387`): uma forma só, para que a
            # comparação nunca dependa de como se digitou.
            valor = endereco.normalizar(valor)
        else:
            _conferir_tamanho(modelo, campo, valor, campo.replace("_", " "))
        saneados[campo] = valor
    return saneados
