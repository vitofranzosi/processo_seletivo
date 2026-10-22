# Auditoria de integridade A.4

Data: 19/10/2026. Branch `001-decisoes-pendentes`; HEAD `550f5bb8983bcdbf32eff210622449a0c959d12d`.

## Método e escopo

Leitura binária com Python `-B`, SHA-256, JSON e subprocessos Git estritamente de leitura. Nenhum módulo do operador foi importado ou executado. Nenhuma conversão foi gravada. A representação comparativa foi calculada somente em memória: `b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")`. Os bytes atuais continuam sendo a identidade operacional; a equivalência textual não libera a guarda.

Conferidos os 12 itens de `fase-5b.1/integridade.json`, os 17 hashes posteriores da evidência A.2 e os 19 hashes de documentos/propostas A.2. A comparação das cópias A.1 com seu inventário anterior consta no manifesto A.4. Inventários de fases distintas não são intercambiáveis: uma versão antiga deve ser comparada à sua cópia histórica, não ao operador revisado.

## Manifesto operacional: 10 correspondências e duas divergências

| Arquivo | SHA-256 esperado | SHA-256 atual | SHA-256 CRLF em memória | Resultado |
|---|---|---|---|---|
| fase-5b.1/autorizacao.example.json | a0fed569fccf98a22b0181f8c6fab2b79ad3c5125a52bae2ac507a1568b5d000 | a0fed569fccf98a22b0181f8c6fab2b79ad3c5125a52bae2ac507a1568b5d000 | 64ffd488c98b9b34dd2f072af8e723779e7737e946aee3051ecb9a0db4162cc1 | Bytes coincidem |
| fase-5b.1/baseline.json | 9766ace9d1fd8a7250dd409b2b8dabcafbbdd11e0ce29ae261cfd9d59c54e97b | 9766ace9d1fd8a7250dd409b2b8dabcafbbdd11e0ce29ae261cfd9d59c54e97b | b70dff571e054f6ab12eba8f4bdce55e2ce5c45daaa370c50bdb0fc6b5a870b5 | Bytes coincidem |
| fase-5b.1/cenarios.json | 3813b6193ca68e6b828391d2e5463206e1b541552710c46488835d2518ca4d97 | 3813b6193ca68e6b828391d2e5463206e1b541552710c46488835d2518ca4d97 | 7f31f93e84eb56e7c3085df66c34ca3927eeedd309defdb84266302bf538333a | Bytes coincidem |
| fase-5b.1/compose.homologacao.yaml | 1dcbb2314a5e7b3e3c2ec2fb135bbb3daad73b884137c0092c349597eeebc06f | 1dcbb2314a5e7b3e3c2ec2fb135bbb3daad73b884137c0092c349597eeebc06f | 8a4524efddd1305772203341e8cdc67b35711e832c207b1295da8406a519a9de | Bytes coincidem |
| fase-5b.1/homologacao.env.example | 5e3f08e55f99db85c0331ba5b6cfe1a8d0183d0a77e0752239f21c45e83cdf07 | 5e3f08e55f99db85c0331ba5b6cfe1a8d0183d0a77e0752239f21c45e83cdf07 | a7ed089647746c80ca665d9fcd7fa29ef30e490577ef103053db572251917fde | Bytes coincidem |
| fase-5b.1/isolamento/contrato.py | 80b0316aafcac4c97532080402bcbfbfbca75bec5cb55cae3a2db13742876747 | 80b0316aafcac4c97532080402bcbfbfbca75bec5cb55cae3a2db13742876747 | 026963b6b50e6a53838e757e4e948992e758900d242aa3fd342e4f6e909231b0 | Bytes coincidem |
| fase-5b.1/isolamento/iniciar_aplicacao.py | 51552a3c9f62d0d311d6d5dcdd203a5d357786912e9d3ee2c63c3aaedb5df21f | 51552a3c9f62d0d311d6d5dcdd203a5d357786912e9d3ee2c63c3aaedb5df21f | c7b13ab978ef0606c70315fb72495ab8bbf3a17fa0d98f39174bf72b77955e92 | Bytes coincidem |
| fase-5b.1/isolamento/politica-protecoes.json | 1fba2dac871dd024ff06e1f2f6f91882474b88f03bc2029e9eb1498bb022598d | 1fba2dac871dd024ff06e1f2f6f91882474b88f03bc2029e9eb1498bb022598d | 02f56876e81d2db66891b15c0973a018265d32180da0a2cc6e57c38230aa8b10 | Bytes coincidem |
| fase-5b.1/isolamento/politica_operacional.py | 36c2d9441e048c3931f217531178b917ea9bd4f0f13bd7980ee9a06da18f1fef | 36c2d9441e048c3931f217531178b917ea9bd4f0f13bd7980ee9a06da18f1fef | 19d30c0dc6d6f7884711a8a0bebc5b6749e4d00a7c083d14428a7a34a4742812 | Bytes coincidem |
| fase-5b.1/isolamento/settings_homologacao.py | cdb95950abace0b6c7710cb7f93c2b0a911f12789c4508226b654bec0f37a81f | cdb95950abace0b6c7710cb7f93c2b0a911f12789c4508226b654bec0f37a81f | de7b4aadfbd8fe34a75def3353728b4eebdf337c53898e48da9132f01d861d5f | Bytes coincidem |
| fase-5b.1/isolamento/tarefas.py | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 | f6c2e3e7aa17d8f8c717c5f0632aa67806d74c85e3677af7833f9f6fb198f2a1 | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 | Diverge; CRLF coincide |
| fase-5b.1/operar.py | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 | eab9d9b5d53946e84822ce0d3924633bbff03bc74f9108b1c288d8d210c46c9a | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 | Diverge; CRLF coincide |

