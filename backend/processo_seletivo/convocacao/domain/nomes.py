"""O vocabulário da convocação e os códigos de recusa, ditos uma vez.

**Por que este módulo existe separado.** O mesmo código de recusa aparece na aplicação, na
interface e no teste que o prende; escrevê-lo três vezes é como um deles fica para trás numa
renomeação. É a forma que `ocupacao/domain/nomes.py` e `classificacao/domain/nomes.py` já usam.

**O que deliberadamente NÃO está aqui: as formas de comunicar.** `PUBLICATION` e
`INDIVIDUAL_MESSAGE` são vocabulário do **conteúdo publicado**, e moram onde o publicado as define
— `publicacoes/domain/vocabulario_da_regra.py`. Duas grafias do mesmo valor em módulos diferentes é
como uma delas fica para trás numa renomeação, e aqui a renomeação seria uma Retificação.

**O vocabulário é verificado por varredura** (`019`, `UX-035` e `UX-039`): esta feature não afirma
contagem de ocupação — o número é da `016` —, não diz *"recebido em"*, *"lido em"* nem *"entregue
em"*, e não diz *"direito à vaga"*. A fronteira vale nos dois sentidos: a `016` continua proibida
de falar de convocação (`UX-034`).
"""

from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao

# --- Espécies de convocação (019, data-model §1) ------------------------------------------------
# **Três, e a terceira não se chama `REGULARIZACAO`.** O mesmo termo para o ato e para o desfecho
# confunde tela e código: convoca-se **para regularizar**, e o que a pessoa faz em seguida é a
# regularização. São momentos distintos, e o nome de cada um os mantém distintos.
VAGA_INICIAL = "VAGA_INICIAL"
SUPLENCIA = "SUPLENCIA"
PARA_REGULARIZAR = "PARA_REGULARIZAR"
ESPECIES_DE_CONVOCACAO = (VAGA_INICIAL, SUPLENCIA, PARA_REGULARIZAR)

# --- Espécies de desfecho (019, R-006) ----------------------------------------------------------
# **Sete, e os dois últimos de exclusão são distintos de propósito** (`D-011`). *Não atendimento à
# convocação* e *cancelamento de matrícula por inércia* têm atores, prazos e fundamentos
# diferentes: o segundo depende de atestado de fato externo; o primeiro, do vencimento informado.
# Colapsá-los num só apagaria norma.
ACEITE = "ACEITE"
REGULARIZACAO = "REGULARIZACAO"
INDEFERIMENTO = "INDEFERIMENTO"
DESISTENCIA_EXPRESSA = "DESISTENCIA_EXPRESSA"
NAO_ATENDIMENTO = "NAO_ATENDIMENTO"
INERCIA = "INERCIA"
RECLASSIFICACAO = "RECLASSIFICACAO"
ESPECIES_DE_DESFECHO = (
    ACEITE,
    REGULARIZACAO,
    INDEFERIMENTO,
    DESISTENCIA_EXPRESSA,
    NAO_ATENDIMENTO,
    INERCIA,
    RECLASSIFICACAO,
)

# **O efeito de cada desfecho na porta é declarado, nunca inferido** (`R-006`). Duas linhas incluem
# e cinco excluem — e é a inclusão que impede o número de só descer: sem ela, a suplente que aceita
# nunca entraria na contagem. A reclassificação exclui **e** move na fila; o movimento é da
# `domain/fila.py`, porque a porta só conhece exclusão e inclusão.
EFEITO_POR_DESFECHO = {
    ACEITE: nomes_da_ocupacao.EFEITO_INCLUSAO,
    REGULARIZACAO: nomes_da_ocupacao.EFEITO_INCLUSAO,
    INDEFERIMENTO: nomes_da_ocupacao.EFEITO_EXCLUSAO,
    DESISTENCIA_EXPRESSA: nomes_da_ocupacao.EFEITO_EXCLUSAO,
    NAO_ATENDIMENTO: nomes_da_ocupacao.EFEITO_EXCLUSAO,
    INERCIA: nomes_da_ocupacao.EFEITO_EXCLUSAO,
    RECLASSIFICACAO: nomes_da_ocupacao.EFEITO_EXCLUSAO,
}

