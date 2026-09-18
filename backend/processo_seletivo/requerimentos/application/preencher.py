"""Abrir, gravar e enviar o Requerimento de Matrícula — os três sob a política do domínio.

**A recusa é do comando, e a tela apenas a antecipa.** A Constituição, no Princípio IV: *"Validações
no frontend PODEM melhorar a experiência, mas **NÃO são fronteira de segurança**"*. Um `POST` que
chegue sem passar pela tela encontra aqui a mesma recusa que ela anuncia.

**Uma trava só, e a escolha custou um deadlock para ser feita.**

`FOR SHARE` no **Processo Seletivo** impede que um desfecho de convocação seja gravado entre a
leitura da chamada em aberto e o commit do envio: os comandos da `019` passam por
`comando_de_comissao`, que trava o Processo com `select_for_update`. Sem compartilhar essa linha, o
envio confirmaria sobre uma chamada que outra transação já fechou — um requerimento válido
pendurado num fato que já não existia.

**E por que *não* há trava no Edital.** A primeira redação tomava as duas, na crença de que só a
trava do Edital impediria um par incoerente: `versao_aceita` apontando uma versão e
`declaracao_hash` resumindo o texto de outra. Duas coisas mudaram isso.

A primeira é que o par deixou de poder divergir. O resumo passou a ser calculado a partir do
**mesmo objeto de versão** que se grava — `declaracao_publicada(versao.content)` —, e não de um
texto recebido no `POST`. Uma Retificação publicada entre a leitura e a gravação faz o requerimento
registrar a versão que a pessoa **leu e aceitou**, com o resumo do texto daquela versão. Isso é
coerente, e é mais verdadeiro do que bloquear a Retificação: o que a `SC-129` pede é reconstituir o
texto que a pessoa leu, não o texto de hoje.

A segunda é que as duas travas juntas produziam *deadlock* real, e não teórico. Este repositório tem
**duas ordens de travamento incompatíveis**: `comando_de_comissao` toma o Processo e depois o
Edital; `replace_draft` e a publicação tomam o Edital com o Processo na mesma consulta. Quem pedisse
as duas linhas deadlockaria contra uma das duas, em qualquer ordem que escolhesse — e o preço, para
o candidato, é um erro interno no envio. Esta feature foi a primeira a precisar das duas, e o teste
de corrida da T036 reproduziu o defeito nas duas ordens antes de esta redação existir.

**A divergência de ordens entre aqueles dois caminhos fica registrada como achado**, e não vira
escopo desta feature: nenhum comando anterior pedia as duas linhas, e ninguém sofria com isso.

`FOR SHARE` e não `FOR UPDATE`: candidatos não se bloqueiam entre si, e ela conflita com o
`FOR UPDATE` de quem registra o desfecho.
"""

import hashlib
import unicodedata

from django.db import connection

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.convocacao.application.selectors import chamada_em_aberto
from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato
from processo_seletivo.requerimentos.application.exigencia import (
    versao_vigente,
    vigente_de,
    vigentes,
)
from processo_seletivo.requerimentos.domain import (
    declaracao,
    disponibilidade,
    endereco,
    nomes,
)
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context

# Os campos que a pessoa declara. A lista fechada mora aqui porque é ela que separa o que o
# formulário aceita do que alguém poderia tentar gravar por um `POST` montado à mão.
CAMPOS_DECLARADOS = (
    "data_de_nascimento",
    "municipio_natal",
    "uf_natal",
    "nacionalidade",
    "sexo",
    "cor_raca",
    "estado_civil",
    "nome_da_mae",
    "nome_do_pai",
    "rg",
    "rg_orgao_emissor",
    "rg_expedido_em",
    "titulo_eleitoral",
    "zona_eleitoral",
    "secao_eleitoral",
    "telefone_celular",
    "necessidade_especifica",
    "renda_familiar_faixa",
    "cep",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "municipio",
    "uf",
    "codigo_ibge",
    "endereco_conferido_por_referencia",
)

