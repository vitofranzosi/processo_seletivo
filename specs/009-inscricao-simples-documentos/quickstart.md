# Fase 1 — Como demonstrar e validar

**Feature**: 009 — Inscrição Simples e Documentos do Candidato | **Data**: 2026-08-31

A condição de merge de cada entrega é o **percurso navegado**, não a contagem de testes (princípio
VI da Constituição, P-008 da spec). Este guia diz como preparar o ambiente, o que rodar, o que abrir
e o que se deve ver — em duas janelas, porque a feature tem dois atores e eles não compartilham
sessão.

---

## Pré-requisitos

Três particularidades do ambiente, todas conhecidas, nenhuma da feature.

**PostgreSQL local precisa de `LC_ALL`, e a role padrão da máquina não existe no cluster** —
sobrescreva `DB_USER`.

**`TEST_DB_ENGINE=postgresql` é obrigatório e é o que se esquece.** `config/settings/test.py` só olha
essa variável; sem ela a suíte usa sqlite em memória **sem avisar**. Nesta feature o custo é
específico: as constraints parciais e condicionais do modelo (uma marca de período por Cronograma,
protocolo único quando presente) não são exercidas, e o sinal é a contagem de skips.

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" uv run pytest -q
```

**A interface administrativa exige o seletor de identidade ligado**; sem a variável, `/gestao/`
devolve 503. A partir desta feature, o canal do candidato exige a sua própria — e as duas continuam
recusadas em produção.

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true PORTAL_IDENTIDADE_DEMO=true \
  ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos DB_USER="$(whoami)" \
  uv run python manage.py runserver 8009
```

A raiz de arquivos precisa existir e ficar **fora** de qualquer diretório servido como estático.
Em produção as três configurações são fiscalizadas antes de o processo subir.

---

## O cenário-base

Um Edital que exercita as quatro combinações de aplicabilidade com o menor número de dados possível.
A seed é o ponto de partida; o que falta é declarado pela interface, que é onde a demonstração vale.

```bash
cd backend && DB_USER="$(whoami)" uv run python manage.py seed_demo
```

Depois, pelo assistente, no Edital de demonstração:

| O que declarar | Onde | Valor |
|---|---|---|
| Período de inscrições | Etapa `Inscrição` | O Evento de inscrições do Cronograma, marcado |
| Documento de identificação | Etapa `Inscrição` | Obrigatório, sem Perfil, sem modalidade |
| Diploma de graduação | Etapa `Inscrição` | Obrigatório, Perfil `DOC-INFO` |
| Autodeclaração | Etapa `Inscrição` | Obrigatório, modalidade `PPP` |

Submeter, homologar e publicar com os dois atores institucionais, como as features anteriores já
demonstram. O documento publicado passa a ter a seção **Documentos exigidos para a inscrição**.

---

## Validação por entrega

### Entrega 1 — A oportunidade se encontra (US1, parte consultável)

Abrir o canal público **em janela anônima**, sem identificação.

- A seleção publicada aparece na vitrine, com identificação, título e unidade.
- O detalhe traz resumo, Perfis, vagas, localidade, requisitos e o documento oficial.
- Nada de `/gestao/`, nada de dado administrativo, nenhuma identificação pedida.
- Nesta entrega **ainda não** há situação temporal nem convite por vaga: eles dependem da entrega 2,
  e a spec diz isso na própria US1.

### Entrega 2 — O Edital governa a inscrição (US2, e a US1 se completa)

**Parte da 008 integrada** — as duas escrevem no compositor do documento.

- A etapa `Inscrição` do assistente aponta o Evento e declara os três documentos, com adicionar,
  editar, remover e ordenar.
- O documento publicado enuncia os três, com os adicionais de modalidade identificados.
- O conteúdo publicado declara `schemaVersion: 4`, `isRegistrationPeriod` no Evento marcado e a
  coleção `documentRequirements` com identidade estável.
- Uma Retificação alcança `/documentRequirements/id=<uuid>/required` e
  `/schedule/id=<uuid>/isRegistrationPeriod` sem alteração de gramática.
- A página pública passa a dizer **futura**, **aberta** (com data e hora de término) ou
  **encerrada**, e a oferecer `Inscrever-se nesta vaga` por Perfil.
