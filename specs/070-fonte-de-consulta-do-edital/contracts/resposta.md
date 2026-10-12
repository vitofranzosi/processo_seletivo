# Contrato — a resposta da fonte de consulta

O que `duvidas.application.consultar.consultar(...)` devolve (`R-017`), pergunta a pergunta. É o
contrato que a tela da Fase A mostra e que as Fases B e C vão consumir. As estruturas estão em
[data-model.md](../data-model.md) §2.

---

## 1. O catálogo, com as fontes de cada pergunta

Para cada pergunta, a tabela distingue dois papéis:

- **trata do assunto**: a fonte responde ao que se perguntou. Se houver texto entre essas fontes, o
  tipo muda (`R-013`);
- **acompanha**: a fonte é mostrada inteira, mas não muda o tipo.

Todo texto livre de entidade usada sai literal e inteiro (`FR-1426`).

| Pergunta | Trata do assunto | Acompanha | Links |
|---|---|---|---|
| `P-01` Até quando posso me inscrever? | **Dado**: o Evento de período de inscrições (início e término); a situação no instante; o desfecho | **Texto**: a descrição e o local do Evento; a seção `inscricao` | Cronograma na página pública |
| `P-02` Quais são as próximas datas? | **Dado**: os Eventos em andamento e por vir no instante, com a fase de cada um | **Texto**: a descrição e o local de cada Evento | Cronograma na página pública |
| `P-03` Quantas vagas há neste Perfil? | **Dado**: as vagas imediatas; o quadro por lista, com a ampla concorrência pela linha sem modalidade; o cadastro de reserva; a reversão | **Texto**: a descrição, a localidade, a carga horária e a remuneração do Perfil; a descrição e o fundamento de cada modalidade; a seção `publico-alvo` (acrescentados na implementação, pelo guardião de cobertura) | Vagas do Perfil na página pública |
| `P-04` Quais são os requisitos deste Perfil? | **Texto**: os requisitos do Perfil; a seção `requisitos-gerais` | **Texto**: a seção `publico-alvo` | Vagas do Perfil na página pública |
| `P-05` Que documentos preciso enviar? | **Dado**: os documentos aplicáveis (`aplicabilidade`), com a obrigatoriedade; o vínculo a anexo | **Texto**: as instruções de cada documento; a seção `inscricao`; com modalidade escolhida, `verificacao-autodeclaracao` e `atendimento-pcd` | Edital e documentos na página pública; anexos |
| `P-06` Posso me inscrever em mais de um Perfil? | **Dado**: o teto de inscrições; **Texto**: a seção `inscricao` | — | — |
| `P-07` Como será a seleção? | **Dado**: as Etapas que o Perfil usa (caráter, peso, notas); os marcos do Perfil (forma da ordem, combinação, normalização, arredondamento, corte, desempate) | **Texto**: a seção `classificacao`; o nome da Etapa | Anexos citados |
| `P-08` Posso recorrer? Em que prazo? | **Dado**: a janela recursal de cada marco do Perfil; **Texto**: a seção `recursos`; os Eventos com a raiz `recurs` (`R-014`) | — | Cronograma na página pública |
| `P-09` Como funciona o sorteio? | **Dado**: o método do marco, ou o comum do Edital (algoritmo, fonte, ocorrência, quando, derivação), e a habilitação ao sorteio | **Texto**: os textos de normalização e de substituição; a seção `classificacao` | — |
| `P-10` Como serei convocado? | **Dado**: a forma de convocação do Perfil; o momento do Requerimento; **Texto**: as seções `convocacao` e `matricula` | **Texto**: a declaração do Requerimento | — |
| `P-11` Onde tiro dúvidas? | O canal (`R-011`) | — | — |
| `P-12` Onde estão o Edital e os anexos? | **Dado**: cada publicação (original e Retificações), com datas, vigência e o que contém; cada anexo com rótulo | — | Os documentos e os anexos |

### 1.1 A `P-12` e o documento de origem