# **Os dois derivados nunca vêm da tela.** O código IBGE porque a `FR-388` o proíbe; a marca de
# conferência porque ela **afirma** que a referência confirmou a localidade, e quem afirma é quem
# conferiu. Aceitar qualquer um dos dois do formulário permitiria plantá-los por um `POST` montado
# à mão — e a marca plantada faria a tela abrir o campo que deveria estar fechado.
DERIVADOS = ("codigo_ibge", "endereco_conferido_por_referencia")
CAMPOS_DA_TELA = tuple(campo for campo in CAMPOS_DECLARADOS if campo not in DERIVADOS)


def _travar(inscricao):
    """A linha que este ato precisa que não mude debaixo dele.

    Fora do PostgreSQL é no-op, e é honesto que seja: o SQLite serializa a escrita inteira, e as
    corridas que estas travas impedem não existem lá.
    """
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        # **Uma linha só.** Pedir também o Edital deadlockaria contra uma das duas ordens de
        # travamento que já convivem neste repositório — a razão inteira está no topo do módulo.
        cursor.execute(
            "SELECT p.id FROM processos_processoseletivo p "
            "JOIN processos_edital e ON e.processo_id = p.id WHERE e.id = %s FOR SHARE",
            [str(inscricao.edital_id)],
        )


def _conteudo(inscricao):
    return versao_vigente(inscricao)


def apurar(inscricao, conteudo=None):
    """A política, com a chamada em aberto e o requerimento injetados — nunca lidos pelo domínio.

    **A chamada é consultada em dois casos, e o segundo faltava.** Para *abrir* no momento na
    convocação — e para *corrigir* um requerimento **já enviado**, seja qual for o momento.

    A primeira redação só consultava no momento na convocação, e com isso quem declarou **na
    inscrição** nunca recebia *conferir e atualizar* ao ser convocado. É exatamente o cenário de
    dado envelhecido que a `FR-410` e o `R-2` existem para mitigar: quem preencheu em março e é
    chamado em setembro pode ter mudado de endereço, e a coleta antecipada é o que torna isso
    provável.

    Fora desses dois casos a consulta não é paga: ler a fila de chamada para descartá-la seria
    custo em toda tela de preenchimento, que é a mais visitada.
    """
    if conteudo is None:
        conteudo = _conteudo(inscricao).content
    momento = disponibilidade.momento_declarado(conteudo)
    vigente = vigente_de(inscricao)
    ja_enviado = vigente is not None and vigente.status == nomes.ENVIADO
    precisa_da_chamada = momento == nomes.NA_CONVOCACAO or ja_enviado
    chamada = chamada_em_aberto(inscricao) if precisa_da_chamada else None
    return disponibilidade.apurar(conteudo, chamada_em_aberto=chamada, requerimento=vigente)


def _exigir_disponibilidade(inscricao, conteudo):
    apurado = apurar(inscricao, conteudo)
    if not apurado.exigido:
        raise DomainError(
            nomes.NAO_EXIGIDO, "Este certame não pede Requerimento de Matrícula.", 404
        )
    if not apurado.disponivel:
        raise DomainError(
            nomes.INDISPONIVEL,
            "O Requerimento de Matrícula ficará disponível quando você for convocado.",
            409,
        )
    return apurado


def _anterior_da_identidade(inscricao):
    """O último requerimento **enviado** desta pessoa, em qualquer certame (`FR-377`).

    Da mesma **identidade**, e não da mesma Inscrição: é o que faz a cópia atravessar Editais e
    anos. Quem já se matriculou antes confere o que declarou; não redigita.
    """
    return (
        RequerimentoDeMatricula.objects.filter(
            inscricao__identity_subject=inscricao.identity_subject, status=nomes.ENVIADO
        )
        .exclude(inscricao=inscricao)
        .order_by("-enviado_em")
        .first()
    )


