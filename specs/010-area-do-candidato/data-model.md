# Modelo de dados — 010 Área do Candidato

**Spec**: [spec.md](./spec.md) · **Decisões**: [research.md](./research.md)

Três tabelas novas, uma restrição acrescentada a uma tabela existente, e nenhuma alteração
destrutiva. `Inscricao` e `DocumentoSubmetido` são consumidas como estão.

---

## CandidateIdentity — a identidade do candidato

Quem é a pessoa para o sistema, de forma persistente. Não guarda permissão alguma: o candidato não é
ator institucional (P-006).

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, chave primária | gerado na criação |
| `subject` | texto, único | `cand:` + 32 hexadecimais de UUID4 para identidades novas (D-002); para as reconciliadas, **exatamente** o valor que as inscrições já carregam |
| `nome` | texto | vazio até a primeira inscrição; editável pelo titular a qualquer momento (`FR-008`) |
| `cpf_normalizado` | texto, 11 dígitos | vazio até a primeira inscrição; declarado, nunca provado (`FR-007`); congela na primeira inscrição enviada |
| `created_at` | instante | absoluto |

**Invariantes**

- `subject` é único e é o **único** dado que decide propriedade de Inscrição (`FR-001`).
- `subject` de identidade nova não deriva de segredo de configuração nem de dado pessoal (`FR-002`).
- `cpf_normalizado`, quando presente, é um CPF de formação válida (`FR-006`) — o que **não** prova
  titularidade e nunca é tratado como se provasse.
- Não há restrição de unicidade sobre `cpf_normalizado`. Duas identidades podem declarar o mesmo CPF
  (`FR-064`), e a coincidência é assinalada onde importa, não bloqueada onde machuca.

**Relacionamentos**

- Para `Inscricao`: por valor, através de `subject`. **Não** é chave estrangeira, e não passa a ser —
  a `FR-042` proíbe tocar naquele campo. É essa ausência que obriga o bloqueio compartilhado de
  D-010.
- Para `CandidateEmail`: uma para muitas.

---

## CandidateEmail — a credencial

Um endereço cujo controle foi provado.

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, chave primária | |
| `identidade` | referência | em cascata com a identidade: credencial sem dona não é nada |
| `email_canonico` | texto, **único no sistema** | forma canônica conservadora (D-006) |
| `email_como_informado` | texto | preservado para exibição; nunca decide identidade |
| `principal` | booleano | exatamente um por identidade que tenha credencial |
| `verified_at` | instante | só existe linha se houve prova |
| `created_at` | instante | |

**Invariantes**

- `email_canonico` é único em todo o sistema, **por restrição de banco** (`FR-011`). Verificação
  prévia à gravação não serve: duas confirmações simultâneas passariam pelas duas verificações.
- Uma identidade com credencial tem exatamente um `principal` (`FR-013`, `FR-018`).
- A última credencial de uma identidade não pode ser removida (`FR-018`).
- Não existe linha "não verificada": a tabela guarda credencial provada. O que a `009` gravou em
  `Inscricao.email` é indício histórico, não credencial (`FR-015`).

---

## DesafioDeAcesso — a tentativa de provar controle

Não é dado permanente de domínio (`FR-033`).

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID, chave primária | |
| `email_canonico` | texto, indexado | o endereço a que o desafio se refere |
| `finalidade` | texto | `entrar`, `adicionar_credencial` ou `retomar` (`FR-028`) |
| `codigo_hash` | texto | resumo salgado; nunca o código (`FR-027`, D-003) |
| `origem_hash` | texto, indexado | resumo da origem da solicitação; nunca o endereço de rede em claro (D-005) |
| `expira_em` | instante | criação + 10 minutos (`FR-024`) |
| `tentativas_codigo` | inteiro | teto de 5 (`FR-029`) |
| `tentativas_cpf` | inteiro | teto de 5 na confirmação da reconciliação (`FR-052a`, D-016) |
| `consumido_em` | instante, opcional | marca o uso único do código |
| `reconciliacao_ate` | instante, opcional | enquanto presente e futuro, esta linha porta a reconciliação pendente (`FR-052b`) |
| `reconciliacao_alvo` | referência opcional | a identidade que o convite anunciou, quando havia uma só; é ela que a confirmação de CPF confere, e não o resultado de uma busca refeita (D-020) |
| `criado_em` | instante, indexado | base das janelas de limite |

**Invariantes e transições**

```text
criado ──(código correto, no prazo, tentativas_codigo < 5)──► consumido
   │                                                             │
   ├──(tentativas_codigo = 5)───────────────► morto  [terminal]  │
   ├──(prazo vencido)───────────────────────► expirado [terminal]│
   └──(novo desafio no mesmo endereço)──────► invalidado [terminal]
                                                                 │
        sem correspondência anterior ────────────────────────────┤──► encerrado [terminal]
                                                                 │
        com correspondência anterior: reconciliação pendente ────┘
                    │
                    ├──(CPF confere)──────────────────► reconciliado [terminal]
                    ├──(tentativas_cpf = 5)───────────► encerrado    [terminal]
                    ├──(recusa explícita)─────────────► encerrado    [terminal]
                    └──(reconciliacao_ate vencido)────► encerrado    [terminal]
```

