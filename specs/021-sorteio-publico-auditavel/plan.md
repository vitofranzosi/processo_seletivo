# Implementation Plan: Sorteio público auditável

**Branch**: `claude/spec-021-sorteio-auditavel` | **Date**: 2026-09-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/021-sorteio-publico-auditavel/spec.md`

## Summary

O certame que seleciona por sorteio sai do sistema no meio: exporta inscritos, sorteia em software de
terceiro e volta com uma lista que ninguém reproduz. Esta feature traz o ato para dentro, com a
ordem de acontecimentos invertida em relação à prática atual — **o universo é comprometido antes de
a semente existir**.

A abordagem, em uma linha: a relação de habilitados publicada **é** o compromisso, e o
`AtoDeOrdenacao` constituído por sorteio é o resultado dele. Entre os dois, uma ocorrência futura de
fonte pública externa fixa a semente, e uma chave SHA-256 por participante — sobre a serialização
canônica que o repositório já tem — produz a ordem. O manifesto público e uma segunda implementação
em JavaScript, exercitada pelos mesmos vetores normativos na CI, transformam reprodutibilidade em
auditabilidade de terceiro.

O que a feature **não** faz continua sendo metade do desenho: ela não habilita, não elimina, não
ocupa vaga e não convoca.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 5.2 LTS, Django REST Framework, `hashlib` da biblioteca padrão para
SHA-256 — nenhuma dependência criptográfica nova

**Storage**: PostgreSQL 16+ (a CI valida contra 18). Append-only por trigger e por privilégio de
role, como o restante do acervo normativo

**Testing**: pytest (domínio, integração, contrato, interface, portal) e `node --test`, disparado
pelo próprio pytest em `tests/test_javascript.py`, para a implementação de referência em JavaScript

**Target Platform**: servidor Linux; interface administrativa e portal público servidos pelo mesmo
monólito

**Project Type**: monólito modular — módulo novo `sorteios`, mais alterações em `classificacao`,
`editais`, `publicacoes`, `interface` e `portal`

**Performance Goals**: um sorteio de 300 participantes vai do comando à ordem publicada em menos de
um minuto de operação (SC-004) — é o tempo de uma tomada de transmissão ao vivo. O cálculo de N
chaves SHA-256 é irrelevante nessa escala; o custo real é a chamada à fonte externa, que acontece
**antes** da transação

**Constraints**: nenhuma semente digitável em caminho algum; nenhuma prévia da ordem depois de a
semente ser conhecida; um ato raiz por tupla `(relação, ocorrência, método, recorte)`; manifesto sem
dado pessoal além do que a relação publicada já expõe

**Scale/Scope**: os Editais lidos vão de dezenas a poucos milhares de inscritos; o 28/2026 tem 21
recortes num só certame (7 polos × 3 listas)

## Constitution Check

*GATE: avaliado antes da Fase 0 e reavaliado depois da Fase 1.*

| Princípio | Como esta feature o atende | Situação |
|---|---|---|
| **I · Linguagem ubíqua** | Relação de Habilitados, Método do Sorteio, Ocorrência da Fonte e Sorteio são termos dos próprios Editais lidos, e nenhum duplica conceito existente. Identidades estáveis e públicas; `publicNumber` identifica sem autorizar | ✅ |
| **II · Integridade normativa e temporalidade** | Relação, método, ocorrência, sorteio e ato são append-only e sucedidos, nunca editados. O método declarado é conteúdo normativo, e trocá-lo é ato da classe da Retificação. Degrau canônico 10 com conversão sem invenção | ✅ |
| **III · Segurança, dados e auditoria** | Negar por padrão nos quatro comandos, por `comando_de_comissao`. Manifesto e relação publicam o mínimo — número público, e nunca CPF ou identificador interno (LGPD: necessidade, finalidade, minimização). Toda observação de ocorrência é auditada, **inclusive a que não vira sorteio** | ✅ |
| **IV · Regras explícitas e consistência** | Regras no domínio, transições explícitas, constituição transacional e idempotente, concorrência tratada por chave de idempotência e por constraint parcial | ✅ |
| **V · Qualidade e simplicidade** | Sem mensageria, sem event sourcing, sem serviço novo: um módulo, cinco entidades e duas colunas. Rastreabilidade FR → teste declarada em `data-model.md` | ✅ com ressalva registrada em Complexity Tracking |
| **VI · Completude de jornada** | Seis histórias, todas alcançáveis pelo canal do ator: gestão para quem conduz, portal anônimo para quem verifica, composição para quem elabora. Nenhuma capacidade demonstrável só por shell | ✅ |

**Reavaliação pós-Fase 1**: nenhum artefato de desenho introduziu violação. As duas tensões reais —
alteração de uma constraint existente e dependência de fonte externa — estão declaradas abaixo, com
mitigação.

## Project Structure

### Documentation (this feature)

```text
specs/021-sorteio-publico-auditavel/
├── plan.md              # este arquivo
├── research.md          # Fase 0 — treze decisões de desenho
├── data-model.md        # Fase 1 — entidades, constraints, transições
├── quickstart.md        # Fase 1 — o ciclo do 77/2026, pelos canais dos atores
├── contracts/
│   ├── algoritmo-sorteio.md   # o contrato normativo IFES-SORTEIO-SHA256-v1
│   ├── manifesto.md           # a forma do pacote público
│   └── interfaces.md          # as três superfícies
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 — do $speckit-tasks, não deste comando
```

### Source Code (repository root)

```text
backend/processo_seletivo/
├── sorteios/                        # MÓDULO NOVO
│   ├── domain/
│   │   ├── chave.py                 # a chave e a ordenação — função pura, sem Django
│   │   ├── projecao.py              # quem entra na relação, e a numeração
│   │   ├── manifesto.py             # derivação determinística do manifesto
│   │   └── normalizacao.py          # material bruto → semente
│   ├── application/
│   │   ├── relacao.py               # publicar (= congelar), suceder
│   │   ├── metodo.py                # declarar
│   │   ├── ocorrencia.py            # observar, com evidência de indisponibilidade
│   │   ├── sorteio.py               # constituir (atômico, idempotente), anular
│   │   └── verificacao.py           # recalcular das entradas
│   ├── infrastructure/
│   │   └── fontes/                  # a porta e os adaptadores da fonte externa
│   ├── api/                         # rotas públicas: relação, manifesto, verificação
│   ├── migrations/
│   └── models.py
├── classificacao/                   # + origem, + lista_id, constraints parciais
├── editais/                         # + EventoCronograma.location
├── publicacoes/                     # + degrau 10 em domain/elevacao.py
├── interface/                       # telas de gestão, inclusive a tela transmitida
└── portal/                          # relação, resultado e "Verificar este sorteio"