def _copiar_para_a_frente(inscricao):
    """O que o rascunho novo já sabe — por **cópia**, nunca por referência (`D-005`).

    Editar o novo não pode alcançar o anterior: o requerimento de 2024 continua dizendo o que dizia
    em 2024. É a diferença entre reaproveitar e compartilhar, e é ela que mantém o passado
    reproduzível.

    Sem requerimento anterior, o telefone vem da **Inscrição** — que congelou na submissão e pode
    ter meses, e por isso entra como ponto de partida a confirmar, nunca como verdade (`FR-379`).

    **A nacionalidade é traduzida na cópia, e o anterior fica intacto** (`031`, `D-008`). O campo
    foi texto livre até 18/09/2026, e um `Brasileira` copiado ao pé da letra para uma lista fechada
    produz um rascunho com valor que o `<select>` não tem: a tela abre com o campo em branco, a
    pessoa acha que nunca declarou, e o reaproveitamento que esta função existe para oferecer vira
    um campo a preencher de novo. Traduzir **na cópia** é o único lugar em que a conversão cabe —
    o requerimento enviado é imutável, e reescrevê-lo apagaria o que a pessoa declarou.
    """
    anterior = _anterior_da_identidade(inscricao)
    if anterior is None:
        return {"telefone_celular": inscricao.telefone}
    copiado = {campo: getattr(anterior, campo) for campo in CAMPOS_DECLARADOS}
    copiado["telefone_celular"] = anterior.telefone_celular or inscricao.telefone
    copiado["nacionalidade"] = _nacionalidade_na_lista(anterior.nacionalidade)
    return copiado


def _nacionalidade_na_lista(declarada: str) -> str:
    """O valor histórico dito no vocabulário de hoje — e `OUTRO_PAIS` quando não era o Brasil.

    **`OUTRO_PAIS` não perde a declaração da pessoa**: o país que ela escreveu continua escrito no
    requerimento anterior, que é imutável e continua legível. O que se copia para a frente é um
    ponto de partida a confirmar, e afirmar *"não é o Brasil"* é mais fiel do que copiar um texto
    que a lista não aceita — ou do que deixar em branco, que diria que ela não declarou nada.
    """
    valor = (declarada or "").strip()
    if not valor or valor in nomes.NACIONALIDADES:
        return valor
    sem_acento = unicodedata.normalize("NFKD", valor)
    limpo = "".join(letra for letra in sem_acento if not unicodedata.combining(letra)).lower()
    return nomes.BRASIL if limpo in nomes.GRAFIAS_HISTORICAS_DE_BRASIL else nomes.OUTRO_PAIS


def abrir_rascunho(*, inscricao, correlation_id=""):
    """O rascunho, criado sob a política e já preenchido com o que o sistema sabe.

    Idempotente: havendo requerimento vigente, ele é devolvido. Abrir duas vezes é o que acontece
    quando a pessoa atualiza a página, e criar duas linhas ali seria a duplicata que a
    `uq_requerimento_raiz_por_inscricao` recusaria — com um erro que ela não causou.
    """
    conteudo = _conteudo(inscricao).content
    with command_context() as agora:
        _travar(inscricao)
        existente = vigente_de(inscricao)
        if existente is not None:
            return existente
        apurado = _exigir_disponibilidade(inscricao, conteudo)
        return RequerimentoDeMatricula.objects.create(
            inscricao=inscricao,
            status=nomes.RASCUNHO,
            disponibilizado_em=agora,
            created_at=agora,
            # **Persistida também na raiz**, e não só no sucessor: é o que torna reconstituível qual
            # convocação abriu aquele requerimento (`FR-408`).
            convocacao_autorizadora=apurado.chamada,
            **_copiar_para_a_frente(inscricao),
        )


def gravar(*, inscricao, dados, expected_revision, correlation_id=""):
    """Grava o rascunho. Enviado não passa por aqui — a guarda do modelo e o gatilho o barram."""
    conteudo = _conteudo(inscricao).content
    with command_context():
        _travar(inscricao)
        _exigir_disponibilidade(inscricao, conteudo)
        requerimento = _rascunho_para_escrita(inscricao, expected_revision)
        # **Saneado antes de encostar no modelo** (`declaracao.sanear`). O Django **não** valida
        # `choices` em `save()`: atribuir o `POST` cru gravava `sexo="X"` e `uf="ZZ"` sem que nada
        # recusasse, e um valor maior que a coluna virava erro 500 em vez de frase legível.
        #
        # **O CEP sai normalizado de lá** (`FR-387`): uma forma só, guardada uma vez. O custo é um
        # CEP digitado pela metade sumir ao gravar — e é o preço certo, porque a coluna é o
        # registro, e registro que guarda não-CEP é pior do que campo que volta vazio.
        for campo, valor in declaracao.sanear(
            RequerimentoDeMatricula, dados, CAMPOS_DA_TELA
        ).items():
            setattr(requerimento, campo, valor)
        _enriquecer_o_endereco(requerimento)
        requerimento.revision += 1
        requerimento.save()
        return requerimento


