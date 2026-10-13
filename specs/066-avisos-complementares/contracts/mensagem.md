# Contrato — A mensagem (066)

*O que sai na caixa de entrada, e de onde vem cada parte. A composição é função pura de
`avisos/domain/mensagem.py`, testada sem banco.*

## Partes, nesta ordem

1. **Assunto**: o da seleção, com as variáveis resolvidas.
2. **Corpo**: o da seleção, com as variáveis resolvidas.
3. **Linha de retificação**, só quando `Aviso.retificadora` (`FR-1248`):
   > Este aviso se refere a publicação que retifica a de {data da publicação retificada}.
   Com várias publicações retificadas, as datas se juntam. **Nada diz que a situação de alguém
   mudou.**
4. **Rodapé fixo** (`FR-1257`), que não é editável e é visível no editor (`UX-176`).

As partes 1 a 4 são congeladas na confirmação. Só `{nome_do_candidato}` se resolve no envio
(`R-007`).

## Rodapé

```
—
A publicação oficial está em {destino_oficial} e é a referência para prazos e
resultados, conforme o {edital}. Este aviso não substitui a publicação.
Em caso de dúvida, fale com {atendimento}.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
```

Na chamada, entre a primeira frase e "Em caso de dúvida":

```
O prazo corre conforme o Edital, a partir da publicação, e não do recebimento deste aviso.
```

`{destino_oficial}` é escolhido pelo sistema, nesta ordem (`R-008`):

1. `{link_da_publicacao}`, quando o aviso cita uma publicação só;
2. `{referencia_da_publicacao}`, na chamada;
3. `{pagina_do_processo_seletivo}`, nos demais casos.

Ele não é variável oferecida à seleção.

`{atendimento}` é `settings.PORTAL_ATENDIMENTO`, obrigatório em produção, como na mensagem da
convocação. Não é variável oferecida à seleção.

## Variáveis (`FR-1255`)

| Variável | Resultado | Chamada | Valor |
|---|---|---|---|
| `{nome_do_candidato}` | ✓ | ✓ | `Inscricao.nome`; a única por pessoa |
| `{edital}` | ✓ | ✓ | "Edital nº 57/2026" |
| `{processo_seletivo}` | ✓ | ✓ | título do Processo |
| `{perfil}` | ✓ | ✓ | nome do Perfil no conteúdo da versão que o ato citou |
| `{etapa}` | ✓ | — | a Etapa do marco |
| `{natureza_do_resultado}` | ✓ | — | "preliminar" ou "definitivo" |
| `{data_da_publicacao}` | ✓ | ✓ | instante do ato no fuso da instalação: a publicação mais recente citada, ou o envio da comunicação por publicação |
| `{link_da_publicacao}` | só com **uma** publicação citada | — | o endereço permanente daquela publicação (`selecoes/resultados/<id>/`), que continua valendo depois da sucessão (`FR-1255a`) |
| `{pagina_do_processo_seletivo}` | ✓ | ✓ | a página pública do Edital (`selecoes/<edital_id>/`) |
| `{referencia_da_publicacao}` | — | ✓ | a referência que a comunicação da chamada declarou, como foi escrita |
| `{area_do_candidato}` | ✓ | ✓ | URL de `portal:inscricoes`, **sem token** (P-001 da `010`) |

- **A sintaxe** é `{nome}`, com nome em minúsculas e sublinhado. Chaves duplicadas, `{{ }}`, viram
  texto literal.
- **Validação** (`FR-1256`):
  - chave fora da tabela → `aviso_variavel_desconhecida`;
  - chave marcada "—" para a origem → `aviso_variavel_sem_valor`;
  - `{link_da_publicacao}` em aviso que cita mais de uma publicação → também
    `aviso_variavel_sem_valor`, com a sugestão de `{pagina_do_processo_seletivo}`.
- **Os modelos** são validados contra a união das duas colunas. O aviso é validado contra a coluna
  da origem dele.
- **Não há** modalidade, lista, posição, pontuação, resultado, motivo, CPF nem telefone, e nenhuma
  dessas chaves é aceita.

## Os três modelos iniciais (`D-008`, `FR-1260a`)

Assunto dos três: **`Processo Seletivo Ifes — Nova publicação disponível`**.

**Divulgação de resultado**

```
Olá, {nome_do_candidato}.

Foi publicado em {data_da_publicacao} o resultado {natureza_do_resultado} da etapa
{etapa}, do {perfil}, no {edital}.

Para consultar a sua situação, entre na área do candidato:
{area_do_candidato}

Se o Edital prevê recurso contra este resultado, o prazo e a forma estão na publicação.
```

**Publicação retificadora**

```
Olá, {nome_do_candidato}.

Foi publicada em {data_da_publicacao} uma publicação retificadora do resultado
{natureza_do_resultado} da etapa {etapa}, do {perfil}, no {edital}.

Consulte a publicação vigente e a sua situação na área do candidato:
{area_do_candidato}
```

**Nova chamada publicada**

```
Olá, {nome_do_candidato}.

Foi publicada em {data_da_publicacao} uma nova chamada do {perfil}, no {edital}, e a
sua inscrição está entre as convocadas.

O que fazer e até quando estão na publicação oficial. Acompanhe também pela área do
candidato: {area_do_candidato}
```

- O terceiro modelo usa só variáveis da chamada. Os dois primeiros usam `{etapa}` e
  `{natureza_do_resultado}`, e por isso só servem a aviso de resultado: escolhidos para uma chamada,
  a prévia os recusa com `aviso_variavel_sem_valor`.
- **O corpo não diz a situação**, e os três orientam a consulta na área autenticada (`D-007`).

## Forma da mensagem

- Texto simples, UTF-8 e um destinatário só (`To`), sem `Cc` nem `Bcc` (`FR-1271`).
- O remetente é `DEFAULT_FROM_EMAIL`.
- `Auto-Submitted: auto-generated` (RFC 3834), para que respostas automáticas de férias não voltem.
- **Nenhum cabeçalho ou parâmetro de rastreio**: sem pixel e sem link com identificador do
  destinatário.
