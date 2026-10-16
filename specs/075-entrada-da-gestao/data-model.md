# Data model — 075

Nenhuma tabela e nenhuma migration.

## A identidade da sessão (`interface_identidade`)

| Campo | Antes | Agora |
|---|---|---|
| `subject` | o nome escolhido | igual |
| `escopo` | `cefor` | igual |
| `papeis` | as chaves de `PAPEIS` marcadas | igual; chaves desconhecidas são descartadas no envio |
| `origem` | — | `"demonstracao"` (`FR-1698`). Sessão sem o campo conta como demonstração (`D-005`) |

## `DESCRICOES` (`interface/identidade.py`)

Mapa papel → frase, com exatamente as chaves de `PAPEIS` (`FR-1701`).

## As entradas da escolha (`interface/demonstracao.py`)

- **De comissão**: `subject`, iniciais, responsabilidade (Presidência de comissão / Avaliação /
  Membro de comissão), códigos dos Processos, Etapas alocadas, avaliações pendentes.
- **De responsabilidade**: chave do papel, rótulo, descrição, ícone, `subject` sugerido (o de quem
  mais usou as permissões do papel na trilha do escopo, sem candidatos nem `implantacao`; ou
  `demo.<papel>`).