# **Que desfecho cabe em que chamada** — e a tabela existe porque nem toda combinação é possível
# juridicamente. O enum sozinho aceitaria `ACEITE` numa convocação para regularizar, incluindo a
# pessoa na contagem de ocupantes sem que Resultado nenhum a habilitasse; e `REGULARIZACAO` numa
# chamada para vaga, produzindo sucessor de um Resultado que não estava indeferido.
#
# **`INERCIA` não cabe na chamada para regularizar**: não há matrícula a cancelar antes de a pessoa
# ter regularizado. **`REGULARIZACAO` não cabe na chamada para vaga**: o que ela sucede é um
# indeferimento, e ali não há um.
DESFECHOS_POR_ESPECIE = {
    VAGA_INICIAL: (
        ACEITE,
        INDEFERIMENTO,
        DESISTENCIA_EXPRESSA,
        NAO_ATENDIMENTO,
        INERCIA,
        RECLASSIFICACAO,
    ),
    SUPLENCIA: (
        ACEITE,
        INDEFERIMENTO,
        DESISTENCIA_EXPRESSA,
        NAO_ATENDIMENTO,
        INERCIA,
        RECLASSIFICACAO,
    ),
    PARA_REGULARIZAR: (
        REGULARIZACAO,
        INDEFERIMENTO,
        DESISTENCIA_EXPRESSA,
        NAO_ATENDIMENTO,
        RECLASSIFICACAO,
    ),
}

#: Os dois desfechos que **incluem** na contagem, e portanto pressupõem que a pessoa passe a ocupar.
DESFECHOS_QUE_INCLUEM = (ACEITE, REGULARIZACAO)

# --- Espécies de atestado de fato externo (019, data-model §3) ----------------------------------
# O sistema **não detém o artefato** e não infere o fato: registra que alguém competente concluiu.
ATESTADO_NAO_ACESSO_AO_AMBIENTE = "NAO_ACESSO_AO_AMBIENTE"
ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA = "AUSENCIA_NA_PRIMEIRA_SEMANA"
ATESTADO_NAO_ENTREGA_PRESENCIAL = "NAO_ENTREGA_PRESENCIAL"
ESPECIES_DE_ATESTADO = (
    ATESTADO_NAO_ACESSO_AO_AMBIENTE,
    ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA,
    ATESTADO_NAO_ENTREGA_PRESENCIAL,
)

# --- Códigos de recusa (019, contrato §3) -------------------------------------------------------
APURACAO_AUSENTE = "apuracao_ausente"
APURACAO_OBSOLETA = "apuracao_obsoleta"
SEM_DEFICIT = "sem_deficit"
FORA_DA_FAIXA = "fora_da_faixa"
ORDEM_NAO_VIGENTE = "ordem_nao_vigente"
PRECEDENCIA_NA_ORDEM = "precedencia_na_ordem"
CONVOCACAO_VIGENTE_EXISTENTE = "convocacao_vigente_existente"
REABILITADO_A_FRENTE = "reabilitado_a_frente"
VENCIMENTO_ANTERIOR_AO_ENVIO = "vencimento_anterior_ao_envio"
DESFECHO_JA_REGISTRADO = "desfecho_ja_registrado"
ATESTADO_OBRIGATORIO = "atestado_obrigatorio"
RECLASSIFICADO_ANTES_DO_ESGOTAMENTO = "reclassificado_antes_do_esgotamento"
LISTA_ALCANCADA_ESGOTADA = "lista_alcancada_esgotada"
FORMA_DE_COMUNICACAO_NAO_DECLARADA = "forma_de_comunicacao_nao_declarada"
MOTIVO_DA_SUCESSAO_OBRIGATORIO = "motivo_da_sucessao_obrigatorio"

# **Este não é reescrito aqui, e a diferença é a que importa**: quem recusa é `ocupacao.apurar`,
# e a grafia mora com quem a levanta. Reescrevê-la produziria duas cadeias de caracteres iguais
# hoje e divergentes depois.
EMPATE_NA_FRONTEIRA_DO_ALVO = nomes_da_ocupacao.EMPATE_NA_FRONTEIRA_DO_ALVO

# **Reexportado pela mesma razão**: "declare o fundamento deste ato" é a mesma recusa, e a `019` a
# levanta nos mesmos termos que a porta da `016`. Duas constantes com o mesmo valor divergiriam na
# primeira renomeação, e a tela exibiria um código que a aplicação já não emite.
FUNDAMENTO_OBRIGATORIO = nomes_da_ocupacao.FUNDAMENTO_OBRIGATORIO

