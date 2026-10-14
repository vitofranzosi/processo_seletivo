# Modelo de dados — 072

**Nenhuma tabela, campo, migration ou dado normativo novo.** O que existe abaixo são estruturas de
leitura, montadas na renderização a partir do que já está gravado, e uma chave de sessão de uso único.

## Leituras derivadas

### Resultado vigente com prazo (`leitura`, extraído de `views.selecao`)

Uma linha por publicação de resultado **vigente** do Edital (a de `historico_publico_dos_editais`),
acrescida de:

| Campo | Origem | Regra |
|---|---|---|
| `recurso_ate` | `janela_da_publicacao_divulgada(publicacao, conteudo=citado, vigente=conteúdo vigente)` | o fim da janela, só se `agora <= fim`; senão `None` |

`agora` é um instante por renderização (FR-1635).

### Resumo do acompanhamento (cartão da vitrine; D-004)

Função pura sobre a lista acima.

| Campo | Regra |
|---|---|
| `total` (M) | número de resultados vigentes |
| `mais_recente` | maior `publicado_em` entre os vigentes |
| `natureza` | a natureza comum a todos, ou vazio quando difere (FR-1630) |
| `abertos` (N) | vigentes com `recurso_ate` |
| `prazo_unico` | o término, quando N = M e todos os términos são iguais (FR-1631) |
| `primeiro_prazo` | o menor término entre os abertos, quando 0 < N e não há `prazo_unico` (FR-1632) |

Sem vigente, a função devolve `None` e o cartão não escreve nada (FR-1633).

### Oferta do Perfil (cartão e cabeçalho da seleção)

| Campo | Regra |
|---|---|
| `nome` | o nome publicado do Perfil |
| `quantidade` | "N vaga(s)", "N vaga(s) e cadastro reserva", "cadastro reserva" ou vazio (FR-1607) |

Listas com teto — Perfis (3 no cartão, 5 no cabeçalho) e lugares (3) — devolvem os itens e quantos
sobraram; com busca ativa, os que casam com o termo vêm primeiro (FR-1608 a FR-1610).

### Vaga do destino (telas de acesso)

`{perfil, numero, ano, titulo}` lidos da versão vigente quando o destino validado é a rota de inscrição
numa vaga; `None` em qualquer outro caso (FR-1619, FR-1620).

## Sessão

| Chave | Conteúdo | Grava | Lê e remove |
|---|---|---|---|
| `portal_volta_a_vaga` | identificador do Perfil e marca "dados guardados" | `_entrar` e `meus_dados`, a caminho de uma vaga | `selecao`, só se o Perfil for do Edital da página |

O e-mail exibido na mensagem vem da sessão do candidato no momento da leitura, e não é copiado para a
chave.
