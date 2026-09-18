"""As 34 colunas do arquivo de importação — **uma função por coluna** (`FR-445`).

**Esta é a decisão de arquitetura da feature, e ela é deliberadamente mais longa de escrever.** A
tentação é mapear os 34 campos por dicionário e aplicar `legivel()` em cima, e ela é a forma exata
de o erro entrar: `legivel()` serve à leitura humana das duas telas da `029` — formata data em
`dd/mm/aaaa` para quem lê e traduz código em texto de gente. Metade disso é o que o destino quer, e
a outra metade não. `Casado(a)` é o que uma pessoa lê e o que o importador recusa.

Trinta e quatro funções pequenas, cada uma dizendo de onde tira, o que faz e o que devolve quando
não há dado, são impossíveis de errar em silêncio — e o silêncio é o risco desta feature, porque o
erro aparece depois da matrícula, com a pessoa no meio.

**Toda célula é texto** (`FR-437`), inclusive datas, CPF, RG, CEP e códigos. O formato `@` é
aplicado na escrita (`infrastructure/planilha.py`); aqui a garantia é que nada sai como número.

**As quatro tentações, e por que cada uma é recusada** (contrato, *O que o serializador NÃO faz*):

| Tentação | Por quê não |
|---|---|
| Converter a faixa de renda para per capita | os limites coincidem, o denominador não (`D-002`) |
| Reescrever `PPP` como `PPI` | o `code` publicado é ato imutável (`D-003`, `FR-441`) |
| Emitir `PT` por Portugal | uma amostra com um valor não prova ISO 3166 (`D-008`, `Q-7`) |
| Deduzir curso, turno ou polo | o valor é vocabulário de outro sistema (`D-001`) |
"""

from dataclasses import dataclass

from processo_seletivo.matriculas.domain import flexao, nomes
from processo_seletivo.matriculas.domain.lacuna import Lacuna
from processo_seletivo.requerimentos.domain import nomes as requerimento
from processo_seletivo.requerimentos.domain import rotulos
from processo_seletivo.shared.api.problems import DomainError

# **Alterada à mão por quem mudar qualquer serializador**, no molde de `SCHEMA_VERSION` e pela mesma
# razão (`FR-454`): o número precisa dizer *"esta geração usou estas regras"*.
#
# **Por que não é derivada do arquivo.** Um resumo criptográfico do módulo mudaria também quando só
# um comentário mudasse — e um registro de auditoria que muda sem que nenhuma regra tenha mudado
# ensina quem audita a ignorá-lo.
VERSAO_DOS_MAPEAMENTOS = 1

# **Os códigos de forma de ingresso que o destino reconhece** (`FR-441`). `AC` é a ampla
# concorrência, e `PPI` é o que o comentário da planilha de importação prevê para a cota racial.
#
# **A lista é curta porque a evidência é curta**, e é este o ponto em que a resposta do Registro
# Acadêmico entra (`T002`). Acrescentar códigos por suposição faria a exportação afirmar
# correspondências que ninguém confirmou — e o `code` de um Edital publicado **não é reescrito**
# para caber aqui: `PPP` continua `PPP`, e a geração é recusada nomeando o código e o Edital
# (`D-003`).
CODIGOS_DO_DESTINO = ("AC", "PPI")

# **A grafia das faixas do destino**, copiada da tabela da `D-002`. Elas têm os mesmos limites das
# faixas deste sistema e **outro denominador** — ver `renda_da_familia` e o aviso obrigatório do
# relatório (`FR-452`).
FAIXAS_DO_DESTINO = {
    requerimento.ATE_MEIO: "Até 0,5",
    requerimento.DE_MEIO_A_UM: "0,5 a 1",
    requerimento.DE_UM_A_UM_E_MEIO: "1 a 1,5",
    requerimento.DE_UM_E_MEIO_A_DOIS_E_MEIO: "1,5 a 2,5",
    requerimento.DE_DOIS_E_MEIO_A_TRES_E_MEIO: "2,5 a 3,5",
    requerimento.ACIMA_DE_TRES_E_MEIO: "Acima de 3,5",
}