`operar.py`: 358 LF, zero CRLF e zero CR isolado. `isolamento/tarefas.py`: 32 LF, zero CRLF e zero CR isolado. Para ambos, a representação CRLF coincide com o hash esperado. Não foi identificada diferença adicional de conteúdo nessa comparação criptográfica; isso não é validação da segurança do programa.

## Divergências adicionais contra registros A.2

| Arquivo | SHA-256 esperado | SHA-256 atual | SHA-256 CRLF em memória | Resultado |
|---|---|---|---|---|
| fase-5b.1/integridade.json | cfedd1455cd34e91679115e9c7e30d2f05a53afd63efe961271fda03c3eb7982 | c82d449005a8161d3ef8b40d84f09a3055c749d8e152ac504bfadb79d22d5405 | cfedd1455cd34e91679115e9c7e30d2f05a53afd63efe961271fda03c3eb7982 | Diverge; CRLF coincide |
| fase-5b.1/operar.py | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 | eab9d9b5d53946e84822ce0d3924633bbff03bc74f9108b1c288d8d210c46c9a | cceeb2aa92d6b8271dab8891c2b31ef873c318495c715115c9734962e3b0ca78 | Diverge; CRLF coincide |
| fase-5b.1/revisao-estatica.json | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 | Diverge; CRLF coincide |
| fase-5b.1/isolamento/tarefas.py | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 | f6c2e3e7aa17d8f8c717c5f0632aa67806d74c85e3677af7833f9f6fb198f2a1 | d6b7b61a429cd922663b0d89269477d91770b4052c78030e421bf85f337d07b4 | Diverge; CRLF coincide |
| fase-5b.2-a/fechamento-a2/hashes-antes.json | 312c03b7650ad6c7c927df46cd58043fb39839fd7902a515c05d490ec3d2a5e0 | 599368acde19f352805f769ef66092fee133ea48d0d00bf10b04e262a210cdf9 | 312c03b7650ad6c7c927df46cd58043fb39839fd7902a515c05d490ec3d2a5e0 | Diverge; CRLF coincide |
| fase-5b.2-a/fechamento-a2/inventario-imagens.md | 9dd46415bc558c43a81b3984e111172c61c9cacc581fce180310cbb0378961c3 | ccfdb95f38f9879527e815e1a3bca5c6301e488f2fd50ce580114fd13a6682a4 | 9dd46415bc558c43a81b3984e111172c61c9cacc581fce180310cbb0378961c3 | Diverge; CRLF coincide |
| fase-5b.2-a/fechamento-a2/metadados-publicos.json | 498b27bc248d1aefc2d3a38018299fd0682fcb7ceed2f366276c99f1e3ef8719 | ce8cc77c6e8c3d448f939e10c91ef13b30d2e45f8aeb48b06e1ee73770c0d6af | 498b27bc248d1aefc2d3a38018299fd0682fcb7ceed2f366276c99f1e3ef8719 | Diverge; CRLF coincide |
| fase-5b.2-a/fechamento-a2/historico-a1/integridade.json | 4ec8e0aaba84aec85a260c8f168e3c1a9232cf5dff7e1287497c8b41b89830b3 | b348326c5233b7a4d871354bf13bb70e997756203d47c085f0d9224f0185383a | 4ec8e0aaba84aec85a260c8f168e3c1a9232cf5dff7e1287497c8b41b89830b3 | Diverge; CRLF coincide |
| fase-5b.2-a/fechamento-a2/historico-a1/operar.py | 006dcdf52014c0a01acd0543a247932d6e906b51ef203a7fff584929d79c21bf | 1c64fe4bc078ee7cfa9f971d266f785df66d27a83bb996cc4bb3576f71aaa790 | 006dcdf52014c0a01acd0543a247932d6e906b51ef203a7fff584929d79c21bf | Diverge; CRLF coincide |

