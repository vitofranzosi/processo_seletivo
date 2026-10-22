# Integridade — medições físicas

Investigação FASE-5B.2-A-I1-BASE-01; executor Codex; 20/10/2026, America/Sao_Paulo (UTC−03:00).
Repositório: D:\projetos\cefor\processo_seletivo. Branch: 001-decisoes-pendentes. HEAD observado: 4ec10ba52636ef54b56dee35970333f5742548df.

I1 bloqueado; I2–I6 não autorizados; G1–G6 bloqueados individualmente. Nenhuma nova baseline aprovada.

Método: Get-FileHash -LiteralPath, SHA256, sobre os bytes atuais. Nenhuma conversão de encoding, final de linha ou hash de representação transformada. Hashes abaixo são medições locais; referências históricas não ganham confiança independente por coincidirem.

## Manifestos

| Referência | SHA-256 físico atual |
|---|---|
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/manifesto-a4.json | fb0f7aed253644c4217e22162d2b328d8929e78b96b92abe16739d9c7014010d |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/manifesto-a5.json | 7632e49c687a27dabdc96131b46e7e2623d118bf18c2629d3af5b63a2b904f5d |

A.4: hash publicado na matriz-integridade.md da A.5 coincide com fb0f7aed253644c4217e22162d2b328d8929e78b96b92abe16739d9c7014010d. A.5: sem hash externo confiável disponível nesta investigação; o valor acima é referência de coleta, sem assinatura ou aprovação de baseline.

Comparados 111 registros anteriores e cinco novos Markdown na A.4; 117 anteriores e seis novos Markdown na A.5: 239 verificações, todas coincidentes com os hashes declarados nesses manifestos. Contagens se sobrepõem e não são 239 arquivos únicos. Somados os manifestos, o universo documental protegido é de 124 caminhos (117 anteriores à A.5 mais sete da entrega A.5).

## Onze divergências históricas

| ID | Caminho | Origem histórica declarada A.5 | SHA-256 histórico | SHA-256 físico agora = físico A.5 | CRLF histórico A.5 |
|---|---|---|---|---|---|
| D01 | doc/saneamento-2026-10-16/fase-5b.1/isolamento/tarefas.py | fase-5b.1/integridade.json; fechamento-a2/evidencia-a2.json:hashes_depois_5b1 | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 | f6c2e3e7aa17d8f8c717c5f0632aa67806d74c85e3677af7833f9f6fb198f2a1 | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 |
| D02 | doc/saneamento-2026-10-16/fase-5b.1/operar.py | fase-5b.1/integridade.json; fechamento-a2/evidencia-a2.json:hashes_depois_5b1 | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 | eab9d9b5d53946e84822ce0d3924633bbff03bc74f9108b1c288d8d210c46c9a | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 |
| D03 | doc/saneamento-2026-10-16/fase-5b.1/integridade.json | fechamento-a2/evidencia-a2.json:hashes_depois_5b1 | cfedd1455cd34e91679115e9c7e30d2f05a53afd63efe961271fda03c3eb7982 | c82d449005a8161d3ef8b40d84f09a3055c749d8e152ac504bfadb79d22d5405 | cfedd1455cd34e91679115e9c7e30d2f05a53afd63efe961271fda03c3eb7982 |
| D04 | doc/saneamento-2026-10-16/fase-5b.1/revisao-estatica.json | fechamento-a2/evidencia-a2.json:hashes_depois_5b1 | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 |
| D05 | doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/hashes-antes.json | fechamento-a2/evidencia-a2.json:hashes_documentos_e_propostas | 312c03b7650ad6c7c927df46cd58043fb39839fd7902a515c05d490ec3d2a5e0 | 599368acde19f352805f769ef66092fee133ea48d0d00bf10b04e262a210cdf9 | 312c03b7650ad6c7c927df46cd58043fb39839fd7902a515c05d490ec3d2a5e0 |
| D06 | doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/inventario-imagens.md | fechamento-a2/evidencia-a2.json:hashes_documentos_e_propostas | 9dd46415bc558c43a81b3984e111172c61c9cacc581fce180310cbb0378961c3 | ccfdb95f38f9879527e815e1a3bca5c6301e488f2fd50ce580114fd13a6682a4 | 9dd46415bc558c43a81b3984e111172c61c9cacc581fce180310cbb0378961c3 |
| D07 | doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/metadados-publicos.json | fechamento-a2/evidencia-a2.json:hashes_documentos_e_propostas | 498b27bc248d1aefc2d3a38018299fd0682fcb7ceed2f366276c99f1e3ef8719 | ce8cc77c6e8c3d448f939e10c91ef13b30d2e45f8aeb48b06e1ee73770c0d6af | 498b27bc248d1aefc2d3a38018299fd0682fcb7ceed2f366276c99f1e3ef8719 |
| D08 | doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/integridade.json | fechamento-a2/evidencia-a2.json:hashes_documentos_e_propostas | 4ec8e0aaba84aec85a260c8f168e3c1a9232cf5dff7e1287497c8b41b89830b3 | b348326c5233b7a4d871354bf13bb70e997756203d47c085f0d9224f0185383a | 4ec8e0aaba84aec85a260c8f168e3c1a9232cf5dff7e1287497c8b41b89830b3 |
| D09 | doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/operar.py | fechamento-a2/evidencia-a2.json:hashes_documentos_e_propostas | 006dcdf52014c0a01acd0543a247932d6e906b51ef203a7fff584929d79c21bf | 1c64fe4bc078ee7cfa9f971d266f785df66d27a83bb996cc4bb3576f71aaa790 | 006dcdf52014c0a01acd0543a247932d6e906b51ef203a7fff584929d79c21bf |
| D10 | doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/integridade.json | correcao-a1/estado-anterior.json | da4a15af9ef69c74c8446d5b46bff72d6a1d345d378283c5a8cb51f8ba2d7a10 | 6aa4f89caf5d0e102b75daeb3628c41ce283624c1cc7b423cb7fc64f04567206 | da4a15af9ef69c74c8446d5b46bff72d6a1d345d378283c5a8cb51f8ba2d7a10 |
| D11 | doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/revisao-estatica.json | correcao-a1/estado-anterior.json | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 |