# **Cor ou raça na grafia do destino.** Cinco categorias do IBGE, e `INDIGENA` **não está aqui**: o
# formato de destino não a comporta, e é o `R-1`. Quem se declarou indígena sai com a coluna vazia e
# **nomeado no relatório** (`FR-440`) — nunca mapeado para *parda*, que é o mapeamento que apagaria
# a declaração e que a contradição do próprio destino torna tentador: a Modalidade `PPP` reserva
# vaga para quem a coluna `COR` não sabe registrar.
CORES_DO_DESTINO = {
    requerimento.BRANCA: "Branca",
    requerimento.PRETA: "Preta",
    requerimento.PARDA: "Parda",
    requerimento.AMARELA: "Amarela",
}


@dataclass(frozen=True)
class Dossie:
    """Tudo o que os 34 serializadores leem de **uma** pessoa, reunido antes de a linha ser montada.

    **Reunido antes, e não buscado dentro de cada função**: trinta e quatro serializadores que
    consultassem o banco por conta própria custariam trinta e quatro consultas por pessoa, e é
    exatamente o crescimento que a `SC-090` da `019` proibiu para a tela de convocação.
    """

    protocolo: str
    nome: str
    cpf: str
    email: str
    requerimento: object
    # `None` **é** a ampla concorrência, e não falta de dado — a grafia que `Inscricao.modality_id`,
    # `PosicaoNaOrdem.modalidade_id` e `AtoDeOrdenacao.lista_id` já praticam (`D-003`).
    modalidade_code: str | None
    polo: str
    edital_codigo: str

    @property
    def quem(self) -> str:
        """Como esta pessoa é nomeada no relatório de lacunas e nas recusas."""
        return f"{self.nome} ({self.protocolo})"


@dataclass(frozen=True)
class Celula:
    """O texto que vai para a planilha e, quando ele é vazio, a razão de ser vazio."""

    texto: str
    lacuna: Lacuna | None = None


# ---------------------------------------------------------------------------
# Auxiliares — e eles NÃO são um `legivel()` genérico
#
# São três formas de dizer a mesma frase sobre ausência, e nenhum deles decide o que a coluna
# significa: quem decide é o serializador que os chama, e é por isso que cada coluna continua
# tendo função própria.
# ---------------------------------------------------------------------------


def _nao_declarado(campo: str) -> Lacuna:
    return Lacuna(
        nomes.AUSENCIA,
        f"Não declarado no Requerimento de Matrícula: {rotulos.ROTULOS[campo].lower()}.",
    )


def _do_requerimento(dossie: Dossie, campo: str) -> Celula:
    """O campo tal como declarado, ou vazio com a ausência contada.

    **Sem tradução nenhuma**: é o auxiliar das colunas que o destino quer cruas — nome da mãe,
    logradouro, bairro. Toda coluna que precise de conversão tem a conversão escrita na função dela.
    """
    valor = (getattr(dossie.requerimento, campo) or "").strip()
    return Celula(valor) if valor else Celula("", _nao_declarado(campo))


def _data(dossie: Dossie, campo: str) -> Celula:
    """`dd/mm/aaaa`, sem depender do idioma do servidor (`FR-437`).

    `%d/%m/%Y` não consulta locale nenhum — ao contrário de `%x`, que devolveria `07/12/94` numa
    máquina e `12/07/1994` em outra, e o arquivo diria datas diferentes conforme onde foi gerado.
    """
    valor = getattr(dossie.requerimento, campo)
    return Celula(valor.strftime("%d/%m/%Y")) if valor else Celula("", _nao_declarado(campo))


def _so_digitos(valor: str) -> str:
    return "".join(caractere for caractere in valor if caractere.isdigit())


# ---------------------------------------------------------------------------
# As 34, na ordem em que saem no arquivo
# ---------------------------------------------------------------------------


def inscricao_protocolo(dossie: Dossie) -> Celula:
    """1 · `INSC` — o protocolo da Inscrição, como ele é.

    **Opaco de propósito, e não normalizado aqui** (`Q-3`). A amostra do destino traz `117817`, e o
    protocolo deste sistema é `INS-2026-K7M4Q2PX`, **deliberadamente sem sequência**: um número
    corrido diria quantas inscrições existem. Torná-lo sequencial para caber no destino desfaria uma
    decisão de domínio, e isso não é formatação — é outra feature, com outra conversa.
    """
    return Celula(dossie.protocolo)


