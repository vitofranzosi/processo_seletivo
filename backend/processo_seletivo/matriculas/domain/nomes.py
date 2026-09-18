"""O vocabulário da exportação de matrículas e os códigos de recusa, ditos uma vez.

**Por que este módulo existe separado.** O mesmo código de recusa aparece na aplicação, na interface
e no teste que o prende; escrevê-lo três vezes é como um deles fica para trás numa renomeação. É a
forma que `convocacao/domain/nomes.py` e `requerimentos/domain/nomes.py` já usam.

**O conceito novo desta feature é a lacuna** — a coluna que sai vazia com a razão declarada. Ele é
do domínio, e não jargão técnico: quem conduz lê *"estas colunas saíram vazias, e por quê"* antes de
baixar o arquivo, e é essa leitura que impede a célula vazia de virar preenchimento manual às
pressas.
"""

# --- A permissão (`FR-455`) ---------------------------------------------------------------------
# **Própria, e o conteúdo é a razão.** O arquivo reúne, numa linha só, CPF, RG, filiação e endereço
# de cada convocado — é o artefato mais concentrado de dado pessoal que este sistema produz. Quem lê
# o dossiê de uma Inscrição vê uma pessoa por vez, e `inscricao:consultar` autoriza isso; baixar o
# conjunto inteiro é outro ato (Princípio III).
EXPORTAR = "matricula:exportar"

# --- As espécies de população (`FR-433`) --------------------------------------------------------
# **Duas, e nenhuma é padrão.** Não existe *"exportar tudo"*: o arquivo tem o conjunto que alguém
# escolheu e nomeou, e a ausência de escolha recusa a geração em vez de assumir uma.
#
# `CONVOCACAO` — os convocados de um marco de classificação: quem foi chamado e não teve a chamada
# desfeita por desistência, indeferimento ou inércia. É a população da matrícula corrente.
# `RESULTADO` — o conjunto de um resultado divulgado, pela publicação que o divulgou.
CONVOCACAO = "CONVOCACAO"
RESULTADO = "RESULTADO"
ESPECIES_DE_POPULACAO = (CONVOCACAO, RESULTADO)

# --- As três formas de não ter valor (contrato, §"As três formas") ------------------------------
# **Distintas de propósito, e o relatório não as colapsa.**
#
# `EXTERNA` — o valor é vocabulário de outro sistema, e este nunca o teve (`D-001`). Não é falha de
#   ninguém, e o relatório diz *"preencher no destino"*.
# `NOMINAL` — o sistema **tem** um valor declarado e o destino não o comporta, ou não foi
#   confirmado. Sai vazia **e a pessoa é nomeada**, porque apagar uma declaração em silêncio é o
#   defeito que esta feature existe para não cometer.
# `DIVERGENCIA` — a coluna sai **preenchida**, e o que ela mede não é o que o destino define
#   (`D-002`). Não é lacuna de valor; é lacuna de significado, e ela viaja em toda geração
#   (`FR-452`).
# `AUSENCIA` — a pessoa simplesmente não declarou, e a coluna não a exige. Nome do pai, complemento
#   do endereço e necessidade específica são ausências legítimas, e o relatório as conta **sem
#   nomear ninguém**: listar quem não declarou o nome do pai exporia uma ausência legítima sem
#   nenhum ganho para quem lê.
AUSENCIA = "AUSENCIA"
EXTERNA = "EXTERNA"
NOMINAL = "NOMINAL"
DIVERGENCIA = "DIVERGENCIA"
ESPECIES_DE_LACUNA = (AUSENCIA, EXTERNA, NOMINAL, DIVERGENCIA)

# --- Recusas (`FR-435`, `FR-441`, `FR-455`) -----------------------------------------------------
# **A recusa diz o que falta e de quem** (`UX-061`), nunca *"não foi possível gerar"*. As quatro
# separam fatos diferentes: escolher nada, população sem gente, gente sem declaração, e grafia que
# obrigaria a exportação a inventar uma correspondência.
POPULACAO_NAO_ESCOLHIDA = "population_not_chosen"
# **O download que não corresponde ao resumo lido** (`UX-060`). Não é falha de permissão nem de
# dado: é o mundo ter mudado entre conferir e baixar — uma sucessão de requerimento, um desfecho
# registrado, mais alguém convocado. `409`, como a prévia obsoleta da `017`, porque a resposta
# certa é reler e tentar de novo.
RESUMO_NAO_CONFERIDO = "export_preview_stale"
POPULACAO_VAZIA = "empty_population"
DECLARACAO_FALTANDO = "declaration_missing"
MODALIDADE_DESCONHECIDA = "unknown_modality_code"
RECUSAS = (
    POPULACAO_NAO_ESCOLHIDA,
    RESUMO_NAO_CONFERIDO,
    POPULACAO_VAZIA,
    DECLARACAO_FALTANDO,
    MODALIDADE_DESCONHECIDA,
)

# --- A operação, para a trilha ------------------------------------------------------------------
# **Uma só, e ela não é a geração.** O arquivo tem registro próprio — `GeracaoDeArquivo` —, e
# duplicá-lo na trilha criaria duas fontes para o mesmo fato. O que a trilha registra é a **prévia
# que nomeia pessoas**: ela exibe cor/raça e nacionalidade declaradas, nominalmente, e é a única
# leitura desta feature que mostra dado sensível sem produzir arquivo nenhum.
#
# **O nome segue a forma do resto do mapa** — `APP_ATO`, em maiúsculas, como `CONVOCACAO_CONVOCAR`
# e `REQUERIMENTO_ENVIAR`. Ele tem rótulo em `interface/views.py::OPERACOES`; sem isso a trilha
# exibiria o código cru a quem pergunta quem leu o quê.
OPERACAO_PREVIA = "MATRICULA_PREVER"

# --- O formato físico (`FR-436`) ----------------------------------------------------------------
# A aba tem **este** nome, e os 34 cabeçalhos saem na grafia exata do destino. Nenhum dos dois é
# configurável: quem os muda está mudando o contrato com o Registro Acadêmico, e isso é conversa,
# não parâmetro.
ABA = "Import_ModeloCefor"
TIPO_DO_ARQUIVO = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
