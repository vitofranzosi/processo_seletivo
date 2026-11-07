# Quickstart: verificar a inaplicabilidade documental

**Feature**: [spec.md](spec.md) · Para depois da implementação. Nada aqui roda antes dela.

## 1. Ambiente

Um banco próprio desta worktree, como o `CLAUDE.md` pede. O servidor sobe com o seletor de
identidade, no molde da entrada `formalizacao-117` do `.claude/launch.json`.

```bash
cd backend && make preparar DB_NAME=ps131demo
```

## 2. O Edital

1. Componha um Edital com documentos na convocação:
   - a certidão, obrigatória, sem condição;
   - o laudo médico, obrigatório, recorte *PcD em todos os Perfis*;
   - o *"Certificado de alistamento militar ou de reservista"*, obrigatório, com *"Exigido somente
     quando"* = *"no caso de candidatos do sexo masculino, maiores de 18 anos"*.
2. Tente marcar a condição num documento facultativo e publicar: a publicação é impedida.
3. Publique. No PDF, o item do alistamento sai com a condição depois da vírgula; a certidão e o laudo
   saem como antes.

## 3. A conferência

Convoque uma candidata PcD (Ana) e um candidato de ampla concorrência (Caio). Como membro **só
alocado** à conferência:

1. Ana, certidão: a opção *"Não se aplica"* não aparece. Pelo `curl` com o POST forjado, a recusa é
   `nao_se_aplica_sem_condicao`.
2. Ana, laudo: o mesmo.
3. Ana, alistamento, sem arquivo:
   - motivo `"."`: `motivo_sem_conteudo`;
   - motivo *"Candidata do sexo feminino, conforme o documento de identidade."*: aceito.
4. Caio, laudo (fora do recorte): o POST forjado de conferência devolve 404.
5. Caio envia um arquivo no alistamento. *"Não se aplica"* sem abrir: `nao_se_aplica_sem_abertura`.

## 4. O aceite

Como gestor:

1. Na condução, a linha da Ana separa conformes e *"não se aplica após análise"*.
2. *Registrar desfecho* → *Aceite*. O bloco mostra o alistamento, a condição, o motivo, o conferente e
   o instante.
3. Sem marcar a ciência: recusa.
4. Em outra aba, como o alocado, registre uma conferência nova no item. Volte e confirme com a ciência
   marcada: recusa por conjunto superado, com a lista nova.
5. Marque e confirme: aceito. Na trilha do desfecho, os identificadores das conferências, sem o
   motivo.

## 5. A formalização

Exporte a Ana. No manifesto, o alistamento sai como *"não se aplica após análise"*, com o instante
da conferência, e sem o motivo.

## 6. A transição

Num clone do banco de demonstração de 07/11 (`createdb -T gps_docs_demo ps131transicao`, sem tocar
na origem), abra a convocação do Gael, que tem *"não se aplica"* nos três obrigatórios
incondicionais:

- pela 11ª decisão, o aceite é recusado, nomeando os três como *"registrado sem condição publicada"*;
- as convocações decididas continuam decididas.