def nome(dossie: Dossie) -> Celula:
    """2 · `NOME` — o nome da identidade do candidato.

    **Da identidade, e não da Inscrição.** A Inscrição congelou o nome na submissão, meses antes; a
    matrícula é feita com o nome que a pessoa tem agora. O congelado continua onde deve estar — na
    Inscrição, provando o que foi submetido.
    """
    return Celula(dossie.nome)


def classificacao(dossie: Dossie) -> Celula:
    """3 · `CLASSIF_CURSO_FINAL` — **vazia enquanto a `Q-2` não for respondida** (`FR-448`).

    O nome da coluna e o comentário do Registro Acadêmico discordam: um diz *classificação no
    curso*, o outro manda continuar a sequência das linhas. A planilha não desempata — vem
    pré-preenchida de `1` a `35`.

    **A exportação não escolhe entre as duas.** Numerar as linhas é **uma das duas respostas
    possíveis**, e implementá-la agora faria o arquivo afirmar uma leitura que ninguém confirmou.
    Respondida a questão, é esta função que passa a ler a fonte que ela indicar.
    """
    return Celula(
        "",
        Lacuna(
            nomes.EXTERNA,
            "O destino não diz se a coluna é a classificação no curso ou a numeração das linhas, e "
            "as duas leituras produzem números diferentes. Preencher no destino.",
        ),
    )


def vazio_externo(dossie: Dossie) -> Celula:
    """4, 5 e 34 · `COD_CURSO`, `COD_TURNO`, `COD_POLO` — **sempre vazias** (`D-001`, `FR-438`).

    **O valor é externo a este sistema**: é vocabulário do sistema acadêmico, que este não conhece.
    Não há configuração de códigos por oferta, não há cadastro de turno nem de polo — e essa
    ausência é o que a decisão comprou: um subsistema inteiro de configuração sai do escopo porque a
    resposta certa é a célula vazia.

    **Dedução aqui seria o defeito, e não a ajuda.** Uma planilha montada à mão preenche toda
    coluna, porque quem a monta tenta ser prestativo — e nada no arquivo distingue depois o
    declarado do deduzido às pressas.
    """
    return Celula(
        "",
        Lacuna(
            nomes.EXTERNA,
            "Vocabulário do sistema acadêmico, que este sistema não conhece. Preencher no destino.",
        ),
    )


def forma_de_ingresso(dossie: Dossie) -> Celula:
    """6 · `COD_FORMA_INGRESSO` — `AC` pela **ausência** de Modalidade, ou o `code` publicado.

    **A ausência de Modalidade é ampla concorrência, e não falta de dado** (`D-003`). Esta é a única
    correspondência desta feature que é derivação legítima e não invenção: ela traduz o mesmo fato,
    e o destino chama esse fato de `AC`.

    **A grafia publicada não é reescrita** (`FR-441`). O `code` é texto digitado por quem redige o
    Edital, e um certame já publicado pode trazer grafia que o destino não conhece — o `seed_demo`
    deste repositório escreve `PPP` onde o comentário da planilha prevê `PPI`, duas letras de
    diferença para o mesmo instituto jurídico. Corrigir isso na saída faria o arquivo discordar do
    Edital, e corrigir Edital publicado é Retificação, não formatação. Então a geração **para** e
    nomeia o código e o Edital: decidir a correspondência é de quem opera, e não da exportação.
    """
    if dossie.modalidade_code is None:
        return Celula("AC")
    if dossie.modalidade_code not in CODIGOS_DO_DESTINO:
        raise DomainError(
            nomes.MODALIDADE_DESCONHECIDA,
            f"O Edital {dossie.edital_codigo} publicou a Modalidade «{dossie.modalidade_code}», "
            "que o formato de importação não reconhece. A grafia publicada não é reescrita pela "
            "exportação: a correspondência precisa ser acertada com o Registro Acadêmico.",
            422,
        )
    return Celula(dossie.modalidade_code)


def cpf(dossie: Dossie) -> Celula:
    """7 · `CPF` — onze dígitos, sem pontuação (`FR-444`).

    **A forma é a do destino, e não a da coluna deste sistema.** O CPF exibido preserva a pontuação
    de quem o digitou; o normalizado é o que a comparação usa, e é o que o destino quer. O zero à
    esquerda sobrevive porque a célula é texto (`FR-437`) — sem isso, `01234567890` chega como
    `1234567890` e o importador recusa uma pessoa que existe.
    """
    return Celula(dossie.cpf)