A `P-12` lista **cada** documento pelo ato que o produziu, com a marca do que ele contém:

> "Retificação publicada em 11/10/2026: contém a publicação original e esta Retificação."

Nenhum é chamado de "Edital completo" nem de "documento vigente" (`D-004`). Quando o documento de
origem da versão vigente não contém todos os atos dela (`R-005`), a `P-12` diz isso, e o ponto para
revisão também.

---

## 2. Tipos por pergunta

| Pergunta | `RESPONDIDA` | `DEPENDE_DA_LEITURA` | `NAO_INFORMA` | `FONTES_DIVERGENTES` |
|---|---|---|---|---|
| `P-01` | Evento de período existe | — | — (a pergunta não é oferecida sem o Evento) | — |
| `P-02` | sempre — com todos os Eventos encerrados, "não há datas por vir neste cronograma" é dado, e não ausência | — | — | — |
| `P-03` | sempre | — | — | — |
| `P-04` | Requisitos do Perfil e nenhuma seção | Requisitos do Perfil **e** seção `requisitos-gerais` preenchida, ou só a seção | — (não oferecida) | — |
| `P-05` | Nenhum veredito `divergente` | Algum veredito `divergente` (`R-008`) | — (não oferecida) | — |
| `P-06` | Teto declarado e seção `inscricao` vazia | Seção `inscricao` preenchida, com ou sem teto | Nem teto nem seção | — |
| `P-07` | sempre | — | — | — |
| `P-08` | Só a janela declarada — inclusive a negativa declarada (`FR-1422`) | Duas ou mais fontes de naturezas diferentes, ou só texto | Nenhuma: nem janela, nem seção, nem Evento (`FR-1422`) | — |
| `P-09` | sempre | — | — | — |
| `P-10` | Forma de convocação e seções vazias | Forma e alguma das seções, ou só as seções | — | — |
| `P-11` | Um canal do Edital, ou o institucional | — | Nem Edital nem implantação | Mais de um canal distinto no Edital |
| `P-12` | sempre | — | — | — |

**Lista literal é dado** (`R-013`). Na `P-04`, os requisitos do Perfil são a coleção que a pergunta
pede: listados inteiros, dão `RESPONDIDA`. A seção `requisitos-gerais`, que é prosa sobre o assunto,
leva a `DEPENDE_DA_LEITURA`. O mesmo vale na `P-10` para as seções `convocacao` e `matricula`, diante
da forma de convocação declarada.

**`DETALHE_EM_ANEXO` como tipo não é produzido na Fase A.** Nenhuma pergunta do catálogo pede um
detalhe que só um anexo contenha. Ele existe na spec (`FR-1421`) para a pergunta livre da Fase B,
como a pontuação de um título (`CA-13` na forma original). Na Fase A, o anexo aparece como **aviso**
`DETALHE_EM_ANEXO`. É o caso da `P-07` do 92/2026, que é o `CA-13` como a `FR-1450` o mapeia.

---

## 3. Avisos

| Aviso | Quando | O que diz |
|---|---|---|
| `RETIFICACAO_FUTURA` | Há versão com `valid_from > instante` | A data de vigência. Por cartão afetado, o valor futuro e a Retificação de origem (`R-003`) |
| `DESFECHO` | Desfecho com `em <= instante` | "Este Edital foi cancelado em …" ou "encerrado em …". No desfecho do Edital, o período não está em curso |
| `DETALHE_EM_ANEXO` | Texto mostrado cita um anexo publicado, ou documento vinculado a anexo (`R-012`) | "O detalhe está no Anexo IV — …, que esta consulta não lê", com o link |
| `REDACAO_ALCANCA_MAIS` | Veredito `divergente` (`R-008`) | Que o documento publicado nomeia o grupo pelo nome e pode ser lido como exigido também aqui |

---

## 4. A explicação

Escrita por `duvidas/domain/explicacao.py`, em linguagem simples, com só valores dos cartões
(`FR-1425`). As formas iniciais, para a revisão com o setor:

