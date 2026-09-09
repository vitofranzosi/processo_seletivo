# Contrato normativo — `IFES-SORTEIO-SHA256-v1`

Este documento **é** o que o Edital publica quando declara o algoritmo. Ele existe para que uma
pessoa fora da instituição, com uma biblioteca de SHA-256 e nada mais, reproduza a ordem.

Trocar qualquer regra daqui é publicar outra versão do algoritmo — `…-v2` —, e é ato da classe da
Retificação. Nunca implantação de software.

## 1. Entradas

| Entrada | Origem | Forma |
|---|---|---|
| `relationHash` | resumo canônico da relação congelada | 64 hex minúsculos |
| `drawScopeId` | identidade do recorte: `<perfilId>` ou `<perfilId>:<listaId>` | texto |
| `seed` | semente normalizada, obtida da ocorrência declarada | texto |
| `publicNumber` | número público do participante na relação | inteiro ≥ 1 |

## 2. Serialização canônica

Os bytes que entram no resumo são produzidos pela mesma serialização canônica do restante do
sistema (`shared/canonical.py`), e a regra é reproduzível sem ele:

1. objeto JSON com **exatamente** estas cinco chaves;
2. chaves ordenadas alfabeticamente;
3. sem espaços — separadores `,` e `:`;
4. sem escapes não-ASCII (`ensure_ascii = false`);
5. texto normalizado em Unicode **NFC**;
6. codificação UTF-8.

```json
{"domain":"processo-seletivo/sorteio/v1","drawScopeId":"…","publicNumber":1,"relationHash":"…","seed":"…"}
```

## 3. A chave do participante

```text
key(p) = SHA256( canonical_bytes({
    "domain":       "processo-seletivo/sorteio/v1",
    "drawScopeId":  <drawScopeId>,
    "publicNumber": <publicNumber de p>,
    "relationHash": <relationHash>,
    "seed":         <seed>
}) )
```

O `domain` é literal e invariante nesta versão. O `relationHash` está na chave para que dois
sorteios distintos que recebam a mesma semente não produzam a mesma permutação relativa.

## 4. A ordem

1. ordene os participantes pela chave, **crescente**, comparando o resumo binário completo de 32
   bytes — comparar a representação hexadecimal minúscula dá o mesmo resultado, porque o
   comprimento é fixo;
2. havendo chaves idênticas, ordene esses participantes por `publicNumber` **crescente**;
3. a posição é a ordem resultante, de 1 a N, sem lacunas.

Todos os participantes da relação recebem posição. A ordem **não** é truncada pelo número de vagas.

## 5. Vetores normativos

Vivem em `backend/tests/contract/fixtures/sorteio/`, um arquivo JSON por vetor, e são exercitados
por duas implementações independentes — Python, no domínio, e JavaScript, em
`backend/tests/javascript/sorteio.test.js`.

Cada vetor traz:

```json
{
  "name": "…",
  "input": {"relationHash": "…", "drawScopeId": "…", "seed": "…", "participants": [1, 2, 3]},
  "canonicalBytes": {"1": "…", "2": "…", "3": "…"},
  "keys": {"1": "<64 hex>", "2": "<64 hex>", "3": "<64 hex>"},
  "expectedOrder": [2, 3, 1]
}
```

Vetores obrigatórios:

| Vetor | O que prova |
|---|---|
| `tres-participantes` | o caminho feliz, com bytes canônicos exibidos |
| `acentos-e-nfc` | normalização NFC muda a chave, e a regra está declarada |
| `colisao-de-chave` | o desempate por `publicNumber` existe e é executado |
| `um-participante` | ordem de um é legítima |
| `mesma-semente-recortes-distintos` | `relationHash` separa os dois |

## 6. O que o verificador de terceiro precisa, e nada além

- o manifesto publicado (§ `manifesto.md`);
- uma implementação de SHA-256;
- estas cinco regras.

Não precisa de acesso ao sistema, de credencial, do vídeo da transmissão nem de falar com o Ifes.
