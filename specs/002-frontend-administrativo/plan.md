# Implementation Plan: Interface Administrativa de Processos Seletivos e Editais

**Branch**: `002-frontend-administrativo` | **Date**: 2026-08-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-frontend-administrativo/spec.md`

**Status**: Draft — Constitution Check aprovado; um ponto de confirmação externa registrado.

## Summary

Construir a interface administrativa como páginas renderizadas pelo servidor dentro do projeto
Django existente, usando o design system do SUAP para os componentes e HTMX para as interações que
exigem atualização parcial — a composição de Perfis e do Cronograma, que são listas dinâmicas.

As views da interface invocam os **commands da camada de aplicação** já existentes, não a API HTTP.
Os commands são a fronteira do domínio: eles verificam autorização, gravam auditoria e controlam
transação. Chamar a si mesmo por HTTP acrescentaria uma volta de rede e uma segunda serialização sem
acrescentar garantia alguma.

A autenticação institucional **não** integra este incremento. A interface consome identidade e
permissões como dado vindo do backend, mantendo a fronteira explícita para que a integração com o
diretório seja trocada sem tocar nas telas.

## Technical Context

**Language/Version**: Python 3.13 — o mesmo do backend, mesmo projeto

**Primary Dependencies**: Django 5.2 LTS com o motor de templates habilitado; design system do SUAP
(filtros e tags de template, CSS, Open Sans, Font Awesome); HTMX para atualização parcial; nenhuma
dependência de build JavaScript

**Storage**: nenhuma nova. A interface não persiste conteúdo normativo. O rascunho local em
preenchimento vive no navegador e é descartado ao ser enviado ao domínio

**Testing**: pytest e pytest-django, com o cliente de teste do Django exercitando as views; testes de
acessibilidade automatizados sobre o HTML renderizado; inspeção manual para o que a automação não
cobre

**Target Platform**: navegador atual em computador institucional; servido pelo mesmo processo Django
do backend

**Project Type**: aplicação web renderizada no servidor, dentro do monólito modular existente

**Performance Goals**: primeira renderização útil em até 2 s em rede institucional; atualização
parcial de lista em até 500 ms; nenhuma tela deve exigir mais de uma requisição por interação

**Constraints**: eMAG 3.1 e WCAG 2.1 nível AA simultaneamente; todos os fluxos concluíveis por
teclado; nenhuma regra de domínio reimplementada na interface; nenhuma decisão de autorização
tomada na interface

**Scale/Scope**: dezenas de servidores do Cefor em uso simultâneo; aproximadamente 12 telas; um
Edital com até algumas dezenas de Perfis e Eventos

## Constitution Check

*GATE: aprovado antes da pesquisa; a reavaliar após o desenho detalhado.*

| Princípio constitucional | Evidência no plano | Resultado |
|---|---|---|
| Linguagem e integridade do domínio | As telas usam os termos canônicos — Processo Seletivo, Edital, Perfil de Vaga, Retificação — e a estrutura da tela não redefine o domínio | PASS |
| Fonte única normativa | A interface não guarda conteúdo normativo; tudo vem do backend e volta por command | PASS |
| Imutabilidade e temporalidade | Edital publicado é apresentado como imutável, com Retificação como único caminho de correção; vigência futura é exibida explicitamente | PASS |
| Segurança e menor privilégio | A interface oculta o que a pessoa não pode fazer, mas a decisão continua no backend; ocultar não é autorizar | PASS |
| Segregação de funções | A interface comunica a exigência antes da tentativa; quem impede continua sendo o domínio | PASS |
| Auditoria | Nenhum ato ocorre fora dos commands, que já auditam; a interface só oferece consulta autorizada | PASS |
| Regras críticas no backend | Validação em tela previne erro e não é fronteira; toda recusa vem do domínio | PASS |
| Transações e concorrência | ETag e If-Match continuam sendo do backend; a interface apresenta o conflito em linguagem compreensível | PASS |
| Contratos explícitos | Ver [Decisão 2](#decisão-2--as-views-chamam-commands-e-não-a-própria-api) | PASS com justificativa |
| Migrations versionadas | Nenhuma migration nova; a interface não tem esquema próprio | PASS |
| Qualidade e rastreabilidade | Os 28 FRs e 9 SCs desta feature rastreiam para testes, incluindo os quatro herdados da 001 | PASS |
| Simplicidade | Sem projeto separado, sem toolchain de build, sem framework de UI; a solução mais simples que atende os requisitos | PASS |
| Interfaces acessíveis e claras | eMAG 3.1 e WCAG 2.1 AA, teclado, confirmação antes de ato irreversível | PASS |

## Decisões técnicas

### Decisão 1 — Páginas no servidor, com HTMX para o que é dinâmico

O que torna esta interface difícil não é interatividade rica: é **clareza sobre atos com efeito
jurídico**. HTML renderizado no servidor entrega acessibilidade por construção — foco, ordem de
leitura, navegação por teclado e funcionamento com leitor de tela são comportamento nativo do
navegador, não algo a reconstruir.

HTMX entra apenas onde a alternativa seria recarregar a página inteira: acrescentar e remover Perfis
e Eventos, e reordenar o Cronograma. São listas que crescem durante a elaboração, e recarregar a
página a cada item tornaria SC-001 — montar um Edital em 15 minutos — improvável.

**Alternativa descartada**: SPA em React ou Vue consumindo a API. Honraria melhor o desenho
contract-first da 001 e permitiria evoluir front e back separadamente, mas custaria toolchain de
build, e acessibilidade AA em SPA exige reconstruir manualmente foco, anúncio de mudança de rota e
estado de carregamento. Nenhum requisito desta feature pede a independência que justificaria esse
custo.

**Alternativa descartada**: templates sem HTMX. Mais simples ainda, mas a composição de Perfis e
Cronograma ficaria desconfortável a ponto de ameaçar SC-001 e SC-002.

### Decisão 2 — As views chamam commands, e não a própria API

As views invocam `processos.application.commands`, `editais.application.draft`,
`publicacoes.application.publish_edital` e `publicacoes.application.retificacoes` diretamente.

A Constituição exige contratos explícitos e proíbe que entidades de persistência sejam contrato
público. **Ambas as exigências continuam atendidas**: os commands já são o contrato interno, com
entradas explícitas e erros de domínio tipados, e a API HTTP permanece intacta como contrato externo,
verificada pelos testes de conformidade da 001.

O que se evita é a interface chamar o próprio processo por HTTP: acrescentaria latência, uma segunda
serialização e um ponto de falha, sem acrescentar garantia — a autorização, a auditoria e a transação
vivem nos commands, não na camada HTTP.

**Consequência aceita**: interface e backend passam a ser implantados juntos. É adequado para um
monólito modular com uma equipe pequena, e é o que a 001 já escolheu para si.

### Decisão 3 — Design system do SUAP

O [design system do SUAP](https://suap.ifrn.edu.br/comum/design_system/) é a identidade visual
corrente da rede dos Institutos Federais, e é **feito para templates Django** — distribui filtros e
tags, não componentes JavaScript. Traz tema gov.br, tema de alto contraste e modo daltonismo, o que
adianta parte de FR-024.

Componentes que mapeiam direto nos requisitos:

| Componente | Onde serve |
|---|---|
| Steps | O caminho elaborar → submeter → homologar → publicar (US3) |
| Timeline | Histórico de Retificações e trilha de auditoria (US4, US6) |
| Alerts e status badges | Achados de validação por severidade e situação do Edital (FR-009) |
| Tables e cards | Lista de Processos e Editais (FR-003) |
| Form elements | Composição de Perfis e Cronograma (FR-005, FR-007) |

**⚠️ Ponto a confirmar antes da implementação**: como o design system é obtido e licenciado para uso
fora do SUAP — se há pacote distribuível, se o CSS pode ser incorporado ao projeto, e se o Ifes tem
alguma customização própria. A escolha não muda a arquitetura, mas muda o que precisa ser escrito.
Confirmar com quem administra o SUAP no Ifes.

### Decisão 4 — A autenticação é uma fronteira, não uma implementação

A interface obtém identidade, escopo e permissões de uma única origem, e nada além dela sabe como
esse dado é produzido. Neste incremento, essa origem lê o adaptador de desenvolvimento que já existe
no backend. Quando o LDAP for integrado, apenas essa origem muda.

Para permitir exercitar os fluxos com identidades diferentes durante o desenvolvimento e a validação
com usuários, existirá um seletor de identidade — **habilitado exclusivamente fora de produção**, por
configuração, e ausente do HTML quando desabilitado.

**⚠️ Este incremento não é implantável em produção.** Não é limitação a resolver no plano: é a
decisão registrada na especificação. A entrega serve para demonstração, validação com servidores do
Cefor e medição de SC-001, SC-002 e SC-003.

### Decisão 5 — O que fica no navegador

FR-020 exige que o conteúdo em preenchimento sobreviva à expiração de sessão e à queda de conexão. O
rascunho local vive no armazenamento do navegador, associado ao Edital e à pessoa, e é **descartado
assim que o domínio aceita o envio**.

Ele não é fonte normativa e não substitui o rascunho estruturado do Edital, que continua no backend.
A distinção precisa aparecer na tela: a pessoa deve saber o que já foi enviado e o que ainda existe
apenas no navegador dela.

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-administrativo/
├── spec.md
├── plan.md
├── research.md              # a criar: design system, HTMX, ferramenta de acessibilidade
├── data-model.md            # a criar: modelos de apresentação, não de persistência
├── quickstart.md            # a criar: como validar a interface
├── checklists/
│   └── requirements.md
└── tasks.md                 # criado somente por $speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── config/
│   └── settings/            # habilitar TEMPLATES, staticfiles e o design system
├── processo_seletivo/
│   ├── interface/           # app novo: a interface administrativa
│   │   ├── views/           # uma view por fluxo, invocando commands
│   │   ├── forms/           # tradução de entrada da pessoa para o payload do command
│   │   ├── templates/       # páginas e fragmentos HTMX
│   │   ├── templatetags/    # apresentação de situação, severidade e instante
│   │   └── identidade.py    # a fronteira de autenticação da Decisão 4
│   └── ...                  # apps de domínio, inalterados
├── static/                  # design system e CSS próprio
└── tests/
    ├── interface/           # views, formulários e fluxos
    └── acessibilidade/      # conformidade eMAG e WCAG sobre o HTML renderizado
```