| Pergunta | Forma (os valores entre `{}` vêm dos cartões) |
|---|---|
| `P-01` aberto | "As inscrições estão abertas até {término}. Situação em {instante}." |
| `P-01` futuro | "As inscrições começam em {início} e vão até {término}." |
| `P-01` encerrado | "O período de inscrições terminou em {término}." |
| `P-03` | "O Perfil {código} tem {total} vagas imediatas: {n} de ampla concorrência{, n na modalidade X…}. {Cadastro de reserva: …}" |
| `P-08`, dependente | "O Edital trata de recurso em mais de um lugar, mostrados abaixo. Esta consulta não os concilia; em caso de dúvida, procure {canal}." |
| `P-08`, não informa | "O Edital não traz informação sobre recurso contra este resultado. Isso não quer dizer que não caiba; procure {canal}." |
| `P-11`, divergente | "O Edital informa mais de um canal para dúvidas, mostrados abaixo." |

**Proibido na explicação:**

- avaliar a pessoa ("você pode", "você será aceito") (`FR-1425`);
- palavra que o cartão não tenha;
- frase do compositor do documento (`R-009`).

---

## 5. Pontos para revisão

| Tipo | Detecção | Texto |
|---|---|---|
| `CANAIS_DIVERGENTES` | `FR-1440` | "O Edital informa mais de um canal para dúvidas. Resolver antes de abrir o assistente de dúvidas neste Edital." |
| `EXCLUSIVIDADE_DO_CANAL` | `FR-1442` | "O Edital restringe as dúvidas a um canal ("exclusivamente"). Resolver antes de abrir o assistente de dúvidas neste Edital." |
| `ANEXO_CITADO_INEXISTENTE` | `R-012` | "O texto cita o Anexo {X}, que não está entre os anexos publicados." |
| `RETIFICACAO_FUTURA` | `R-003` | "Há Retificação publicada com vigência a partir de {data}." |
| `DOCUMENTO_DE_ORIGEM_INCOMPLETO` | `R-005` | "O documento que a página pública oferece como Edital completo não contém: {atos}." |

---

## 6. Forma serializada (`como_dict()`)

Determinística, com chaves em ordem fixa, para as Fases B e C. A Fase A não a expõe por rota
(`FR-1445`). Os testes a usam para comparar respostas.

```text
{
  "pergunta": "P-05",
  "parametros": {"perfil": "<código>", "modalidade": "<código> | null"},
  "instante": "<ISO 8601 com fuso>",
  "versao": {"id": "<uuid>", "identificador": "<12 hex>", "vigenteDesde": "...",
             "publicadaEm": "...", "retificacoes": [{"publicadaEm": "...", "vigenteDesde": "..."}]},
  "mudanca": null | {"anterior": "<uuid>", "atos": [{"publicacao": "<uuid>", "vigenteDesde": "..."}]},
  "tipo": "RESPONDIDA | NAO_INFORMA | DEPENDE_DA_LEITURA | FONTES_DIVERGENTES | DETALHE_EM_ANEXO",
  "avisos": [{"tipo": "...", "texto": "..."}],
  "explicacao": "<texto>",
  "referencias": [
    {"natureza": "TEXTO | DADO", "localizacao": "...", "caminho": "/profiles/id=…/requirements",
     "rotulo": "... | null", "conteudo": "...",
     "origens": [{"publicacao": "<uuid>", "ato": "ORIGINAL | RETIFICACAO",
                  "publicadoEm": "...", "vigenteDesde": "...", "documento": "<url>"}],
     "futuro": [{"valor": "...", "vigenteDesde": "...", "publicacao": "<uuid>"}],
     "links": [{"rotulo": "...", "url": "..."}]}
  ],
  "situacao": null | {"instante": "...", "periodo": "...", "desfecho": null | {...}}
}
```

**Nenhum campo é dado pessoal.** Nenhum campo vem de fora da versão consultada, salvo o canal
institucional e o desfecho.