def sexo(dossie: Dossie) -> Celula:
    """8 · `SEXO` — `F` ou `M`, que é o que os dois lados escrevem.

    Binário dos dois lados, e é isso que torna a flexão de `ESTADO_CIVIL` total (`D-004`).
    """
    return _do_requerimento(dossie, "sexo")


def estado_civil_flexionado(dossie: Dossie) -> Celula:
    """9 · `ESTADO_CIVIL` — flexionado por `SEXO`, pela tabela da `D-004` (`FR-442`).

    **Nunca `Casado(a)`**: aquela é a forma que as telas da `029` exibem, e o destino não a conhece.
    """
    palavra = flexao.flexionar(dossie.requerimento.estado_civil, dossie.requerimento.sexo)
    return Celula(palavra) if palavra else Celula("", _nao_declarado("estado_civil"))


def email(dossie: Dossie) -> Celula:
    """10 · `EMAIL` — a credencial principal da identidade.

    **A credencial, e não o endereço que a Inscrição guardou.** O da Inscrição é indício histórico:
    ele prova o que foi informado no dia da inscrição, e pode ter meses. A matrícula precisa do
    endereço pelo qual a pessoa é alcançável hoje, e esse é o que ela provou controlar.

    **A razão da ausência é escrita aqui, e não tirada de `ROTULOS`.** O e-mail não é campo do
    Requerimento — ele vem da identidade —, e a primeira redação desta função pediu emprestada a
    frase do telefone celular: o relatório dizia que faltava telefone numa linha da coluna `EMAIL`.
    Uma razão emprestada é pior que nenhuma: ela manda quem lê procurar o campo errado.
    """
    if dossie.email:
        return Celula(dossie.email)
    return Celula(
        "",
        Lacuna(
            nomes.AUSENCIA,
            "Esta identidade não tem endereço de e-mail principal verificado.",
        ),
    )


def data_de_nascimento(dossie: Dossie) -> Celula:
    """11 · `DATA_NASCIMENTO` — `dd/mm/aaaa`, como texto.

    Como texto porque o Excel converte `12/07/1994` no serial `34527` assim que a célula é numérica,
    e o que chega ao destino deixa de ser uma data (`SC-144`).
    """
    return _data(dossie, "data_de_nascimento")


def cor(dossie: Dossie) -> Celula:
    """12 · `COR` — a cor ou raça declarada, **e vazia com a pessoa nomeada se for indígena**.

    **O destino não comporta *indígena***, e é o `R-1`. A coluna sai vazia e o relatório diz de quem
    é e o que a pessoa declarou (`FR-440`) — **nunca** substituída por valor próximo: mapear
    *indígena* para *parda* apagaria a declaração de alguém, em silêncio, dentro de um arquivo que
    ninguém confere linha a linha.

    **A contradição é do destino, e não deste sistema**: a Modalidade `PPP` reserva vaga com
    fundamento na Lei 12.990/2014 — que nomeia indígenas — e a coluna `COR` do mesmo arquivo não
    sabe registrá-los. Corrigir isso de verdade exige mudar o domínio do destino, e é material para
    a conversa que a `Q-1` abre.
    """
    declarado = dossie.requerimento.cor_raca
    if declarado == requerimento.INDIGENA:
        return Celula(
            "",
            Lacuna(
                nomes.NOMINAL,
                "O formato de importação não comporta a cor declarada. A exportação não substitui "
                "por valor próximo: a correspondência precisa ser acertada com o Registro "
                "Acadêmico.",
                valor_declarado=rotulos.COR_RACA[requerimento.INDIGENA],
            ),
        )
    traduzido = CORES_DO_DESTINO.get(declarado, "")
    return Celula(traduzido) if traduzido else Celula("", _nao_declarado("cor_raca"))


def nome_da_mae(dossie: Dossie) -> Celula:
    """13 · `NOME_MAE` — como declarado.

    Vazio é ausência **declarada**, e não campo esquecido: a `FR-384` da `029` admite o envio sem
    filiação porque essa situação é comum e legítima.
    """
    return _do_requerimento(dossie, "nome_da_mae")


