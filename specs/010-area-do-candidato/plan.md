# Implementation Plan: Área do Candidato e Acesso sem Senha

**Branch**: `claude/spec-010-candidate-area-746d47` | **Date**: 2026-09-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-area-do-candidato/spec.md`

## Summary

A feature dá ao candidato uma identidade persistente e uma área pessoal, autenticadas por código de
uso único enviado ao seu e-mail, sem senha. Ela substitui o provedor de identidade de demonstração da
`009` preservando integralmente a titularidade do que já foi submetido, e entrega a lista de
inscrições, a retomada de rascunho, a reconferência de dados e documentos, o comprovante e o
acompanhamento do certame.

**A descoberta que mais determina o desenho**: a reconciliação com os dados anteriores não pode
acontecer no primeiro acesso de cada pessoa. Enquanto ela não ocorre, a propriedade das inscrições
continua derivada de um segredo de configuração, e rotacioná-lo tornaria cada inscrição inalcançável
pelo seu titular, em silêncio. Por isso ela é **migração de dados**, roda uma vez na implantação, e
tem permissão para **interromper** quando encontra dado que não consegue reconciliar sem inventar
(D-007).

**A descoberta que mais economiza**: o contrato que a abertura de rascunho consome —
`IdentidadeDoCandidato(subject, nome, cpf, email)` — não precisa mudar. Trocar quem o preenche é
suficiente, e é o que mantém a jornada da `009` intacta enquanto o provedor por baixo é substituído
(D-008).

**A que mais custa em rigor**: `Inscricao` não referencia a identidade por chave estrangeira. A
movimentação de credenciais da `FR-053` precisa, por isso, de bloqueio de linha tomado **também** na
abertura de rascunho — senão um rascunho nasce entre a verificação e o descarte, e fica órfão de uma
identidade que deixou de existir (D-010).

**Nenhuma dependência nova.** `backend/pyproject.toml` permanece como está.

## Technical Context

**Language/Version**: Python 3.13 (`backend/pyproject.toml`).

**Primary Dependencies**: Django 5.2, DRF 3.16. Nenhuma dependência nova. O envio de mensagem usa a
API de e-mail da própria plataforma; o resumo do código usa os *hashers* que já vêm com ela (D-003,
D-014).

**Storage**: PostgreSQL. Três tabelas novas — identidade, credencial de e-mail e desafio de acesso —
e nenhuma alteração destrutiva nas existentes. A única alteração em tabela existente é a restrição que
passa a exigir CPF utilizável em inscrição enviada (`FR-063`). Ela mora no app que define `Inscricao`,
e portanto é **uma segunda migração**, que depende da que reconcilia (D-007).

**Testing**: pytest com pytest-django e os marcadores já registrados em `pyproject.toml` —
`acceptance`, `contract`, `integration`, `authorization`, `performance`. Esta feature usa
intensamente `authorization`: a demonstração de segurança da spec é condição de conclusão, e cada um
dos seis casos vira teste.

**Target Platform**: servidor Linux; navegador do candidato, incluindo celular — `UX-009` fixa 375 px
sem rolagem horizontal.

**Project Type**: aplicação web renderizada no servidor. Dois canais HTML já existentes — `/gestao/`
para o ator institucional e o portal para o candidato — e esta feature só toca o segundo.

**Performance Goals**: nada de vazão. O alvo é de percurso: `SC-001` fixa duas telas e menos de 60
segundos no acesso recorrente. O custo acrescentado por requisição é a leitura da identidade a partir
da sessão (D-008), na mesma ordem das consultas que a página já faz.

**Constraints**: o candidato nunca recebe permissão institucional; nenhum caminho concede acesso a
partir de dado declarado; nenhuma inscrição existente muda de titular; e a aplicação recusa subir em
produção com mecanismo de envio que não entrega.

**Scale/Scope**: centenas a poucos milhares de identidades por seleção. Seis fatias entregáveis, três
telas novas de acesso, duas telas novas de área pessoal e uma de credenciais.

## Constitution Check

*GATE: verificado antes da Fase 0 e reavaliado após a Fase 1.*

**I — Linguagem ubíqua e integridade do domínio.** Os conceitos novos são três e não colidem com
nenhum existente: Identidade do Candidato, Credencial de E-mail e Desafio de Acesso. Candidato já era
termo do domínio, e a identidade não o redefine — dá-lhe persistência. Identificadores são estáveis e
não conferem autorização. Os invariantes que importam vão para restrição de banco: exclusividade do
endereço canônico (`FR-011`), CPF utilizável em inscrição enviada (`FR-063`), e a restrição existente
de uma inscrição por identidade, Edital e Perfil permanece intacta (`FR-062`). **Passa.**

**II — Integridade normativa, imutabilidade e temporalidade.** Nada aqui altera Publicação, Retificação
ou versão consolidada. A versão aceita por uma inscrição permanece imutável, e o aviso de Edital
atualizado não a toca (`FR-078`, `FR-079`). Os instantes do desafio são absolutos e persistidos
(`FR-024`). **Passa.**

**III — Segurança, proteção de dados e auditoria.** É o eixo desta feature. Negação por padrão,
titularidade verificada no servidor, resposta que não permite enumerar, e a demonstração de segurança
como condição de conclusão. Minimização: CPF fora de endereço de página e fora de log; origem das
solicitações guardada como resumo, não em claro (D-005); código nunca persistido em forma
recuperável. Auditoria na trilha existente, com a limitação de escopo declarada de frente em D-012.
**Passa, com a decisão D-012 registrada.**

**IV — Regras explícitas e consistência operacional.** Todas as decisões de acesso são de domínio e
verificadas no servidor. Concorrência tratada nos três pontos onde ela morde: consumo do código
(D-004), exclusividade do endereço (`FR-011`, por restrição e não por consulta prévia) e movimentação
de credenciais (D-010). **Passa.**

**V — Qualidade, rastreabilidade e simplicidade.** Nenhuma dependência nova, nenhum serviço novo,
nenhum motor genérico. As duas tentações foram recusadas com motivo escrito: cache compartilhado
(D-005) e comando de reconciliação à parte (D-007). Rastreabilidade por `FR`/`SC` da spec até os
testes. **Passa.**

**VI — Completude de jornada e valor demonstrável.** As seis entregas da spec terminam, cada uma, em
comportamento observável no navegador do candidato. A primeira já vai de informar o endereço até
chegar à área — a identidade persistente não é entrega separada. **Passa.**

**Reavaliação após a Fase 1**: o desenho não introduziu violação nova. Ele fechou dois pontos que a
avaliação inicial deixara em aberto — onde os eventos de credencial aparecem (e onde não aparecem), e
quem serializa a criação de rascunho contra o descarte de identidade.

## Project Structure

### Documentation (this feature)

```text
specs/010-area-do-candidato/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — quinze decisões, com alternativas recusadas
├── data-model.md        # Fase 1 — entidades, invariantes e a migração de reconciliação
├── quickstart.md        # Fase 1 — como validar cada fatia no navegador
├── contracts/
│   ├── acesso.md        # As rotas do desafio, da sessão e da reconciliação
│   └── area.md          # As rotas da área pessoal e dos documentos
├── checklists/
│   └── requirements.md  # Checklist de qualidade da spec
└── tasks.md             # Fase 2 — gerado pelo $speckit-tasks, não por este comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── identidade/                     # APP NOVO — o domínio da identidade do candidato
│   ├── domain/
│   │   ├── enderecos.py            # forma canônica do e-mail (D-006)
│   │   └── codigo.py               # geração, resumo e verificação do código (D-003)
│   ├── application/
│   │   ├── desafio.py              # solicitar, validar, limitar (D-004, D-005)
│   │   ├── associacao.py           # primeira associação e reconciliação (FR-049 a FR-057)
│   │   └── credenciais.py          # adicionar, remover, principal, corrigir nome e CPF
│   ├── migrations/
│   │   ├── 0001_identidade.py      # as três tabelas + restrições
│   │   └── 0002_reconciliacao.py   # migração de dados; interrompe quando precisa (D-007)
│   └── models.py
│
├── portal/                         # EXISTENTE — o canal; ganha as telas e perde a declaração
│   ├── identidade.py               # passa a montar o contrato a partir do registro (D-008)
│   ├── views.py                    # + acesso, área, credenciais; − identificação declarada
│   ├── urls.py
│   └── templates/portal/
│       ├── acesso_email.html       # informar endereço
│       ├── acesso_codigo.html      # informar código
│       ├── acesso_reconciliar.html # o convite, recusável
│       ├── inscricoes.html         # Minhas inscrições, com estado vazio
│       ├── credenciais.html        # acesso à conta
│       └── identificar.html        # REMOVIDO (D-011)
│
├── inscricoes/                     # EXISTENTE — mudanças mínimas e localizadas
│   ├── application/
│   │   ├── rascunho.py             # toma o bloqueio da identidade antes de criar (D-010)
│   │   └── consulta.py             # marca coincidência de CPF (D-013)
│   └── migrations/0003_cpf_na_submetida.py   # restrição da FR-063; depende de identidade.0002
│
└── config/settings/
    ├── base.py                     # mecanismo e remetente de e-mail, por ambiente
    └── production.py               # recusa o que se sabe não entregar (D-014)