- Publicar um Edital sem Evento marcado produz **aviso**, não recusa; e ele não recebe inscrições.
- **Recriar a seed**: os Editais publicados sob a versão 3 deixam de ser retificáveis, o que é o
  limite declarado na precondição 1 da spec.

### Entrega 3 — Identificar-se e continuar (US3)

- Acionar `Inscrever-se nesta vaga` sem identidade leva à identificação e **volta para a mesma
  vaga**.
- `Sua inscrição` traz nome, CPF e e-mail já preenchidos, e o CPF aparece mascarado como informação.
- Sair e voltar oferece `Continuar inscrição` e chega à mesma inscrição.
- Na outra janela, identificado como servidor no `/gestao/`, o portal continua sem reconhecê-lo como
  candidato — e vice-versa.
- Tentar iniciar a mesma inscrição duas vezes não cria duas.

### Entrega 4 — Enviar os documentos (US4)

- Escolhendo ampla concorrência, o sistema pede **dois** documentos; escolhendo `PPP`, **três**.
- Enviar um PDF grava na hora, sem `Salvar`, e a contagem avança para `1 de 2`.
- Enviar uma foto renomeada para `.pdf` é recusado com a mensagem que **ensina a converter**, e o
  arquivo já enviado continua lá.
- Durante o envio de um arquivo de vários megabytes há progresso visível e o aviso de não fechar a
  página. Simule com limitação de rede no navegador.
- Substituir um arquivo deixa claro qual passou a valer.
- Mudar a modalidade de `PPP` para ampla concorrência avisa qual arquivo será descartado **antes**
  de descartar.
- Copiar o endereço do arquivo e abri-lo em janela anônima não entrega nada.
- Em 375 px, a tela inteira funciona sem rolagem horizontal; o percurso todo é possível por teclado.

### Entrega 5 — Revisar, enviar, receber protocolo (US5)

- A revisão mostra oportunidade, dados e documentos, com `Editar` por bloco; voltar não perde nada.
- Faltando obrigatório, o envio é recusado nomeando o que falta.
- Aceitas as duas declarações, o envio produz protocolo `INS-<ano>-XXXXXXXX` e um comprovante
  imprimível pelo navegador.
- Acionar o envio duas vezes seguidas produz **uma** inscrição.
- Publicar uma Retificação com o rascunho aberto faz o envio seguinte avisar e pedir confirmação
  nova — e confirmar uma vez não faz o aviso voltar na tentativa seguinte.
- Encerrado o período pelo relógio, o rascunho aberto não pode mais ser enviado.
- Enviada, a inscrição não oferece nenhum caminho para alterar ou substituir arquivo.

### Entrega 6 — A equipe consulta o que chegou (US6)

Na janela institucional, no Edital:

- `Inscrições` mostra o total e a lista com protocolo, candidato, CPF mascarado, Perfil, modalidade,
  recebidos/esperados e data.
- O detalhe agrupa cada documento **sob o requisito que ele atende**, com o nome original.
- Cada documento abre no navegador; baixar existe como ação secundária individual.
- Não há deferimento, nota, parecer, classificação nem `Baixar todos`.
- Um ator sem permissão no Processo não alcança nem a lista nem o arquivo.

---

## O percurso emblemático (SC-017)

Fim a fim, em duas janelas, sem banco, sem shell, sem API manual:

> Gestor publica o Edital com Perfil, modalidade reservada, período e três documentos →
> candidato chega pela vaga, identifica-se, volta à mesma vaga, encontra seus dados, recebe
> exatamente os documentos que lhe cabem, envia os PDFs, revisa, envia e recebe protocolo →
> gestor abre `Inscrições`, encontra a pessoa e visualiza cada documento sob o seu requisito.

É este percurso, e não a suíte, que fecha a feature.

---

## O que a suíte precisa cobrir

| Nível | O que prova |
|---|---|
| `unit` | Aplicabilidade nas quatro combinações; aceitação de arquivo; alfabeto e forma do protocolo |
| `integration` | Rascunho retomável; substituição; unicidade; revalidação do envio; recriação da seed sob a versão 4 |
| `authorization` | Titularidade; ausência de permissão institucional para o candidato; recusa por endereço direto |
| `contract` | Forma publicada nova conferida contra o `openapi.yaml`; endereçamento das coleções novas |
| `acceptance` | O percurso acima, com dois atores |
