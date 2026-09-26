# Percursos — a página pública do Edital, do anúncio ao registro

**Tudo pela interface.** A gestão prepara pelas telas dela, e o público lê pelo portal, sem
identificação. Shell e banco só preparam o ambiente. Não havendo caminho pela tela, registre a
lacuna e siga (protocolo da `034`).

## Ambiente

- Banco próprio da worktree (`DB_NAME`), `migrate`, e a preparação dos papéis **duas vezes**. A
  saída deve dizer `34 de 34`. Rode também o `seed_demo`: ele cria dois Editais, um com o prazo de
  inscrição aberto e outro com resultado divulgado e janela recursal de cinco dias.
- `INTERFACE_SELETOR_IDENTIDADE=true` para a gestão. O portal público não precisa de identidade.
- Abra por `http://localhost:<porta>`: `127.0.0.1` devolve `DisallowedHost`.
- Para os estados que dependem do relógio, use o seed com `--dias-atras` num banco próprio.

---

## 1 — O Edital cancelado diz que foi cancelado (`SC-282`, `FR-760`, `FR-761`)

1. Na gestão, cancele o Edital de inscrições abertas, com motivo.
2. Abra o endereço público dele, `/selecoes/<edital>/`.

**Esperado**
- a marca diz *cancelado*, com a data de hoje;
- nenhum *Aberta* e nenhum *Faltam N dias*;
- cronograma, documentos e histórico continuam na página;
- o motivo não aparece;
- a vitrine não lista o Edital.

## 2 — Encerrado, e Processo encerrado (`SC-282`, `FR-762`, `FR-763`)

1. Encerre o Edital de resultado divulgado.
2. Abra a vitrine e a página dele.
3. Com outro Edital publicado, encerre o **Processo** dele e abra a página do Edital.

**Esperado**
- o cartão fica em *Inscrições encerradas*, com a marca *encerrado* e a data;
- no Processo encerrado, a página diz o encerramento do Processo;
- nos dois casos, nenhum próximo Evento.

## 3 — O cronograma diz a mesma fase dos dois lados (`SC-283`, `FR-765`, `FR-766`)

1. Componha e publique um Edital com quatro Eventos:
   - o período de inscrições;
   - um Evento com término, em curso;
   - um Evento **sem término** com início uma hora atrás;
   - um Evento declarado cancelado, pela API do rascunho, único canal que o declara.
2. Abra, no mesmo minuto, a página pública, o acompanhamento de um inscrito e a página do Processo
   na gestão.

**Esperado**
- o Evento com término aparece *em andamento* nos três lugares;
- o Evento sem término aparece *concluído* nos três;
- o cancelado aparece *cancelado* no portal, sem fase, e não é próximo marco na gestão.

## 4 — Agora e próximo (`SC-287`, `FR-767`, `FR-768`)

1. Com um Edital de inscrições encerradas e dois Eventos futuros, abra a página.

**Esperado**
- o próximo Evento aparece no cabeçalho, com descrição e data, sem rolar até o cronograma;
- sem Evento futuro nem em curso, nada é dito, e nunca *"em análise"*.

## 5 — O prazo de recurso sem se identificar (`SC-284`, `FR-769` a `FR-771`)

1. Divulgue o preliminar de um marco com janela de cinco dias.
2. Abra a página pública do resultado e a página do Edital.
3. Como o inscrito, abra o acompanhamento.
4. Divulgue o definitivo do **mesmo** ato e abra a página dele.

**Esperado**
- o resultado mostra o período de interposição, com as duas datas, aberto;
- a lista de vigentes mostra *recurso até* a data de encerramento;
- a data é igual à do acompanhamento;
- o definitivo diz o **mesmo** prazo, e não um prazo novo;
- não há botão de recorrer;
- num marco sem janela, nada é dito sobre recurso.

## 6 — O preliminar continua alcançável (`SC-285`, `FR-772`, `FR-773`)

1. Com o preliminar sucedido pelo definitivo (percurso 5), abra a página do Edital.

**Esperado**
- o definitivo aparece como vigente;
- sob o mesmo marco e a mesma lista, em *Publicações anteriores*, está o preliminar, com natureza e
  data, e o endereço dele abre a página que diz *"sucedido"*;
- a página do definitivo lista o preliminar como anterior;
- em no máximo duas navegações, sem digitar endereço.

## 7 — Nada foi escrito (`SC-286`, `FR-774`, `FR-775`)

- O `migrate --check` não aponta migration nova.
- O `make preparar` continua `34 de 34`.
- `tests/integration/portal/test_leitura_sem_escrita.py` passa.
- Os Editais publicados antes da feature continuam abrindo.
