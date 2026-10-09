# Quickstart — Validar os avisos complementares (066)

*Roteiro de validação ponta a ponta, pela interface do ator (Princípio VI). Não contém
implementação. Referências: [contracts/telas.md](contracts/telas.md),
[contracts/despacho.md](contracts/despacho.md), [contracts/mensagem.md](contracts/mensagem.md),
[data-model.md](data-model.md).*

## 0. Pré-requisitos

- O ambiente sobe pelo `AGENTS.md`, com `make preparar` em banco próprio (`DB_NAME=…`). O
  `make preparar` agora imprime também `Modelos de aviso: C criados` na primeira passada, e `0
  criados` nas seguintes (`R-012`).
- `AVISOS_AOS_CANDIDATOS=true`, `INTERFACE_SELETOR_IDENTIDADE=true` e
  `PORTAL_IDENTIDADE_DEMO=true`.
- **Correio sem entrega real.** No compose, o coletor em <http://localhost:8025>. Na execução
  nativa, `DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, em que as
  mensagens saem no terminal **do comando de despacho**, e não no do `runserver`.
- Um Edital do `seed_demo` com resultado publicado em duas listas do mesmo marco e uma inscrição
  presente nas duas. Se o seed não produzir esse caso, ele é montado pelo helper dos testes, numa
  cópia do banco.

## 1. Resultado (US1)

1. Entrar como **publicador**, publicar o resultado preliminar do marco e chegar a "Publicações do
   marco".
2. "Avisar candidatos": conferir que a origem cita as duas listas, que a inscrição das duas conta
   uma vez, e as contagens "com endereço" e "sem endereço".
3. Escolher "Divulgação de resultado" e conferir na prévia:
   - o nome real;
   - o rodapé aponta a **página do processo seletivo**, porque o aviso cita duas publicações, e não
     há link de uma publicação só;
   - o rodapé;
   - nenhuma posição, lista ou modalidade.
4. "Enviar a N pessoas". A tela responde sem esperar e mostra os destinatários pendentes.
5. Rodar `manage.py despachar_avisos` uma vez. No coletor: uma mensagem por pessoa, um destinatário
   por mensagem, assunto "Processo Seletivo Ifes — Nova publicação disponível".
6. O histórico mostra "aceita pelo servidor de correio", e em lugar nenhum "entregue".
7. Abrir "Avisar candidatos" de novo: "nenhuma publicação nova a avisar", com o reenvio
   justificado como única saída.

## 2. Retificação (US2)

1. Retificar uma das listas (recurso provido e nova publicação).
2. "Avisar candidatos": só a sucessora aparece, e os destinatários são os dela. A prévia traz a
   linha "Este aviso se refere a publicação que retifica a de …".
3. Enviar, despachar, e abrir o primeiro aviso: texto e destinatários intactos. O primeiro e-mail
   aponta a página do processo seletivo, que já lista a publicação vigente.

4. **Link histórico**: o segundo aviso cita uma publicação só, e por isso o rodapé traz o link
   **dela**. Retificá-la de novo e seguir o link do segundo e-mail: abre a publicação sucedida, com o
   aviso de que foi retificada e o caminho para a vigente (`FR-1255a`).

## 3. Chamada por publicação (US3)

1. Num Perfil `PUBLICATION`, convocar três suplentes, comunicar com uma só referência e registrar a
   desistência de um deles.
2. No cartão da chamada, "Avisar os convocados desta publicação": o universo mostra três, e a
   mensagem sai para dois. O terceiro aparece como "não elegível para o aviso: desfecho
   registrado".
3. Entrar como **publicador sem base de comissão**: a ação não aparece, e a rota responde como
   inexistente.
4. Num Perfil `INDIVIDUAL_MESSAGE`, a ação não existe.

## 4. Modelos (US4)

1. "Modelos de aviso": os três iniciais estão lá, ativos.
2. Editar um. O aviso já enviado continua com o texto antigo.
3. Inativar os três e rodar `make preparar` de novo: continuam inativos, e nenhum é recriado.
4. Salvar um modelo com `{posicao}`: recusado, com a variável nomeada.
5. Entrar como presidência da comissão: usa os modelos no aviso, mas não chega à gestão de modelos.

## 5. Falha, queda, concorrência e interrupção (US5)

Pela suíte, porque precisam de servidor simulado:

O alvo `test-pg` do Makefile não repassa argumentos ao pytest, e por isso o recorte usa o mesmo par
de variáveis que ele usa:

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_RUNTIME_USER="$POSTGRES_USER" DB_NAME=ps_066 uv run pytest tests/integration/avisos -k "despacho or interrupcao"
```

Os cenários de aceitação 1 a 7 da US5 têm um caso cada. São eles:

- duas execuções simultâneas;
- servidor inalcançável;
- tentativa órfã;
- interrupção com pendentes;
- interrupção no meio de uma execução;
- o aviso de irrecuperáveis;
- o limite por minuto.

Pela interface, a interrupção:

1. Confirmar um aviso grande e despachar com `--limite 5`.
2. "Interromper" diz quantas já foram aceitas e que não voltam.
3. Confirmar e despachar de novo: nenhuma tentativa nova.

## 5a. A chave de habilitação (D-009)

1. Desligar `AVISOS_AOS_CANDIDATOS` e reiniciar: "Avisar candidatos" aparece sem ação, com a
   explicação. O histórico e os modelos abrem normalmente.
2. Com um aviso confirmado e pendente, desligar a chave e rodar o despacho: nenhuma tentativa.
3. Religar com o relógio adiantado além de `AVISOS_JANELA_DE_DESPACHO_HORAS`, pela suíte: os
   pendentes aparecem como "expirado sem envio", e nada sai.

## 6. Verificação

```bash
cd backend && make lint check test-pg DB_NAME=ps_066
```

O `provisionar_papeis` passa a informar **`40 de 40`** tabelas protegidas (`R-015`), e o `AGENTS.md`
acompanha o número. Os números da suíte no `AGENTS.md` sobem, e a lista de pulados não muda.
