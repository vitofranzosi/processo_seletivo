# Contrato — o documento publicado depois da 054

Complementa o contrato da `008` ([composicao.md](../../008-composicao-institucional/contracts/composicao.md)).
Diz o que o documento traz, na ordem; a tipografia é a da `008`.

## Ordem

1. Brasão e órgão (sem mudança).
2. Anúncio do ato: `EDITAL Nº <número>/<ano> — <título>` (sem mudança).
3. **Só no documento de Retificação** — a marca (`FR-995`):
   `Versão consolidada. Publicado em <data>; retificado em <data>[, em <data>…][, com vigência a partir de <data>].`
4. Descrição (sem mudança).
5. Preâmbulo — a Apresentação, quando tiver texto.
6. Seções numeradas, na ordem do catálogo com que o Edital foi publicado, só as que saem:
   - gerada: quando a coleção de origem não está vazia (sem mudança);
   - textual: quando tem texto, **ou** quando o sistema lhe acrescenta norma — a Inscrição com teto
     (`015`, FR-063) e a Matrícula com Requerimento (`FR-996`). O texto de quem elabora vem primeiro.
   - A tabela de Perfis, com mais de um Perfil, termina na linha `Total` (`FR-997`).
7. **Só no publicado** — o fecho (`FR-989`), alinhado à direita: `Vitória (ES), <data por extenso>.`
8. **Só no publicado** — a autoridade (`FR-993`): a rubrica *"Autoridade responsável pelo ato"*; o
   nome, se registrado; o cargo; o ato de nomeação, se registrado.
9. **Só no publicado** — a verificação de integridade (sem mudança).

Os itens 7 a 9 são um bloco inseparável na paginação.

## A frase da Matrícula (`FR-996`)

```text
O Requerimento de Matrícula será enviado {no ato da inscrição | quando o candidato for convocado}.
Ao enviá-lo, o candidato declarará:
    <texto integral da declaração, parágrafo a parágrafo, com recuo>
```

## Presença, por modo

| Elemento | Prévia | Publicado |
|---|---|---|
| marca de prévia | sim | não |
| marca de consolidação | não | só na Retificação |
| fecho (local e data) | **recusado** se oferecido | **obrigatório** |
| autoridade | recusada se oferecida | obrigatória |
| verificação de integridade | não | sim |

## A consulta pública (`signatory`)

`{"authorityId", "name", "role", "appointment"}` — `appointment` é novo, texto, vazio quando a
Publicação não o registrou; `name` pode vir vazio nas Publicações feitas pela interface com o catálogo
sem nome próprio.