def nome_do_pai(dossie: Dossie) -> Celula:
    """14 · `NOME_PAI` — como declarado, e vazio pela mesma razão de `NOME_MAE`."""
    return _do_requerimento(dossie, "nome_do_pai")


def cidade_natal(dossie: Dossie) -> Celula:
    """15 · `CIDADE_NATAL` — o município de nascimento, como declarado."""
    return _do_requerimento(dossie, "municipio_natal")


def nacionalidade(dossie: Dossie) -> Celula:
    """16 · `COD_NACIONALIDADE` — `BR` para Brasil, vazia e **nominal** para os demais (`FR-453`).

    **`BR` é o único valor que a amostra prova**, e é por isso que só ele é emitido. Ele é
    compatível com ISO 3166-1 alpha-2; se o destino usasse alpha-3 seria `BRA`, e numérico seria
    `076`. Um exemplo só não desempata para emitir `PT` por Portugal — seria a invenção que a
    `D-001` recusa, com o agravante de errar justamente no caso raro, que é o que ninguém confere
    (`Q-7`).

    **A grafia histórica é reconhecida, e não convertida no banco.** O campo foi texto livre por
    dois dias, e o declarado num requerimento **enviado** é imutável: reescrevê-lo apagaria a
    declaração de quem já enviou. Então quem lê reconhece — *"Brasil"*, *"Brasileira"* e
    *"Brasileiro"* emitem `BR` —, e o que não for reconhecido sai vazio com a pessoa nomeada.
    """
    declarado = (dossie.requerimento.nacionalidade or "").strip()
    if not declarado:
        return Celula("", _nao_declarado("nacionalidade"))
    if declarado == requerimento.BRASIL or _sem_acento(declarado) in (
        requerimento.GRAFIAS_HISTORICAS_DE_BRASIL
    ):
        return Celula("BR")
    return Celula(
        "",
        Lacuna(
            nomes.NOMINAL,
            "O destino não confirmou qual esquema de código de país usa, e um único exemplo não "
            "prova o esquema. A exportação não emite código de país não confirmado: preencher no "
            "destino.",
            valor_declarado=rotulos.NACIONALIDADE.get(declarado, declarado),
        ),
    )


def _sem_acento(texto: str) -> str:
    import unicodedata

    decomposto = unicodedata.normalize("NFKD", texto)
    return (
        "".join(letra for letra in decomposto if not unicodedata.combining(letra)).strip().lower()
    )


def rg(dossie: Dossie) -> Celula:
    """17 · `RG` — o número do documento, como declarado.

    Como texto: um RG com ponto e traço não é número, e um que comece por zero perde o zero.
    """
    return _do_requerimento(dossie, "rg")


def emissor(dossie: Dossie) -> Celula:
    """18 · `EMISSOR` — o órgão emissor, como declarado."""
    return _do_requerimento(dossie, "rg_orgao_emissor")


def identidade_data(dossie: Dossie) -> Celula:
    """19 · `IDENTIDADE_DATA` — a data de expedição do documento, em `dd/mm/aaaa`.

    **É a data de expedição, e não a de nascimento.** O comentário da planilha chama esta coluna de
    *"data de nascimento"*, por erro de cópia (`Q-4`); o cabeçalho é inequívoco, e é o cabeçalho que
    manda.
    """
    return _data(dossie, "rg_expedido_em")


def titulo_eleitoral(dossie: Dossie) -> Celula:
    """20 · `TITULO_ELE` — três blocos de quatro dígitos, separados por espaço (`FR-451`).

    Guardado sem pontuação, como o CEP, e pontuado na saída: a forma única é da coluna, e a forma do
    destino é da saída.
    """
    valor = dossie.requerimento.titulo_eleitoral
    if not valor:
        return Celula("", _nao_declarado("titulo_eleitoral"))
    return Celula(" ".join(valor[inicio : inicio + 4] for inicio in range(0, 12, 4)))


def zona(dossie: Dossie) -> Celula:
    """21 · `ZONA_ELE` — três dígitos, **com os zeros à esquerda** (`FR-451`).

    Os zeros sobrevivem porque a célula é texto: numérica, `034` chega como `34`, e a zona passa a
    ser outra.
    """
    return _do_requerimento(dossie, "zona_eleitoral")