def _enriquecer_o_endereco(requerimento):
    """O que a **referência** afirma sobre o CEP — e nunca o que a tela mandou (`FR-388`).

    **O código IBGE é derivado.** Aceitá-lo do formulário tornaria a proibição uma promessa: um
    `POST` montado à mão o plantaria. Aqui o comando nem olha o que ele mandar.

    **Município e UF também**, quando a referência os traz. A T030 os mantém somente leitura
    enquanto o CEP for reconhecido, e somente leitura na tela é o valor vindo da referência — quem
    montar o `POST` à mão não escolhe outro. Só os campos que a referência **traz** são derivados:
    registro incompleto não apaga o que a pessoa digitou (`FR-390`).

    **`endereco_conferido_por_referencia` afirma conferência, e por isso pede município e UF.**
    Uma redação anterior o ligava pela mera existência da linha, e então um registro sem localidade
    — ou um `POST` com município divergente — dizia *"conferido"* sobre um endereço que ninguém
    conferiu. O campo é lido pela tela para decidir o que fica aberto; mentir nele abre o que
    deveria estar fechado, e fecha o que deveria estar aberto.

    **CEP não reconhecido deixa o IBGE vazio, e isso não bloqueia nada** (`FR-390`): base ausente,
    desatualizada ou sem aquele CEP são o mesmo caso para quem preenche. O município e a UF
    continuam sendo o que a pessoa digitou.
    """
    referencia = endereco.referencia_de_cep(requerimento.cep)
    if referencia is None:
        requerimento.codigo_ibge = ""
        requerimento.endereco_conferido_por_referencia = False
        return
    requerimento.codigo_ibge = referencia.codigo_ibge
    # **Município e UF, e não logradouro e bairro.** Estes dois a referência apenas sugere: CEP de
    # logradouro traz o nome genérico da via, e quem mora lá às vezes o escreve melhor. Derivá-los
    # a cada gravação apagaria a correção da pessoa em silêncio, uma tecla depois de ela a digitar.
    for campo in ("municipio", "uf"):
        afirmado = getattr(referencia, campo)
        if afirmado:
            setattr(requerimento, campo, afirmado)
    requerimento.endereco_conferido_por_referencia = bool(referencia.municipio and referencia.uf)


def _rascunho_para_escrita(inscricao, expected_revision):
    requerimento = vigentes(inscricao).select_for_update().first()
    if requerimento is None:
        raise DomainError(
            nomes.INDISPONIVEL, "Não há requerimento aberto para esta inscrição.", 409
        )
    if requerimento.status == nomes.ENVIADO:
        raise DomainError(
            nomes.JA_ENVIADO, "Requerimento de Matrícula enviado não é alterado.", 409
        )
    if expected_revision is not None and requerimento.revision != expected_revision:
        raise DomainError(
            "revision_conflict", "Alguém alterou este requerimento enquanto você preenchia.", 409
        )
    return requerimento


# O que o **envio** exige. O rascunho nasce vazio de propósito — obrigatório aqui significa
# obrigatório para enviar, e não para existir.
#
# **A filiação não está nesta lista, e a ausência é a regra** (`FR-384`): pai não declarado é
# situação comum e legítima, e travar o envio por isso inventaria exigência que Edital nenhum faz.
# **O complemento também não**: nem todo endereço tem. **Nem o número**: "s/n" existe. E **nem o
# código IBGE**, que o candidato não digita e que fica vazio quando o CEP não é reconhecido.
OBRIGATORIOS_PARA_ENVIAR = (
    ("data_de_nascimento", "a data de nascimento"),
    ("municipio_natal", "o município de nascimento"),
    ("uf_natal", "a UF de nascimento"),
    ("nacionalidade", "a nacionalidade"),
    ("sexo", "o sexo"),
    ("cor_raca", "a cor ou raça"),
    ("estado_civil", "o estado civil"),
    ("rg", "o número do documento de identidade"),
    ("rg_orgao_emissor", "o órgão emissor do documento"),
    ("rg_expedido_em", "a data de expedição do documento"),
    ("telefone_celular", "o telefone celular"),
    ("renda_familiar_faixa", "a faixa de renda familiar"),
    ("cep", "o CEP"),
    ("logradouro", "o logradouro"),
    ("municipio", "o município"),
    ("uf", "a UF"),
)