São nove caminhos divergentes distintos nos dois inventários A.2: quatro dos 17 artefatos posteriores e cinco dos 19 documentos/cópias. Os dois scripts estão incluídos nesses nove; portanto há sete caminhos adicionais ao par originalmente relatado. Todos os nove recuperam o hash esperado pela representação CRLF em memória. O manifesto operacional também mudou de representação em relação ao hash registrado pela A.2. Nenhum desses registros foi atualizado.

## Git e procedência

Verificadas também as 15 cópias de `correcao-a1/historico-5b1/` contra `correcao-a1/estado-anterior.json`: 13 correspondências e duas divergências adicionais, ambas explicadas pela representação CRLF em memória. No conjunto dos inventários A.1/A.2 são 11 caminhos divergentes distintos; não se confundem com as duas falhas do manifesto operacional atual.

| Cópia histórica A.1 | SHA-256 esperado | SHA-256 atual | SHA-256 CRLF em memória |
|---|---|---|---|
| integridade.json | da4a15af9ef69c74c8446d5b46bff72d6a1d345d378283c5a8cb51f8ba2d7a10 | 6aa4f89caf5d0e102b75daeb3628c41ce283624c1cc7b423cb7fc64f04567206 | da4a15af9ef69c74c8446d5b46bff72d6a1d345d378283c5a8cb51f8ba2d7a10 |
| revisao-estatica.json | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 | 093a8481df6ef8873aa551a0d8a887325c2a9094c4bcd58eebf5a32aa9f9d31f | 408975a7b2532eaad33198ed6faef1e39c4d65d564d2f3ea773380d6890914a6 |

`.gitattributes:5` determina `* text=auto eol=lf`; ambos os scripts têm `text=auto`, `eol=lf`, `filter` e `working-tree-encoding` não especificados. `core.autocrlf=true` vem de `C:/Program Files/Git/etc/gitconfig`; `core.eol` e `core.attributesfile` não estão definidos nos valores consultados (retorno Git 1). O atributo eol=lf específico do repositório prevalece sobre a expectativa genérica de checkout CRLF.

Consultas reproduzíveis, somente leitura:

```powershell
git config --show-origin --get-all core.autocrlf
git config --show-origin --get-all core.eol
git check-attr text eol working-tree-encoding filter -- doc/saneamento-2026-10-16/fase-5b.1/operar.py doc/saneamento-2026-10-16/fase-5b.1/isolamento/tarefas.py
git log --format="%H %s" -- doc/saneamento-2026-10-16/fase-5b.1/operar.py
git cat-file blob HEAD:doc/saneamento-2026-10-16/fase-5b.1/operar.py
```

A última consulta deve ter stdout capturado em bytes, sem redirecionamento textual PowerShell que possa transcodificar. O manifesto A.4 registra os hashes dos blobs, não o conteúdo.

Os scripts foram encontrados no commit `424fc7130fb2cda9c854b77356d4146ec4827d89`. Os blobs desse commit e do HEAD são idênticos aos bytes LF atuais. Todos os caminhos comparados dos três inventários têm blob HEAD igual ao working tree. A mudança de representação antecede esta execução; estado Git limpo não significa concordância com um manifesto histórico CRLF.

## Classificação causal

- **Confirmada:** a divergência do par e dos nove caminhos A.2 é explicada pela representação LF/CRLF, dentro da comparação SHA-256 realizada.
- **Provável:** normalização Git ao incorporar/versionar arquivos sob eol=lf. A política e os primeiros blobs disponíveis corroboram a hipótese.
- **Indeterminada:** instante, ferramenta e agente exatos da conversão anterior. Não há registro anterior CRLF versionado nem trilha suficiente para atribuir a operação. Não atribuir a causa ao merge ou ao core.autocrlf isoladamente.

A custódia é preservada a partir do estado encontrado nesta A.4: 111 arquivos anteriores inventariados. Isso não certifica retroativamente a identidade binária dos 103 arquivos históricos com o estado original da A.3. O novo manifesto é evidência de auditoria, não substituto de `integridade.json`.

## Resultado

**INTEGRIDADE OPERACIONAL BLOQUEADA.** `verificar_integridade` rejeita o par antes de qualquer chamada Docker. Não se executou essa função para confirmar a falha: a conclusão decorre da leitura do comparador exato e dos hashes calculados independentemente.

