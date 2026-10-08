"""Os nomes que a 060 fala para fora: a permissão, as recusas e as operações da trilha.

A permissão vai também **escrita por extenso** no papel `gestor` de `interface/identidade.py`, como
todas as daquele mapa — a fronteira de identidade não deve conhecer quem a consome. A grafia das
duas é conferida por `tests/authorization/test_gerir_autoridades.py`.
"""

# Manter as autoridades da própria unidade: cadastrar, corrigir e encerrar (D-005, FR-1122).
GERIR = "autoridade:gerir"

# Recusas da escolha ao publicar (contracts/autoridades-e-publicacao.md).
SIGNATARIO_OBRIGATORIO = "signatario_obrigatorio"
AUTORIDADE_INDISPONIVEL = "autoridade_indisponivel"
AUTORIDADE_FORA_DE_VIGENCIA = "autoridade_fora_de_vigencia"

# Recusas da manutenção.
AUTORIDADE_JA_USADA = "autoridade_ja_usada"
ENCERRAMENTO_RETROATIVO = "encerramento_retroativo"
VIGENCIA_INVERTIDA = "vigencia_invertida"
AUTORIDADE_JA_ENCERRADA = "autoridade_ja_encerrada"
CARGO_OBRIGATORIO = "cargo_obrigatorio"

# Recusas do registro de Unidades.
UNIDADE_NAO_REGISTRADA = "unidade_nao_registrada"
UNIDADE_RETIRADA = "unidade_retirada"
UNIDADE_MALFORMADA = "unidade_malformada"

# O ator da trilha quando quem muda o registro de Unidades é a implantação, e não uma pessoa na
# tela. É sujeito, e não papel: a sincronização não tem permissão a conferir, porque roda com o
# acesso de quem implanta (contracts/registro-de-unidades.md).
IMPLANTACAO = "implantacao"
