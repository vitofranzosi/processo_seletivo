# O "antes" — o estado contra o qual a 035 é conferida

**Tarefa `T002`, gravada em 18/09/2026, ANTES de qualquer edição de código.** Base: `main`
`9b72d75`. Banco próprio desta worktree, semeado por `manage.py seed_demo`.

**A parte (c) é a razão de este arquivo existir.** A `FR-519` e a `SC-179` prometem que nenhum
sorteio já realizado muda de resultado, e essa prova **não se faz depois**: ordem sorteada publicada
é ato, e um resultado que mudasse em silêncio seria a pior falha desta feature — e a única que
ninguém veria. Chegando ao fim da implementação, não existe mais "antes" que se possa exportar.

A `T027` exporta de novo e compara, linha por linha.

---

## (a) A contagem da suíte

```
cd backend && make lint check test-pg
```

| | |
|---|---|
| Coletados | **7225** |
| Passaram | **7213** |
| Pulados | **12** |
| Falharam | **0** |
| Tempo | 727,95 s (12 min 07 s) |

Contra **PostgreSQL**, com o par `TEST_DB_ENGINE=postgresql` e `POSTGRES_USER` — sem ele a suíte cai
para SQLite e falha por motivo que não é o diff.

## (b) O retrato do acervo

### Acervo — por publicação

| Edital | Ordem | Publicada em | Resumo do conteúdo canônico | Resumo gravado | Esquema canônico | Documento |
|---|---|---|---|---|---|---|
| 01/2026 | 1 | 2026-09-19 02:13:49 | `f4b05831cd614ae39a7f305fafac7cda190592b3ec06b53e128cedb553dddd60` | `b131b18a17d7a9819543a57b23fece9750efd00557233f8d579033b922538096` | 16 | `2b02a80746f1e99a0827282f6618789c15bf3fe34d0d6cb93dc78e10228db937` |
| 01/2026 | 2 | 2026-09-19 02:13:49 | `b695027a1a9ea692ac52ef219629da660a43ab532651b27572b360346334202d` | `dbb4ba7f6521b08930145695ff0a59009b12aef2df7b2210e447a1e9212a1187` | 16 | `11ce1f93858fd8429a79289ea952faec1893d9d0023abe6888b722b55ba05d21` |
| 01/2026 | 3 | 2026-09-19 02:13:49 | `fb4de516d65502fde44e2844400762abb9476d4b3502102c3854c46ac4ec9a55` | `4176acf28118b7030fb169752b9a819bd1d577c7747c16c25996b8a73b6d7e3f` | 16 | `7aadb39d7bcfcff729ca27da4dccb9c958cb6164b4057180e7f67ccf24d23bf1` |
| 26/2026 | 1 | 2026-09-19 02:13:49 | `af121c56bc1f9894d8dadde7eb95c520aa7bc4f657e539758b968ae4e8a859ab` | `1635e001e86ec7d04f47b0318ba18896477b3c41e9afabf5e961306d2d03a002` | 16 | `b65ca4eddef2e0c06f9fb15b1edfcf864c2a48b3ae1cb1929000888b4b92fb1c` |
| 26/2026 | 2 | 2026-09-19 02:13:49 | `f316ac1a4342f887640d0b1fd63e9865b9ae23b1c49ad8f5dc0e444f2d477dd7` | `01c786e42aa6268aa25f1fca7cb92001eb42a6594a3986d7a057897c5ae6cdfb` | 16 | `6fced64b8df12b65b456109f72b44b2ef5547fd95ccdba4f947d743bc6662f66` |
| 51/2026 | 1 | 2026-09-19 02:13:49 | `78687b69d9ba1a98946d8b0319813b1392e4b9e198964756267d1e7d96882a1e` | `6741ae7ba8f8c6dc8f829c52ae8916177087a1869041be10cd507843f783b4ea` | 16 | `b6b2027ad9807be3390d31ecac0b15912624a6760953fcf5a752c5053970cff4` |
| 51/2026 | 2 | 2026-09-19 02:13:49 | `6d11eb9873f46ee42ae0828c622646befbc9454f23a6de6d612a649c72d88ae3` | `2ebb4585e4b5cf28da01f5bd9c9b61f837ecd8a1f95fc7146ef6dd52e193094d` | 16 | `f0866af89ef174dca943b47adff11178a4095e96d3f6000e4b0aacba003c050b` |

### Acervo — por versão consolidada

| Edital | Materializada em | Resumo do conteúdo |
|---|---|---|
| 01/2026 | 2026-09-19 02:13:49 | `ac2984cfa93f7d55447ac7e8489529a311f94475232b3c385a8fa082f73e8d47` |
| 51/2026 | 2026-09-19 02:13:49 | `f2e1158384f518209bc3517dad5514378811979a9b68d21a176b06057e94de55` |
| 51/2026 | 2026-09-19 02:13:49 | `0a13e682ad115965f855e3db159206b820a5968a81fcc9b82bb28152e2566287` |
| 26/2026 | 2026-09-19 02:13:49 | `5b8339db564a7d0fa0199dae98ce2c5fc0e64ce9ab396eaa67bbefa089adcf7d` |
| 26/2026 | 2026-09-19 02:13:49 | `be5ac26d6b3e9ebc61500b0065180dd0df89f4967e69183af58b6c0f6fe7c4c4` |
| 01/2026 | 2026-09-19 02:13:49 | `f131a18b3439642787272b5859556b21d05bd0f270fbbd568c48b68d72c48aeb` |
| 01/2026 | 2026-09-19 02:13:49 | `fee9e0747ee2810db1f1be6b41742c18dfffbff6de7e0ba29c3517ab5d94d1c6` |

## (c) Os sorteios já realizados — semente, ordem e manifesto

**É a garantia mais dura desta feature.** A semente é onde método e ocorrência se encontram; a ordem
sorteada é o ato; o manifesto é contra o que um terceiro reimplementa. Os três são comparados na
`T027`, e qualquer diferença em qualquer um deles reprova a entrega.


- **Sorteio `2dfdea8e-45b3-40c0-886c-656b993cf08f`**
  - ocorrência: `Fonte de demonstração` — `5926`
  - semente normalizada: `12345 67890 11223 44556 77889`
  - resumo do método: `4a7cb1840f9f03fdab287debfadebac22c3773cfc27ebc6b889c465cb835b6ff`
  - resumo do manifesto: `019c2f84ba6b9d794fb94c4fc01c60883e8ca2ce0535ccdb4bbe61628b930139`
  - ordem sorteada (7 posições): `c90cb128c38ec460e9dda632bf9190799129ae70a28dccfa377ec03289bde4ba`
  - ordem, posição a posição: `[[1, "06bab528-834c-49e7-88d0-7df0c8e7f9b2"], [2, "6f5bf5e7-c7df-4a04-952e-f82ef747b65d"], [3, "c74a0478-c048-4142-b34d-85a08743d089"], [4, "04074f10-596a-4d03-b98b-14861bb51d12"], [5, "9abc740a-3ef3-4ddc-8d0c-0a49db153613"], [6, "86954d06-6ea2-4030-898f-ec96935c94f4"], [7, "5ba151ec-fe05-461c-94b0-759837528763"]]`