def secao(dossie: Dossie) -> Celula:
    """22 · `SECAO_ELE` — quatro dígitos, com os zeros à esquerda, pela razão da zona."""
    return _do_requerimento(dossie, "secao_eleitoral")


def cep(dossie: Dossie) -> Celula:
    """23 · `CEP` — **com hífen** (`FR-444`).

    Guardado sem pontuação (`FR-387` da `029`) e emitido com ela: a forma de cada ponta é a daquela
    ponta, e a coluna do banco continua tendo uma forma só.
    """
    valor = dossie.requerimento.cep
    if not valor:
        return Celula("", _nao_declarado("cep"))
    return Celula(f"{valor[:5]}-{valor[5:]}" if len(valor) == 8 else valor)


def endereco(dossie: Dossie) -> Celula:
    """24 · `ENDEREÇO` — o logradouro, como declarado. O cabeçalho é acentuado, e sai assim."""
    return _do_requerimento(dossie, "logradouro")


def numero(dossie: Dossie) -> Celula:
    """25 · `NÚMERO` — como declarado, e **sem tentativa de virar número**.

    *"s/n"* existe, e um endereço sem número é endereço. Como texto, `07` continua `07`.
    """
    return _do_requerimento(dossie, "numero")


def complemento(dossie: Dossie) -> Celula:
    """26 · `COMPLEMENTO` — como declarado. Nem todo endereço tem, e vazio aqui é o caso normal."""
    return _do_requerimento(dossie, "complemento")


def bairro(dossie: Dossie) -> Celula:
    """27 · `BAIRRO` — como declarado."""
    return _do_requerimento(dossie, "bairro")


def cidade(dossie: Dossie) -> Celula:
    """28 · `CIDADE` — o município do endereço, como declarado.

    **Não é a `CIDADE_NATAL`**, e os dois campos existem separados no Requerimento justamente porque
    quem nasceu num lugar mora em outro.
    """
    return _do_requerimento(dossie, "municipio")


def estado(dossie: Dossie) -> Celula:
    """29 · `ESTADO` — a UF do endereço, na sigla de duas letras que a lista fechada garante."""
    return _do_requerimento(dossie, "uf")


def telefone(dossie: Dossie) -> Celula:
    """30 · `CELULAR` — **sem pontuação** (`FR-444`).

    O Requerimento aceita o telefone como a pessoa o escreve; o destino o quer em dígitos. É a mesma
    repartição do CEP, na direção contrária.
    """
    valor = _so_digitos(dossie.requerimento.telefone_celular or "")
    return Celula(valor) if valor else Celula("", _nao_declarado("telefone_celular"))


def renda_da_familia(dossie: Dossie) -> Celula:
    """31 · `RENDA_PER_CAPITA_PNP` — a faixa da família, **sem conversão** (`D-002`).

    **Esta é a coluna que alguém vai tentar consertar, e a decisão está tomada.** Este sistema mede
    a soma da família (`FR-412`); o destino define a coluna como valor **por pessoa**. Os limites
    das duas listas são idênticos — *até 0,5*, *0,5 a 1*, *1 a 1,5*, *1,5 a 2,5*, *2,5 a 3,5* e
    *acima de 3,5* — e é essa coincidência que torna a conversão natural de se fazer e errada.

    **Não há conversão possível sem o denominador**: dividir uma faixa por um número não produz uma
    faixa, e o tamanho do domicílio não é coletado — a `FR-382` o recusou por nome (`Q-6`).

    **O efeito, medido**: uma família de quatro pessoas com 2 salários mínimos declara *de 1,5 a
    2,5* e está em **0,5** por pessoa. A coluna recebe *1,5 a 2,5* — três faixas acima —, e o
    desvio é sempre no mesmo sentido, maior quanto maior a família.

    **Por isso a cópia vem acompanhada, e não sozinha** (`FR-452`): o relatório declara a
    divergência em **toda** geração, inclusive nas que não têm nenhuma outra lacuna. Quem recebe o
    arquivo fica em condição de decidir o que fazer com isso; quem o gera não decide por ele.
    """
    faixa = FAIXAS_DO_DESTINO.get(dossie.requerimento.renda_familiar_faixa, "")
    return Celula(faixa) if faixa else Celula("", _nao_declarado("renda_familiar_faixa"))