backend/tests/
├── unit/sorteios/                   # chave, ordenação, colisão, projeção, normalização
├── contract/
│   ├── test_vetores_de_sorteio.py   # os vetores normativos, em Python
│   └── fixtures/sorteio/            # os vetores
├── integration/sorteios/            # relação, congelamento, constituição, anulação, concorrência
├── interface/                       # as telas de gestão
├── portal/                          # a verificação pública
└── javascript/sorteio.test.js       # a segunda implementação, pelos mesmos vetores
```

**Structure Decision**: módulo novo `sorteios`, no padrão domínio/aplicação/API/persistência dos
demais, porque o vocabulário e o ciclo de vida são próprios e existem **antes** da ordem (R-002).
`classificacao` recebe apenas a dimensão da lista e a proveniência de origem; `divulgacao` não muda.
A direção de dependência é `sorteios → classificacao`, nunca o contrário.

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples, e por que foi recusada |
|---|---|---|
| **Alterar uma constraint existente** (`uq_ato_raiz_por_marco`) | A D-006 exige três atos raiz para o mesmo Perfil e marco, e a constraint de hoje os proíbe | *Um marco por lista* não mexeria em constraint nenhuma — e triplicaria a janela recursal, que é do marco e que os Editais declaram uma vez. A mitigação é dividir em **duas** constraints parciais, mantendo a de hoje palavra por palavra para o ato sem lista (R-001) |
| **Dependência de fonte externa em tempo de execução** | É a feature inteira: a garantia é a semente **não ser nossa**. Uma fonte interna seria reproduzível e escolhível | *Semente do sistema* e *compromisso publicado pela comissão* estão recusados na D-003, com o argumento de que quem conhece o universo mói sementes. Mitigação: porta com adaptadores, material bruto registrado, regra de substituição publicada e toda observação auditada — inclusive a descartada (R-005, R-006) |
| **Segunda implementação do algoritmo, em outra linguagem** | A SC-002 exige duas implementações independentes reproduzindo os vetores; sem isso "reimplementável" é promessa | *Confiar na implementação única* deixaria o contrato sem prova executável. O repositório já dispara `node --test` dentro do pytest — o custo é um arquivo, não uma esteira nova (R-008) |