Todos os onze hashes físicos coincidem com a coluna física da matriz A.5 e diferem dos hashes históricos ali referidos. Os caminhos foram deduplicados; repetições em manifestos não são novos arquivos. Não houve simulação CRLF nesta autorização: a coluna final reproduz somente evidência histórica da A.5, cujo algoritmo declarado é normalizar CRLF para LF e depois LF para CRLF em memória.

A regra atual .gitattributes declara text=auto eol=lf, compatível com a hipótese de normalização. Isso não prova mecanismo concreto, autoria nem momento da transformação. Identidade lógica de conteúdo e equivalência CRLF permanecem conclusões da investigação histórica, não novas provas obtidas por transformação nesta sessão. Bytes atuais, correspondência histórica, identidade lógica, proveniência e autorização operacional são conceitos separados.

## Inventário físico protegido para conferência final

Inclui os 124 documentos e seis caminhos de código diferentes entre commits. Caminhos e hashes dos 15 não rastreados também estão no inventário próprio. Releitura final será comparada a este conjunto de 130 arquivos; resultado de fechamento na resposta, sem reescrever documentos após selagem.

| Caminho | SHA-256 físico de coleta |
|---|---|
| doc/saneamento-2026-10-16/adendo-auditoria.md | 7d56853c8407eb509c37030f620c17fcc1239719add7466e02dffa7972690a3f |
| doc/saneamento-2026-10-16/diagnostico-git.md | 5f0b14aa1532564e45297e67ec972b8d5de22a3deaaf01ab9b4d0164df161030 |
| doc/saneamento-2026-10-16/fase-2-consolidacao-dec-15.md | 1350465b289a8ba993e3194d057548d02331cb11299cda2d4e7c3dfea874f11d |
| doc/saneamento-2026-10-16/fase-2-deliberacao-dec-15.md | 27c131de67d402d78eb79191af4d88c6920513215e39e0db6e4382ced6c024a6 |
| doc/saneamento-2026-10-16/fase-2-rodadas-1-e-2.md | 233b03774f0aacf9d4fbc931c7f07482ae828f4cc129a7edf95d86b3173ab05c |
| doc/saneamento-2026-10-16/fase-2-rodadas-2-e-3.md | 29512d83fc7afe42cff906622b89da2343b6182cba5aa74e008393c96a02bb34 |
| doc/saneamento-2026-10-16/fase-2-rodadas-3-e-4.md | beac1de8d2d1b2984097bc3ecb06b99af96e700547db3483c2f640956e4754d2 |
| doc/saneamento-2026-10-16/matriz-decisoes.md | f0dd174a1f68c111053efd7be6cfc129a9dfec1eeefa55d9ae23d1e202a5cdb8 |
| doc/saneamento-2026-10-16/pauta-dec-15.md | c5e7e9c16bae077cc1fee5908b8538e3308e98f864a441542cefc357f02df3d1 |
| doc/saneamento-2026-10-16/plano-e-revisao.md | a2e594bfae8d62be8f0cf6ddb2f537cf5cb3b42687dee7671b2a012c2e42016b |
| doc/saneamento-2026-10-16/preservacao.md | 3d4d4409c478e12758d72e93124f67b6df6033175b5effe3496695f0ef1ab5f6 |
| doc/saneamento-2026-10-16/preservar-videos.ps1 | 37a16ba2e12cb5613523b9f6083c78e748b127e830cb97e9c4a32a812e75d753 |
| doc/saneamento-2026-10-16/README.md | 46ed3823bb253f0161842f573e68f6700af14f8b4339198ad8a7a5677d3e43c5 |
| doc/saneamento-2026-10-16/redacao-ca-23.md | f351af052c932889a977f7cced50644bc6ee077564c982118c43d885d480e3fe |
| doc/saneamento-2026-10-16/fase-3/dossie-institucional.md | 348c686878ec5e096c1c9958613de91e8313e70d39184e8911f7caac39570aaf |
| doc/saneamento-2026-10-16/fase-3/dossie-tecnico.md | 044fe396423fa43453812b80a43a0b63b9896618a7df3b873ddc57e655e1de30 |
| doc/saneamento-2026-10-16/fase-3/homologacao-e-protocolo.md | a9fdc2f5732c8522bc6a559d257c60832e41f3f907bb1a386989caff1412906f |
| doc/saneamento-2026-10-16/fase-3/matriz-e-limitacoes.md | 24113e51ef4d0507bdb709aaf33d77bfbda00d67d59c183e0bc3716f9a05440f |
| doc/saneamento-2026-10-16/fase-3/README.md | 7f4034ce2b1d998995f7d126093a6ae69a58a6f6e5f4a9b6b0a4ac45a4a9665e |
| doc/saneamento-2026-10-16/fase-3/reproduzir-em-memoria.py | c056e3c540ee195d574b093d78023c5e37de45f156768d1df962d4ffe881fea3 |
| doc/saneamento-2026-10-16/fase-3/resultado-em-memoria.json | 61ea35832aadfcb889e2a8d86fd1b59bf62b8af81b53056789eb31e014427aeb |
| doc/saneamento-2026-10-16/fase-4/consultas-finais.md | 01924190371e6077712fb931f202c34e866f9294a1fea8945176fd2d5d8419de |
| doc/saneamento-2026-10-16/fase-4/matriz-conformidade.md | 0649d0c02365855868b6e6d37d2b2a70a471b31aba1e9c3528df62bf1e5fc471 |
| doc/saneamento-2026-10-16/fase-4/plano-demonstracoes.md | 73665811e605a5f0fd8382a6eac7f6415fb0561d4fc41ac82c53cbb857adf196 |
| doc/saneamento-2026-10-16/fase-4/proposta-autorizacao.md | fcb9cc4aa55216e7f3089904520990a6820e396972feeb541bf57b0c701b7b73 |
| doc/saneamento-2026-10-16/fase-4/protocolo-para-aprovacao.md | b86567d49d553c254b59c7c1006e264e5637a63934c752d2b36f0f1e81a05567 |
| doc/saneamento-2026-10-16/fase-4/README.md | b3914761fee7fa730b1d72360333c47d6c3f2fb7c111257ea157935149b9365e |
| doc/saneamento-2026-10-16/fase-5a/baseline-planejada.md | 47ce72b09c376c4bb33f154f19052c9ec08a1e59dc5dbbf602f13757f0ee2a0a |
| doc/saneamento-2026-10-16/fase-5a/evidencias-43-condicoes.md | 74942743aee9c76856f879b9591d31756fc11fa16b7f435148387b9a46880f61 |
| doc/saneamento-2026-10-16/fase-5a/inventario-tecnico.md | 0de700e725d53a259f58a6ff0c103cbca658673b70e5d5fd60aa758501335b80 |
| doc/saneamento-2026-10-16/fase-5a/isolamento.md | 6a0e6a7140e4e868fd90b6e2884d80f5a75fb960fbbf149d609171f957aba7f4 |
| doc/saneamento-2026-10-16/fase-5a/plano-5b-e-autorizacao.md | a0ab8a357b78dd3f5c776341ede37c0bf8c17628b14140fdb2663415689634a6 |
| doc/saneamento-2026-10-16/fase-5a/README.md | 5bff5efb5692b6c777052af526887930eae27dee0ee6a80b327c3db64c464a91 |
| doc/saneamento-2026-10-16/fase-5a/responsabilidades.md | f46fa4fe36b44b7c296b1bb5c0e9962e0985df6bb842f626925a025571e4b296 |
| doc/saneamento-2026-10-16/fase-5b.1/autorizacao.example.json | a0fed569fccf98a22b0181f8c6fab2b79ad3c5125a52bae2ac507a1568b5d000 |
| doc/saneamento-2026-10-16/fase-5b.1/autorizacao.json | 70bca1309c230d61629d09d42c09da8df5160dace441cb922ed07835b872caee |
| doc/saneamento-2026-10-16/fase-5b.1/baseline.json | 9766ace9d1fd8a7250dd409b2b8dabcafbbdd11e0ce29ae261cfd9d59c54e97b |
| doc/saneamento-2026-10-16/fase-5b.1/cenarios.json | 3813b6193ca68e6b828391d2e5463206e1b541552710c46488835d2518ca4d97 |
| doc/saneamento-2026-10-16/fase-5b.1/compose.homologacao.yaml | 1dcbb2314a5e7b3e3c2ec2fb135bbb3daad73b884137c0092c349597eeebc06f |
| doc/saneamento-2026-10-16/fase-5b.1/homologacao.env.example | 5e3f08e55f99db85c0331ba5b6cfe1a8d0183d0a77e0752239f21c45e83cdf07 |
| doc/saneamento-2026-10-16/fase-5b.1/integridade.json | c82d449005a8161d3ef8b40d84f09a3055c749d8e152ac504bfadb79d22d5405 |
| doc/saneamento-2026-10-16/fase-5b.1/operar.py | eab9d9b5d53946e84822ce0d3924633bbff03bc74f9108b1c288d8d210c46c9a |
| doc/saneamento-2026-10-16/fase-5b.1/procedimentos.md | 10123faac99e4b4ebffb1b6b067decdbce34b11b8364fafaa7edce59a6293656 |
| doc/saneamento-2026-10-16/fase-5b.1/README.md | 707c6fe3c622331404d784ec95bf3e9741aee15e976608ffd003fb5ef0ec4a81 |
| doc/saneamento-2026-10-16/fase-5b.1/revisao-estatica.json | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f |
| doc/saneamento-2026-10-16/fase-5b.1/revisao-estatica.md | 35122cb15beba895d307b1f131cd6b13aeb28847b0caa3806f006be2599ee433 |
| doc/saneamento-2026-10-16/fase-5b.2-a/acoes-e-baseline.md | df84bb1bf63f823cf720b5eff0024afff9f4849dd1e9d9a6975657859680165f |
| doc/saneamento-2026-10-16/fase-5b.2-a/evidencia-estatica.json | 8c4cd34c4bb71f777f99bfdee544efaa654d41978916e0e9bbce998361cc25f2 |
| doc/saneamento-2026-10-16/fase-5b.2-a/imagens-e-autorizacao.md | 7462d0be7e11c70eab144d3ac566450ffcb2df7a230543561fb1de1dc92522eb |
| doc/saneamento-2026-10-16/fase-5b.2-a/inspecao-e-guardas.md | bf0b8057207a7fc355c6b6a59f1c2a8c5eecd0636cd7f48c667c53a8aaba68a0 |
| doc/saneamento-2026-10-16/fase-5b.2-a/README.md | d66912ae241aa83f015e0b605ed05448ae970cb8480aaf881d9b541d5bfcf67a |
| doc/saneamento-2026-10-16/minutas/cefor.md | e39020821b4e9dcaedbe47498348800ab0c4fa596a0c3b77a10fbfbc432276e5 |
| doc/saneamento-2026-10-16/minutas/correio.md | 1649ffe148e068fb1da859a049063b32177e80b42e2836fca9be0aee63259e10 |
| doc/saneamento-2026-10-16/minutas/encarregado.md | ce777164c93720aaec41700080a9252d36ea7c7526a2d0aa881cc7e3aa6a6662 |
| doc/saneamento-2026-10-16/minutas/juridico.md | 6c5b0ac5b735267e8fe5cf0090f53f24588c98e097d85791b0cc4666ee0c7adf |
| doc/saneamento-2026-10-16/minutas/ti.md | d4f734cde00671ce50d12f488c06893aa489389392cfc1475111527f98f9f1cf |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/estado-anterior.json | a2b62a8b90993aa32ba0ae0724100f33c157b85367135b2045611700f43ad763 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/evidencia-a1.json | 8dbd5fb26d840296e18bb0ed7b2ea2cce8d6bd246d88ef1f07870a201d643622 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/matriz-correcao.md | b4ea46271270a0b1fa2d1dd84301e4e4bbade6be8cd75d9cf3f4f7b41a521185 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/operacoes-e-metadados.md | 333a0142358103e8811026b7c4fd082a2877b51b8d8dd8389e4ef68e1d9a501f |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/README.md | c6f21704e43c63d0184803a425bbbb1084fcbf50c15faabd5d900f3aebcd1e99 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/test_guardas_puras.py | ff976e15c7f4ab44a344e4923f178da80dd2df259a7399f27ca246b0c26717dd |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/validacao-e-negativos.md | f307e58dc1ea9166dbb300a1aff51ffe394e4ab7291e9153cff7031c326d6ea4 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/baseline-e-aceite.md | 034de0fcd95336b665b24d626d26588daa26ea0514682e84683627dc996e770f |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/consultar_metadados_publicos.py | 2dec743e3a37f48d8d736859343e8cf78e9510522ecd29879745525a99186fb1 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/Dockerfile.homologacao.proposta | 5967642beed56184cd895016cba5d2df8574eea70f66bf0f9309ad417668e2bb |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/evidencia-a2.json | 7dc27d6df0bf9b6f5f8b54b3cf444d86bfe141166a6b1eb95f8343bb3229fdd4 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/hashes-antes.json | 599368acde19f352805f769ef66092fee133ea48d0d00bf10b04e262a210cdf9 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/inventario-imagens.md | ccfdb95f38f9879527e815e1a3bca5c6301e488f2fd50ce580114fd13a6682a4 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/matriz-autorizacao.md | d843b138aa6bbd78b37fd2ec4a22bfd97833f72c5b0732c02fbb1dd5a06edaa2 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/metadados-publicos.json | ce8cc77c6e8c3d448f939e10c91ef13b30d2e45f8aeb48b06e1ee73770c0d6af |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/plano-inicializacao.md | 8039051aab0b11cad97048ee24e3d4adc5f92780bbd1b596cd363d248df85b75 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/proposta-primeira-validacao.md | f38c2338c7a383921ea3d06dc3f47b944fae7be3b5f00f1c7ed8f88f5a404b4f |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/README.md | 6e5f95cee13e189a009954a842aa5ffe3e8e6b843c11b1d7d2f73bc22b0203b3 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/sessoes-web.md | 28aceb625d3b5a2deb442d1f852e23fab92fd37355730bca96f31711b7155913 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/testes-e-bloqueios.md | a64c6d6098a244ef714fcf051283b6a6b6e3baa19912cf70961e56d7af313444 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/test_guardas_a2.py | ed0a6448f69e346bdec43c8b5c90409a0e0caf72c0315900867285ce4137a395 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/consulta-engine-proposta.md | 6084e7bd41eb3de62ed4fa76c16b02d9e3c8833e896ddbd3f2d233fb2e7aead8 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/criterios-aceite.md | 183aae813b0d6b950a7383c97ba58b7454e828b2baabc7ac87f6fa50ddd737af |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/matriz-autorizacoes.md | 1559bc7aa01ea67a245257e3cf6fa234184ee07f1cfa7f6ae50c57ec9dae7496 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/matriz-dependencias.md | 877e6499f128f6a8ee09e2ff94c303d78a8154b28b6c51b4ec2cd7dfb5efd0d9 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/pendencias-e-bloqueios.md | 679357f87dd1fe82844bb5f8e145fcdb645674e97aa38043c99066078e9cc5b8 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a3/README.md | cab2c870242055be6f4baf0f58e80b2ffa54f11ca9663f9c713cbb4ec81c859f |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/autorizacao.example.json | 8a5aed2ed22f889da1037fd5b62adafd90d67bcbcfcd90d0d55feff795b49a3e |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/compose.homologacao.yaml | f85b126b5e63005f5370b8d325362f08d7d1567984869f5a67ecf3c99ac88603 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/integridade.json | b348326c5233b7a4d871354bf13bb70e997756203d47c085f0d9224f0185383a |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/operar.py | 1c64fe4bc078ee7cfa9f971d266f785df66d27a83bb996cc4bb3576f71aaa790 |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/procedimentos.md | ed50bea1a00b142657737c3e45352e8d5faa9f2cffe2596c82d9d41c4117578b |
| doc/saneamento-2026-10-16/fase-5b.2-a/fechamento-a2/historico-a1/README.md | 8d2da3e5ed0ab36cb5482c5ebdee417101c67674542a14b7adec0e77ad7861f2 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/autorizacao.example.json | 0df11adf11ec09a0ab59516cc3836654908ccce879b472984f039fcb5358eec4 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/baseline.json | 1c3fa946a51da738f2c666cecb4601f79234c53441959646085a2cad8716ac37 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/cenarios.json | 3813b6193ca68e6b828391d2e5463206e1b541552710c46488835d2518ca4d97 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/compose.homologacao.yaml | 8b33a11d89269634753a9be8f0d4f3472a296ce106e7e4a6a31ed0065c695ce9 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/homologacao.env.example | 889a2cecf34a3cfd814319dd3e909bb9adb3186e2f1842fbf7e311a614bc7501 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/integridade.json | 6aa4f89caf5d0e102b75daeb3628c41ce283624c1cc7b423cb7fc64f04567206 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/operar.py | 20af954d51cad18f2643932b7d80b79a4a3336cc68bac56389fac86b58eb1c92 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/procedimentos.md | 40c7814aadca53c58feb0808b27edab69b61777c92585210e963aa6a46311ff6 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/README.md | e7408060b4e72b306ed18bb207e7f41b53f4d69a6a8781433825b94fb3c2a7de |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/revisao-estatica.json | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/revisao-estatica.md | 35122cb15beba895d307b1f131cd6b13aeb28847b0caa3806f006be2599ee433 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/isolamento/contrato.py | 3a9097de00a69db6c4adc3b3e51a893097ce2b29142044c45a9e948c29628617 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/isolamento/iniciar_aplicacao.py | bf0a2c368701dc3dc75216dd579a76b578feb4937e686e0a05caa80248c03a21 |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/isolamento/settings_homologacao.py | cdb95950abace0b6c7710cb7f93c2b0a911f12789c4508226b654bec0f37a81f |
| doc/saneamento-2026-10-16/fase-5b.2-a/correcao-a1/historico-5b1/isolamento/tarefas.py | 869fcd8c313fb8b45910da2dc93553359566fa5196521dd3fef09824954c5919 |
| doc/saneamento-2026-10-16/fase-5b.1/docker-cliente/config.json | ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356 |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/contrato.py | 80b0316aafcac4c97532080402bcbfbfbca75bec5cb55cae3a2db13742876747 |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/iniciar_aplicacao.py | 51552a3c9f62d0d311d6d5dcdd203a5d357786912e9d3ee2c63c3aaedb5df21f |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/politica-protecoes.json | 1fba2dac871dd024ff06e1f2f6f91882474b88f03bc2029e9eb1498bb022598d |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/politica_operacional.py | 36c2d9441e048c3931f217531178b917ea9bd4f0f13bd7980ee9a06da18f1fef |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/settings_homologacao.py | cdb95950abace0b6c7710cb7f93c2b0a911f12789c4508226b654bec0f37a81f |
| doc/saneamento-2026-10-16/fase-5b.1/isolamento/tarefas.py | f6c2e3e7aa17d8f8c717c5f0632aa67806d74c85e3677af7833f9f6fb198f2a1 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/alternativas-saneamento.md | 30d15a3e145cbbec2038dda3baa38b98b8c6990f4029715ff9f890b579c991b6 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/controles-operacionais.md | 712c22ccc659bbc6f8620e560ee680ce284dd7f91a0bd4742eb270c50111af2a |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/integridade.md | fef659a6a143a09f26b72c95a51c41bd20d9fde52f65de6bf2bade9583bc5bd6 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/proposta-autorizacao.md | 4343924cf587a4e8a0a397e595afa6c2a1f9b1f67d4a974080e3b892a373887b |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/README.md | 0d11247c395b79a913a2051b3f17e1683d4edf55cfa821bd6902a6b0cbcc46d1 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a4/manifesto-a4.json | fb0f7aed253644c4217e22162d2b328d8929e78b96b92abe16739d9c7014010d |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/controles-executor.md | ca2c07655fcbebe4352f71fa012fe3cc160b6406a0f8a8535bf035517ba3dfc3 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/estrategia-integridade.md | fc5a7f9c44836553724bb16f4d18eaa008f48c39b9b9b9657f868331f90397c8 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/gates-autorizacao.md | ccdbf70acc7fb181c2d1f50c6aba8142b4e43b4fed1d0d535848f56d1a324c4b |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/matriz-integridade.md | f1918eed671bba9a151afbb83657268fde872f9ceb2ca52ed3a44e2082c2d472 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/plano-implementacao.md | ccea876a9efb6ad1cb581fa558adfcdc25152c5e9aef41fae49630d0a9db6896 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/README.md | 33c4640a2c2e92aa70cfc681de760100e981d7b17799486da7b5ae85940bb622 |
| doc/saneamento-2026-10-16/fase-5b.2-a/validacao-a5/manifesto-a5.json | 7632e49c687a27dabdc96131b46e7e2623d118bf18c2629d3af5b63a2b904f5d |
| backend/processo_seletivo/classificacao/application/calculo.py | cd2dbafa2779ede93abef6b202f63de91401c69a1b63bf6ed98d35a4ca79b463 |
| backend/processo_seletivo/classificacao/domain/desempate.py | 7daa3f4a8418ae6be39b662f29386036af5186e08b68ca3f4bc5571e49d06c97 |
| backend/processo_seletivo/classificacao/domain/universo_classificavel.py | 7a8539743433da19aa2513ba5ed93379dc4218075b1c7e619eeb4e5feb00fdd1 |
| backend/tests/integration/classificacao/test_previa_equivale_ao_oficial.py | 02b754e5301a80c6450ccac6f2612d0fca08d47cfe632f8232783edf8263ab8e |
| backend/tests/unit/classificacao/test_ordenar_com_trajetoria.py | d683fd39e805a6f7be3098b3228eb7a8ad71067da807abb80028bda4423c4155 |
| backend/tests/unit/classificacao/test_universo_classificavel.py | 9d65998dd1f04c1b136e6e3b66e5f2af9359cd44b8f426e1fc73ea2c498033a1 |