Nenhum app de domínio é alterado por esta feature. Se algo no backend precisar mudar — um dado que a
interface precisa e o command não devolve —, isso é evolução da 001 e deve ser tratado como tal, não
contrabandeado como código de interface.

## Fases

**Fase 0 — Pesquisa.** Obter e avaliar o design system do SUAP; escolher a ferramenta de verificação
automatizada de acessibilidade; confirmar como HTMX convive com o CSP e com os componentes do design
system. Resultado em `research.md`.

**Fase 1 — Desenho.** Mapear as telas e os fragmentos, definir os modelos de apresentação e como cada
erro de domínio vira mensagem compreensível. Resultado em `data-model.md` e `quickstart.md`.

**Fase 2 — Tarefas.** Criadas por `$speckit-tasks`, por história, na ordem de prioridade da
especificação.

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| Design system indisponível fora do SUAP | Retrabalho de estilo e perda da identidade da rede | Confirmar antes da Fase 1; o HTML semântico não muda, só a folha de estilo |
| Acessibilidade tratada no fim | eMAG e WCAG viram retrabalho caro | Verificação automatizada desde a primeira tela, no mesmo pipeline dos testes |
| Comandos não devolvem o que a tela precisa | Tentação de consultar modelos direto, furando a fronteira | Tratar como evolução da 001, com teste próprio |
| Interface "quase pronta" ir para produção sem autenticação | Exposição de todos os atos normativos do Cefor | Seletor de identidade ausente do HTML fora de desenvolvimento; registrar o bloqueio no README e no relatório de validação |

## Complexity Tracking

> Preenchido apenas quando o Constitution Check registra violação a justificar.

| Violação | Por que é necessária | Alternativa mais simples rejeitada porque |
|---|---|---|
| Views invocam commands em vez da API HTTP | A interface vive no mesmo processo; os commands já são a fronteira de domínio com autorização, auditoria e transação | Chamar a própria API por HTTP acrescentaria latência, segunda serialização e ponto de falha, sem acrescentar garantia. O contrato HTTP externo permanece intacto e verificado |