Consumir o código **não** é o fim da linha quando há correspondência anterior: é ela que porta a
decisão pendente, porque a sessão não serve de portador — uma aba nova zeraria a contagem — e a
identidade alvo serviria de alvo, permitindo a um terceiro esgotar as tentativas e bloquear o titular
legítimo (D-016). Todo desfecho `encerrado` leva a pessoa à própria identidade, com sessão válida:
nenhum deles é beco sem saída (`FR-052`, P-009).

- O consumo é atômico: uma atualização condicional que só vale se afetar exatamente uma linha
  (`FR-025`, D-004). Ler, verificar e gravar depois deixaria duas abas usarem o mesmo código.
- Um novo desafio invalida os anteriores ainda utilizáveis do mesmo endereço (`FR-026`).
- Os limites por endereço e por origem são contagens sobre `criado_em`, na própria tabela (D-005).
- Os dois contadores são incrementados por atualização condicional, como o consumo (D-004): duas abas
  não dividem o mesmo orçamento de tentativas por engano.
- `reconciliacao_alvo` referencia a identidade com `SET_NULL`, e não em cascata: ele **anota** o que
  o convite anunciou, e não compõe nada com ela. Apagar uma identidade não pode levar junto o
  desafio que a aponta — nem o contador de tentativas que ele guarda (D-020).

**A finalidade `retomar`** existe porque a retomada não é um `entrar` com outro nome: ela move
credenciais e descarta uma identidade. Um código pedido para entrar não pode autorizar isso, e a
contagem de tentativas de CPF vale igual nos dois caminhos (D-016).
- Linhas terminais são descartáveis por rotina operacional (`FR-033`).

---

## Inscricao — existente, com uma restrição a mais

Nada muda em `identity_subject`, em estados, em protocolo ou em imutabilidade. Acrescenta-se:

- **Restrição de verificação**: inscrição no estado enviado tem `cpf_normalizado` com exatamente
  onze dígitos (`FR-063`). Ela entra no mesmo bloco que já exige instante, protocolo, versão aceita e
  aceite das declarações.
- **O que a restrição não afirma**: os dígitos verificadores. O algoritmo não cabe em restrição
  declarativa, e a conferência permanece onde já está — na captura, e na verificação que a
  implantação faz antes de instalar a restrição (D-017). A restrição garante que a coluna é
  utilizável; o domínio garante que o número é um CPF possível.
- **Nada de restrição de unicidade por CPF.** `FR-064` é explícita: duas inscrições enviadas com o
  mesmo CPF no mesmo Perfil são aceitas. A restrição existente por identidade, Edital e Perfil
  permanece intacta (`FR-062`).

---

## A migração de reconciliação

Roda uma vez, na implantação, antes de qualquer acesso (`FR-040`, D-007).

**Duas migrações, nesta ordem**

```text
identidade.0002_reconciliacao      verifica, cria as identidades, interrompe se precisar
              ↓  (depends_on)
inscricoes.0003_cpf_na_submetida   instala a restrição da FR-063
```

São duas porque a restrição incide sobre `Inscricao`, e restrição de modelo mora no app que o define.
A ordem não é preferência: instalar antes de verificar faria a implantação falhar no `ALTER TABLE`,
com a mensagem do banco em vez do relatório que enumera o que precisa de tratamento.

**O que a primeira faz**

1. Agrupa as inscrições existentes por `cpf_normalizado`.
2. Verifica as enviadas: encontrando CPF inutilizável, **interrompe** (`FR-046`).
3. Para cada grupo com **um único** `identity_subject`: cria a identidade com aquele `subject`, aquele
   CPF, e o `nome` da inscrição mais recente do grupo (`FR-041`).

**O que ela nunca faz**

- Reescrever `identity_subject` de qualquer inscrição (`FR-042`).
- Marcar endereço como verificado (`FR-043`).
- Escolher um dado para desempatar (`FR-047`).

**Como ela termina em cada caso**

| Situação encontrada | Desfecho |
|---|---|
| Grupo com um `subject` | identidade criada, `subject` preservado |
| Grupo com mais de um `subject` | **não** cria identidade; registra em log os `subject` e os identificadores das inscrições — nunca o CPF (`FR-009`, `FR-044`); as inscrições ficam intactas e sem novo dono (`FR-047`) |
| Rascunho sem CPF utilizável | registra em log, deixa intacto, não reconcilia (`FR-045`) |
| **Inscrição enviada sem CPF utilizável** | **interrompe a implantação**, enumerando as inscrições que a impediram (`FR-046`) |

A assimetria entre as duas últimas linhas é deliberada: um rascunho inválido não impede a restrição
da `FR-063` de existir; uma inscrição enviada inválida impede. Prosseguir exigiria escolher um dado
por conta própria, e é isso que a `FR-047` proíbe.

---

## O contrato que a `009` consome

`IdentidadeDoCandidato(subject, nome, cpf, email)` permanece como está (P-008). Muda a origem:

| Campo | Antes (`009`) | Agora |
|---|---|---|
| `subject` | derivado do CPF por segredo da aplicação | `CandidateIdentity.subject` |
| `nome` | declarado no formulário | `CandidateIdentity.nome` |
| `cpf` | declarado no formulário | `CandidateIdentity.cpf_normalizado`, formatado |
| `email` | declarado no formulário | a credencial **principal** da identidade (`FR-013`) |

A sessão guarda apenas o identificador da identidade; os quatro campos são lidos do registro a cada
requisição (D-008). É o que faz a correção de nome alcançar os rascunhos abertos sem que a pessoa
precise sair e entrar (`FR-014`).