backend/tests/
├── acceptance/portal/              # as seis fatias, no navegador do candidato
├── authorization/                  # os seis casos da demonstração de segurança
├── integration/identidade/         # desafio, associação, credenciais, concorrência
├── migrations/                     # a reconciliação: preserva, interrompe e relata
└── unit/identidade/                # forma canônica, código, limites
```

**Structure Decision**: um app novo, `identidade`, pela mesma linha que já separa `inscricoes` de
`portal` — o domínio de um lado, o canal do outro (D-001). O `portal` não ganha modelos; ele ganha
telas e passa a ler a identidade de um registro em vez de uma declaração. As alterações em
`inscricoes` são deliberadamente duas, ambas pequenas: o bloqueio na abertura de rascunho e a marca
de coincidência na consulta administrativa. Nada da jornada de inscrição é reimplementado.

**Seis correções à árvore acima, feitas depois da implementação**, pela mesma prática da `009`:
o plano registra o que se pensou, e a nota registra o que se construiu.

1. **`identidade/application/mensagem.py`**, não previsto. A composição do e-mail que leva o código
   saiu de `desafio.py` assim que a segunda finalidade apareceu: solicitar um desafio e redigir a
   mensagem que o anuncia são duas responsabilidades, e só a primeira é regra de domínio. A separação
   é o que permite testar o limite de envio sem inspecionar texto, e o texto sem tocar no limite.
2. **Duas migrações a mais**: `0003_retomar` acrescenta a finalidade `retomar` e o campo
   `reconciliacao_alvo`, ambos nascidos da retomada (`FR-055` a `FR-057`), que o plano tratava como
   caso da reconciliação e mostrou-se ato distinto; `0004_alvo_sobrevive` troca a cascata do alvo por
   `SET_NULL` (D-020). Migrações separadas, e não uma reescrita da `0001`: a `0002` já é migração de
   dados que pode interromper implantação, e reescrever uma migração publicada é o que a `FR-040`
   proíbe na prática.
3. **`credenciais.html` chama-se `conta.html`.** O nome da tela é o que o candidato lê no menu —
   "Minha conta" — e não o nome da tabela que ela mostra.
4. **`meus_dados.html`**, não previsto: o núcleo mínimo (nome e CPF) ganhou tela própria porque é
   pedido **antes** da primeira inscrição, e não dentro da conta. Documentada em
   [contracts/area.md](./contracts/area.md).
5. **`retomar_convite.html`**, não previsto: a retomada precisa de convite recusável próprio, pelo
   mesmo motivo do `acesso_reconciliar.html` — ninguém move credencial de alguém sem que a pessoa veja
   o que vai acontecer e possa dizer não.
6. **`inscricao_enviada.html` e `_documentos_submetidos.html`**, não previstos: o acompanhamento da
   `US5` mostra a inscrição enviada em leitura, com seus documentos, e a tela de rascunho não servia —
   ela oferece ações que uma inscrição enviada não aceita. Some-se `acompanhamento.html`, a lista de
   fatos e prazos da mesma fatia.

Nada disso muda a decisão de estrutura: o domínio continua em `identidade`, o canal em `portal`, e
`inscricoes` recebeu exatamente as duas alterações previstas.

**Mais três arquivos, vindos do percurso da jornada** (D-023 a D-027):
`inscricoes/application/mensagem.py`, que envia a confirmação do envio — no mesmo lugar e pela mesma
razão que `identidade/application/mensagem.py`: compor uma mensagem não é regra de domínio;
`portal/static/portal/reenvio.js`, a contagem regressiva do reenvio, que é enfeite sobre uma resposta
que o servidor já dá por escrito; e `tests/integration/portal/test_hora_do_envio.py`, que guarda a
conversão de fuso que faltava em `comprovante_pdf.instante`.

## Complexity Tracking

> Sem violações a justificar. Nenhuma dependência nova, nenhum serviço novo, nenhuma abstração
> genérica. As duas complexidades que se ofereceram — cache compartilhado para os limites e comando
> de reconciliação apartado — foram recusadas em D-005 e D-007, com o motivo registrado.

## Restrições técnicas desta feature

**A migração pode parar a implantação, e isso é o comportamento correto.** `FR-046`. Uma inscrição
enviada sem CPF utilizável impede instalar a restrição da `FR-063`, e seguir exigiria escolher um dado
por conta própria. A mensagem enumera o que precisa de tratamento. Pelo caminho normal da `009` essa
situação não existe — a identificação valida os dígitos antes de gravar —, mas base de demonstração e
carga manual existem.

**E são duas migrações, nesta ordem**: `identidade.0002_reconciliacao` verifica e cria; depois
`inscricoes.0003_cpf_na_submetida` instala a restrição, declarando dependência da primeira. Invertê-las
faria a implantação falhar no `ALTER TABLE`, com a mensagem do banco no lugar do relatório.

**A restrição afirma onze dígitos, não CPF válido.** D-017. O algoritmo dos dígitos verificadores não
cabe em restrição declarativa; a conferência permanece na captura e na verificação da implantação.
Prometer no texto o que o banco não entrega é pior que não prometer, porque ninguém confere.

**Nada de reescrever `identity_subject`.** `FR-042`. A migração copia; nunca atribui. Isso vale
inclusive para os conjuntos que ela não consegue reconciliar, que ficam intactos e sem novo dono.

**A restrição existente de idempotência permanece.** `FR-062`. A restrição nova de CPF em inscrição
enviada é acrescentada, não substitui nada.

**Dois caminhos tomam o mesmo bloqueio.** D-010. Se apenas a reconciliação bloquear, um rascunho nasce
no intervalo e fica órfão.

**A auditoria de credencial não aparece na consulta por escopo.** D-012. É consequência de o ato não
pertencer a Edital algum, está declarada, e a alternativa — inventar um escopo — faria o campo mentir.

**O desafio consumido continua vivo enquanto houver reconciliação pendente.** D-016. É ele que conta
as tentativas de CPF, porque a sessão não resiste a uma aba nova e a identidade alvo viraria alvo —
um terceiro esgotaria as tentativas e bloquearia o titular legítimo. A retomada da `FR-053` passa
pelo mesmo caminho: prova o endereço de novo, e a contagem vale igual.

**O código de acesso não vai para lugar nenhum além do e-mail.** Nem log, nem auditoria, nem mensagem
de erro, nem endereço de página.