# Espécie fora das três declaráveis. Não está no contrato porque não é regra do certame: é forma de
# entrada, e a tela nunca a produz — só um cliente escrevendo à mão chega aqui.
ESPECIE_DE_CONVOCACAO_INVALIDA = "especie_de_convocacao_invalida"
ESPECIE_DE_DESFECHO_INVALIDA = "especie_de_desfecho_invalida"
ESPECIE_DE_ATESTADO_INVALIDA = "especie_de_atestado_invalida"

# **Duas recusas do atestado, e as duas são sobre o que ele precisa dizer para atestar alguma
# coisa.** Sem a conclusão ele não conclui nada; sem a referência do prazo ele diz "não apareceu"
# sem dizer até quando a pessoa deveria ter aparecido — e é contra esse prazo que a inércia se mede.
CONCLUSAO_OBRIGATORIA = "conclusao_obrigatoria"
REFERENCIA_DO_PRAZO_OBRIGATORIA = "referencia_do_prazo_obrigatoria"

# **A publicação precisa dizer onde publicou.** O sistema não publica no site do certame, e gravar
# a emissão sem a referência iniciaria o prazo de uma convocação que ninguém viu (`FR-288`).
REFERENCIA_DA_PUBLICACAO_OBRIGATORIA = "referencia_da_publicacao_obrigatoria"

# **A emissão que reservou a chave e não chegou a registrar o desfecho.** Ou está em curso noutra
# requisição, ou saiu e a gravação falhou depois dela — e as duas hipóteses têm a mesma aparência.
# Reenviar por conta própria entregaria a mesma convocação duas vezes; o desfecho honesto é dizer
# que o estado é indeterminado e pedir reconciliação.
EMISSAO_EM_ESTADO_INDETERMINADO = "emissao_em_estado_indeterminado"

# **Duas recusas que o contrato não lista, e são consequência da sucessão.** Corrigida a convocação,
# é a sucessora que vale: gravar o desfecho na anterior o deixaria invisível para a leitura do
# recorte, que só olha as vigentes, e a pessoa apareceria como não tendo respondido. E a
# regularização sem Resultado sucessor seria inclusão na contagem sem habilitação que a sustente.
CONVOCACAO_SUCEDIDA = "convocacao_sucedida"

# **Três recusas sobre *qual* desfecho cabe, e não sobre a forma dele.** O enum diz que a espécie
# existe; estas dizem que ela não cabe **nesta** chamada, **agora**, ou **para esta pessoa**. Sem
# elas o comando aceitaria transições juridicamente impossíveis, e o registro delas é append-only.
DESFECHO_INCOMPATIVEL_COM_A_CHAMADA = "desfecho_incompativel_com_a_chamada"
NAO_ATENDIMENTO_ANTES_DO_VENCIMENTO = "nao_atendimento_antes_do_vencimento"
INERCIA_SEM_OCUPACAO = "inercia_sem_ocupacao"
MOTIVO_DA_SUCESSAO_DO_DESFECHO_OBRIGATORIO = "motivo_da_sucessao_do_desfecho_obrigatorio"
REGULARIZACAO_EXIGE_SUCESSOR = "regularizacao_exige_sucessor"

# --- Guarda de implantação, e não de domínio (019, contrato §3) ---------------------------------
# **Separada de propósito.** Não é regra do certame: é recusa de subir com duas normas
# contraditórias vigentes no mesmo repositório. A `FR-084` da `010` diz que o sistema envia mensagem
# em exatamente duas situações e que acrescentar uma terceira exige revisar a regra — e a convocação
# é a terceira. Enquanto a revisão não estiver escrita, mensagem individual não existe.
ENVIO_SEM_REVISAO_DA_010 = "envio_sem_revisao_da_010"

# --- Estado de leitura derivado (019, R-009) ----------------------------------------------------
# **Derivado, e não coluna**, pela mesma razão que a `016` calcula obsolescência em vez de
# guardá-la:
# coluna exigiria `UPDATE` em tabela append-only. Sem este estado, falha de infraestrutura fica
# indistinguível de silêncio da pessoa — e o desfecho que decorre disso é perda de vaga.
CONVOCADO_PRAZO_NAO_INICIADO = "CONVOCADO_PRAZO_NAO_INICIADO"
CONVOCADO_PRAZO_EM_CURSO = "CONVOCADO_PRAZO_EM_CURSO"
CONVOCADO_VENCIMENTO_DECORRIDO = "CONVOCADO_VENCIMENTO_DECORRIDO"
DESFECHADO = "DESFECHADO"