def faltando_para_enviar(requerimento) -> list[str]:
    """O que ainda falta, em palavras — para a tela dizer antes da tentativa.

    **Espaço em branco é ausência.** A primeira redação testava apenas veracidade, e um município
    com três espaços passava por preenchido: o envio concluía, e o dossiê exibia um endereço vazio
    a quem fosse expedir documento de matrícula.
    """
    faltando = []
    for campo, rotulo in OBRIGATORIOS_PARA_ENVIAR:
        valor = getattr(requerimento, campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            faltando.append(rotulo)
    return faltando


def resumo_da_declaracao(texto: str) -> str:
    """O resumo do texto **exatamente como está publicado** (`FR-393`).

    Sem normalizar: normalizar antes de resumir guardaria o resumo de um texto que ninguém leu, e o
    ponto inteiro é reconstituir o que a pessoa tinha na tela quando aceitou.
    """
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def declaracao_publicada(conteudo) -> str:
    """O texto da declaração no conteúdo vigente — a **única** origem do que se resume."""
    return ((conteudo or {}).get("matriculationRequest") or {}).get("declarationText") or ""


def enviar(
    *, identidade, inscricao, versao_exibida_id, declaracao_exibida, aceite, correlation_id=""
):
    """O envio: confere a versão exibida, grava o aceite e registra a trilha.

    **A versão exibida viaja no formulário e é conferida aqui.** Uma Retificação entre o `GET` e o
    `POST` faria a versão gravada não ser a do texto cujo resumo se guarda — e o par ficaria
    incoerente sem que ninguém notasse. É a distinção que a `Inscricao` já carrega em duas colunas,
    `versao_reconhecida` e `versao_aceita`, e pela mesma razão.
    """
    versao = _conteudo(inscricao)
    with command_context() as agora:
        _travar(inscricao)
        # Relido **sob a trava**: entre a leitura de fora e este ponto, uma Retificação pode ter
        # publicado. Daqui em diante ela não pode mais.
        versao = _conteudo(inscricao)
        conteudo = versao.content
        _exigir_disponibilidade(inscricao, conteudo)
        if str(versao.id) != str(versao_exibida_id):
            raise DomainError(
                nomes.EDITAL_ATUALIZADO,
                "O Edital foi retificado enquanto você preenchia. Releia a declaração e envie de "
                "novo.",
                409,
            )
        # **O resumo sai do conteúdo publicado, e o texto recebido é apenas conferido.** A
        # redação anterior resumia direto o que o `POST` mandava: com o identificador de versão
        # certo — que é público — dava para gravar o resumo de qualquer texto, e a `SC-129`
        # reconstituiria a declaração que o remetente escolheu, não a que o Edital publicou. Um
        # resumo que o cliente escolhe não prova nada sobre o que ele leu.
        #
        # Conferir o texto recebido continua valendo: ele é a prova de que a tela exibiu o mesmo
        # que está publicado agora. Divergência aqui é a mesma situação que a versão obsoleta — a
        # pessoa leu outra coisa —, e a resposta é a mesma: releia e envie de novo.
        publicada = declaracao_publicada(conteudo)
        if resumo_da_declaracao(declaracao_exibida or "") != resumo_da_declaracao(publicada):
            raise DomainError(
                nomes.EDITAL_ATUALIZADO,
                "O texto da declaração mudou enquanto você preenchia. Releia e envie de novo.",
                409,
            )
        if not aceite:
            raise DomainError(
                nomes.DECLARACAO_NAO_ACEITA,
                "Para enviar, é preciso aceitar a declaração de veracidade.",
                422,
            )
        requerimento = _rascunho_para_escrita(inscricao, None)
        # **Sucessor que não corrige nada é recusado aqui, e não na tela** (`FR-410`). A cadeia de
        # sucessão é histórico de correções; um elo em que nada mudou faria quem audita ler
        # movimento onde não houve nenhum.
        if nada_mudou(requerimento):
            raise DomainError(
                nomes.SUCESSOR_NAO_AUTORIZADO,
                "Nada mudou em relação ao que você já havia enviado. Altere o que precisa "
                "corrigir, ou volte — o requerimento anterior continua valendo.",
                422,
            )
        faltando = faltando_para_enviar(requerimento)
        if faltando:
            raise DomainError(
                "field_required",
                "Para enviar, ainda falta informar: " + ", ".join(faltando) + ".",
                422,
            )
        requerimento.status = nomes.ENVIADO
        requerimento.enviado_em = agora
        requerimento.versao_aceita = versao
        requerimento.declaracao_hash = resumo_da_declaracao(publicada)
        requerimento.declaracao_aceita_em = agora
        requerimento.revision += 1
        requerimento.save()
        _registrar(
            identidade=identidade,
            inscricao=inscricao,
            requerimento=requerimento,
            agora=agora,
            correlation_id=correlation_id,
        )
        return requerimento


def _registrar(*, identidade, inscricao, requerimento, agora, correlation_id):
    """A trilha do envio (`FR-397`).

    **O agregado é o requerimento, e não a Inscrição.** `record_event` lê `status` e `revision` do
    que recebe: com a Inscrição ali, o registro dizia o estado e a revisão *dela* — que este ato não
    mudou — e a trilha afirmava, em duas colunas, algo que não aconteceu. Quem auditasse leria a
    revisão da inscrição subindo em ato que não a tocou, ou parada em ato que a tocou; nos dois
    casos a coluna mente. A Inscrição continua no registro, por escrito, porque a `FR-397` a exige.

    **Ela referencia, e não copia** (`FR-401`): aponta o requerimento em vez de repetir cor/raça,
    filiação, documento e endereço dentro do registro. Trilha que duplica dado sensível multiplica a
    superfície em vez de protegê-la. O resumo da declaração entra porque é resumo — ele prova qual
    texto foi aceito sem transcrever nada.

    `permission` aqui é o **rótulo nominal do ato**, e não uma permissão do vocabulário de
    autorização: o ator do candidato nasce *"sem uma permissão sequer"*, e quem governa o acesso é a
    titularidade da Inscrição.
    """
    partes = [
        f"inscrição {inscricao.id}",
        f"edital {inscricao.edital_id}",
        f"versão {requerimento.versao_aceita_id}",
        f"declaração {requerimento.declaracao_hash}",
    ]
    if requerimento.requerimento_anterior_id:
        partes.append(f"sucede {requerimento.requerimento_anterior_id}")
    if requerimento.convocacao_autorizadora_id:
        partes.append(f"convocação {requerimento.convocacao_autorizadora_id}")
    record_event(
        actor=ator_do_candidato(identidade, inscricao.edital),
        permission="requerimento:enviar",
        operation=nomes.OPERACAO_SUCESSAO
        if requerimento.requerimento_anterior_id
        else nomes.OPERACAO_ENVIO,
        aggregate=requerimento,
        now=agora,
        correlation_id=correlation_id,
        reason="; ".join(partes),
    )


def autorizacao_para_atualizar(inscricao, conteudo=None):
    """O requerimento enviado e a chamada que autoriza corrigi-lo — **sem gravar nada**.

    **Esta função não cria linha, e a ausência é o conserto de um defeito.** A redação anterior
    criava o sucessor no instante do clique em *Conferir e atualizar*. Como vigente é a folha da
    cadeia, bastava clicar e sair para o requerimento **enviado** sumir da tela da pessoa e do
    dossiê de quem conduz, substituído por um rascunho que ninguém pediu — e a recusa de *"nada
    mudou"* só chegava no envio, tarde demais, com a linha já criada. Contrariava a `FR-406`, que
    manda o enviado continuar legível, e a `FR-410`, que proíbe sucessor sem mudança.

    Quem decide se há sucessor é `atualizar`, e só depois de comparar.
    """
    if conteudo is None:
        conteudo = _conteudo(inscricao).content
    vigente = vigente_de(inscricao)
    if vigente is None:
        raise DomainError(
            nomes.INDISPONIVEL, "Não há requerimento para corrigir nesta inscrição.", 409
        )
    apurado = apurar(inscricao, conteudo)
    if not apurado.exigido:
        raise DomainError(
            nomes.NAO_EXIGIDO, "Este certame não pede Requerimento de Matrícula.", 404
        )
    if vigente.status != nomes.ENVIADO:
        # Já há correção em curso, ou o original nunca foi enviado. Nos dois casos o que existe é um
        # rascunho, e o caminho é continuar preenchendo-o — não abrir outro.
        return vigente, None
    if apurado.chamada is None:
        # **`successor_not_authorized`, e não `matriculation_request_unavailable`.** As duas
        # ausências não são a mesma: `unavailable` diz *"ainda não chegou a sua vez"*, a quem nunca
        # foi chamado; esta diz *"a sua vez passou"*, a quem já enviou e teve a chamada respondida.
        raise DomainError(
            nomes.SUCESSOR_NAO_AUTORIZADO,
            "Só é possível atualizar o Requerimento de Matrícula quando há uma convocação "
            "aguardando a sua resposta.",
            409,
        )
    return vigente, apurado.chamada


def atualizar(*, inscricao, dados, correlation_id=""):
    """Cria o sucessor **se, e somente se, alguma coisa mudou** (`FR-409`, `FR-410`).

    **A comparação vem antes da gravação**, e é essa ordem que faz a `FR-410` ser regra em vez de
    intenção: *"MUST NOT criar sucessor quando nada mudar"*. Comparar depois deixaria a linha
    criada, e a cadeia de sucessão passaria a registrar correções em que nada foi corrigido — quem
    auditasse leria movimento onde não houve nenhum.

    **O sucessor nasce já com o conteúdo novo**, e não com uma cópia a ser editada depois: é o que
    dispensa a linha intermediária que não corrige nada. O antecessor fica intacto e legível
    (`FR-409`) — corrigir não apaga, porque é sob aquela declaração que atos já praticados se
    fundaram.

    **A autorização é a porta, e ela é a regra inteira** (`R-6`). Sucessor só nasce sob chamada em
    aberto, e cita a convocação que o autorizou. Se essa porta afrouxar, o requerimento deixa de
    ser declaração num instante determinado e vira campo editável com histórico.
    """
    conteudo = _conteudo(inscricao).content
    with command_context() as agora:
        _travar(inscricao)
        anterior, chamada = autorizacao_para_atualizar(inscricao, conteudo)
        if chamada is None:
            # Há rascunho em curso: gravar nele é o caminho, e não abrir outro.
            return gravar(
                inscricao=inscricao,
                dados=dados,
                expected_revision=None,
                correlation_id=correlation_id,
            )
        sucessor = RequerimentoDeMatricula(
            inscricao=inscricao,
            status=nomes.RASCUNHO,
            disponibilizado_em=agora,
            created_at=agora,
            requerimento_anterior=anterior,
            convocacao_autorizadora=chamada,
            **{campo: getattr(anterior, campo) for campo in CAMPOS_DECLARADOS},
        )
        for campo, valor in declaracao.sanear(
            RequerimentoDeMatricula, dados, CAMPOS_DA_TELA
        ).items():
            setattr(sucessor, campo, valor)
        _enriquecer_o_endereco(sucessor)
        if _conteudo_declarado(sucessor) == _conteudo_declarado(anterior):
            raise DomainError(
                nomes.SUCESSOR_NAO_AUTORIZADO,
                "Nada mudou em relação ao que você já havia enviado. Altere o que precisa "
                "corrigir, ou volte — o requerimento anterior continua valendo.",
                422,
            )
        sucessor.save()
        return sucessor


def _conteudo_declarado(requerimento):
    """O que a pessoa declarou, para comparar duas declarações campo a campo."""
    return {campo: getattr(requerimento, campo) for campo in CAMPOS_DECLARADOS}


def nada_mudou(requerimento) -> bool:
    """O sucessor diz exatamente o que o antecessor dizia (`FR-410`).

    **A comparação é do comando, e não do template.** A tela evita oferecer o botão; um `POST`
    montado à mão criaria histórico artificial — uma cadeia de correções em que nada foi corrigido —
    e quem auditasse depois leria movimento onde não houve nenhum.

    **Os derivados entram na conta.** Se o CEP mudou para outro que a base reconhece, o código IBGE
    muda junto, e isso é mudança real de endereço mesmo que os campos digitados coincidam.
    """
    anterior = requerimento.requerimento_anterior
    if anterior is None:
        return False
    return _conteudo_declarado(requerimento) == _conteudo_declarado(anterior)
