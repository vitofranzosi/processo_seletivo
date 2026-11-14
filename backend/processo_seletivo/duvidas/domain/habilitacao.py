"""Os nomes da habilitação do assistente (170): as frentes, a permissão, as recusas e os requisitos.

**A permissão vai também escrita por extenso** no papel `administrador-institucional`, em
`seguranca/acessos.py`, como `unidade:administrar` da `110`: a fronteira de identidade não importa
quem a consome. A grafia das duas é conferida por
`tests/authorization/test_habilitar_assistente.py`.
"""

# Habilitar e desabilitar o assistente, e ler a página da administração (FR-7510).
HABILITAR = "assistente:habilitar"

# As duas frentes (Q-1): o piloto da gestão, uma por implantação; a página pública, por Edital.
PILOTO = "PILOTO"
PAGINA_PUBLICA = "PAGINA_PUBLICA"
FRENTES = (PILOTO, PAGINA_PUBLICA)

# As operações da trilha (R-8).
OPERACAO_HABILITAR = "HABILITAR_ASSISTENTE"
OPERACAO_DESABILITAR = "DESABILITAR_ASSISTENTE"

# A marca da conversa com o atalho de demonstração ligado (R-5): sem ato, a conversa não muda.
MARCA_DA_DEMONSTRACAO = "demonstracao"

# As recusas (contracts/tela.md).
MOTIVO_OBRIGATORIO = "motivo_obrigatorio"
CONFIGURACAO_INCOMPLETA = "configuracao_incompleta"
JA_HABILITADO = "assistente_ja_habilitado"
JA_DESABILITADO = "assistente_ja_desabilitado"
SEM_PAGINA_PUBLICA = "edital_sem_pagina_publica"
ABERTURA_PUBLICA_EM_PRODUCAO = "abertura_publica_em_producao"
SO_ENTRADA_INSTITUCIONAL = "so_entrada_institucional"

# O que falta na configuração do serviço (FR-7501), em palavras de quem decide (UX-810). A ordem é a
# de quem configura: o serviço, o endereço e o modelo, o tokenizer, e a credencial.
FALTAS = {
    "servico": "o serviço do modelo não está configurado",
    "servico_desconhecido": "o serviço configurado não é um dos que o sistema conhece",
    "endereco": "falta o endereço do serviço",
    "modelo": "falta o nome do modelo",
    "biblioteca_do_tokenizer": "falta a biblioteca que lê o tokenizer (o grupo `assistente`)",
    "tokenizer": "falta o tokenizer do modelo",
    "credencial": "falta a credencial do serviço",
}

INSTITUCIONAL = "institucional"
POR_EDITAL = "por Edital"
DE_SOFTWARE = "de software"

# Os doze requisitos da abertura em produção (FR-7533). **Documentação e texto da recusa**, e não
# dado: nesta entrega nenhum se registra, e a recusa de produção nomeia todos. O cadastro é da
# entrega da abertura (spec, tabela "Os requisitos da abertura em produção").
REQUISITOS_DA_ABERTURA = (
    (
        "RA-1",
        "Relatório final do piloto, com os critérios de aceite aprovados e cumpridos",
        INSTITUCIONAL,
    ),
    ("RA-2", "Revisão institucional da fonte de consulta com o setor de seleção", INSTITUCIONAL),
    (
        "RA-3",
        "Manifestação do encarregado de dados sobre o texto livre de candidatos e a retenção",
        INSTITUCIONAL,
    ),
    ("RA-4", "Texto aprovado que declara a natureza não oficial das respostas", INSTITUCIONAL),
    ("RA-5", "Medição da carga pública no serviço local", INSTITUCIONAL),
    ("RA-6", "Cláusula de exclusividade do canal de dúvidas resolvida no Edital", POR_EDITAL),
    ("RA-7", "Revisão das fontes do Edital antes de abrir", POR_EDITAL),
    ("RA-8", "Limite por visitante e proteção contra uso automatizado", DE_SOFTWARE),
    ("RA-9", "Texto definitivo das falhas e da apresentação do painel", DE_SOFTWARE),
    ("RA-10", "Correção do documento ligado, que deve levar à versão vigente", DE_SOFTWARE),
    ("RA-11", "Emenda do canal de dúvidas pela revisão institucional", DE_SOFTWARE),
    ("RA-12", "Retenção própria dos registros da página pública", DE_SOFTWARE),
)