def necessidades_especiais(dossie: Dossie) -> Celula:
    """32 · `NECESSIDADES_ESPECIAIS` — o texto declarado, como declarado.

    Texto livre dos dois lados (`Q-5`): a amostra do destino traz `NENHUMA`, e não há indício de
    vocabulário fechado lá. **Não é a cota de pessoa com deficiência** (`FR-385` da `029`) — aquela
    é concorrência, com comprovação e análise; esta é informação de acolhimento.
    """
    return _do_requerimento(dossie, "necessidade_especifica")


def nome_polo(dossie: Dossie) -> Celula:
    """33 · `NOME_POLO` — a localidade publicada do Perfil.

    **O nome sai; o código não** (`D-001`): o nome é do Edital, e o código é vocabulário do sistema
    acadêmico. As duas colunas ao lado uma da outra tornam essa diferença visível a quem conferir.
    """
    return (
        Celula(dossie.polo)
        if dossie.polo
        else Celula(
            "",
            Lacuna(nomes.AUSENCIA, "O Edital não publicou localidade para este Perfil de Vaga."),
        )
    )


@dataclass(frozen=True)
class Coluna:
    """Um cabeçalho do destino e a função que produz o valor dele."""

    cabecalho: str
    serializador: object


# **A ordem é a do destino, e os acentos são os do destino** (`FR-436`). `ENDEREÇO` e `NÚMERO` saem
# acentuados porque é assim que a planilha de importação os escreve — normalizá-los faria o
# importador não encontrar a coluna.
COLUNAS = (
    Coluna("INSC", inscricao_protocolo),
    Coluna("NOME", nome),
    Coluna("CLASSIF_CURSO_FINAL", classificacao),
    Coluna("COD_CURSO", vazio_externo),
    Coluna("COD_TURNO", vazio_externo),
    Coluna("COD_FORMA_INGRESSO", forma_de_ingresso),
    Coluna("CPF", cpf),
    Coluna("SEXO", sexo),
    Coluna("ESTADO_CIVIL", estado_civil_flexionado),
    Coluna("EMAIL", email),
    Coluna("DATA_NASCIMENTO", data_de_nascimento),
    Coluna("COR", cor),
    Coluna("NOME_MAE", nome_da_mae),
    Coluna("NOME_PAI", nome_do_pai),
    Coluna("CIDADE_NATAL", cidade_natal),
    Coluna("COD_NACIONALIDADE", nacionalidade),
    Coluna("RG", rg),
    Coluna("EMISSOR", emissor),
    Coluna("IDENTIDADE_DATA", identidade_data),
    Coluna("TITULO_ELE", titulo_eleitoral),
    Coluna("ZONA_ELE", zona),
    Coluna("SECAO_ELE", secao),
    Coluna("CEP", cep),
    Coluna("ENDEREÇO", endereco),
    Coluna("NÚMERO", numero),
    Coluna("COMPLEMENTO", complemento),
    Coluna("BAIRRO", bairro),
    Coluna("CIDADE", cidade),
    Coluna("ESTADO", estado),
    Coluna("CELULAR", telefone),
    Coluna("RENDA_PER_CAPITA_PNP", renda_da_familia),
    Coluna("NECESSIDADES_ESPECIAIS", necessidades_especiais),
    Coluna("NOME_POLO", nome_polo),
    Coluna("COD_POLO", vazio_externo),
)

CABECALHOS = tuple(coluna.cabecalho for coluna in COLUNAS)


def linha(dossie: Dossie):
    """As 34 células de uma pessoa, na ordem do arquivo.

    Devolve `(textos, lacunas)`: os textos vão para a planilha, e as lacunas para o relatório com a
    coluna a que pertencem. Separá-los aqui é o que permite à tela mostrar o resumo **antes** do
    download (`UX-060`) sem montar a planilha duas vezes.
    """
    celulas = [(coluna.cabecalho, coluna.serializador(dossie)) for coluna in COLUNAS]
    textos = tuple(celula.texto for _, celula in celulas)
    lacunas = tuple(
        (dossie.quem, cabecalho, celula.lacuna)
        for cabecalho, celula in celulas
        if celula.lacuna is not None
    )
    return textos, lacunas
