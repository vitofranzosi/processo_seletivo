# Quickstart — Recorte transversal do documento exigido

Como provar a feature de ponta a ponta, pelos canais dos atores (`SC-268`, Princípio VI): compor e
publicar pela gestão, inscrever e enviar pelo portal, analisar pela Mesa. Sem banco, shell ou API
no percurso. O shell só aparece para subir o servidor e ler o código de acesso.

---

## Pré-requisitos

- Worktree e banco próprios (`DB_NAME`). Migrations aplicadas, e `provisionar_papeis` rodado **depois**
  delas: a saída deve dizer **34 de 34**. Se o primeiro número vier menor, a segunda passada não rodou.
- Servidor local com `INTERFACE_SELETOR_IDENTIDADE=true` e `PORTAL_IDENTIDADE_DEMO=true`. Sem elas,
  `/gestao/` devolve 503 e o portal não identifica.
- O código de acesso do portal sai no terminal do servidor (backend de e-mail de console).
- Datas **futuras** para as inscrições: não há cadastro retroativo de Edital.
- PDFs de teste para anexar.

## Cenário A — o 903 recomposto (US1, US2; `SC-262`, `SC-263`)

1. **Compor** pela gestão um Edital com dois Perfis:
   - **C1**: modalidades AC (declarada ampla), PcD "Pessoas com Deficiência", PPIQ;
   - **C2**: modalidades AC (declarada ampla), PcD "Pessoas com Deficiência".
2. **Documentos:**
   - identidade: todos, obrigatório;
   - laudo médico: **"Pessoas com Deficiência (PcD) — em todos os Perfis que a têm (2 de 2)"**,
     obrigatório;
   - autodeclaração étnico-racial: C1 · PPIQ, obrigatória.

   **Esperado:** a opção "AC em todos os Perfis" não existe.
3. **Revisão:** nenhum IMPEDE sobre documentos. Submeter, homologar e publicar.
4. **Documento publicado:** um grupo *"Dos candidatos concorrentes na modalidade Pessoas com
   Deficiência:"*, com o laudo, sem nome de Perfil.
5. **Portal, cartões:** C1 e C2 anunciam *"Se concorrer em Pessoas com Deficiência, também: Laudo
   médico"*.
6. **Portal, inscrições:**
   - PcD no **C2**, só com a identidade: **o envio é recusado**, e nomeia o laudo. Anexado o laudo,
     o envio passa.
   - AC no C1, com a identidade: envia. O laudo não foi pedido.
7. **Mesa:** distribuir as duas inscrições a um analista e abrir cada uma.

   **Esperado:**

   | Inscrição | Identidade | Laudo | Autodeclaração étnico-racial |
   |---|---|---|---|
   | PcD no C2 | apresentado, "pedido de todos os candidatos" | apresentado, "pedido de quem concorre em Pessoas com Deficiência, em todos os Perfis" | "Não se aplica: pedido de quem concorre ao Perfil C1 em Pretos, Pardos, Indígenas e Quilombolas" |
   | AC no C1 | apresentado | "Não se aplica: pedido de quem concorre em Pessoas com Deficiência, em todos os Perfis" | "Não se aplica: …" |

   Nenhum aviso de lista reconstruída.
8. **Consulta administrativa:** a PcD do C2 sai com *"2 de 2"*, e o detalhe mostra os mesmos três
   estados.

Contagem de `SC-262`, sete superfícies: PDF, cartão do C1, cartão do C2, inscrição PcD no C1,
inscrição PcD no C2, Mesa do C1 e Mesa do C2. Para a do C1, inscrever também um PcD no C1.

## Cenário B — Retificação depois dos envios (US3; `SC-264`, `SC-266`, `SC-267`)

Sobre o Edital do cenário A, com as inscrições já enviadas:

1. **Retificar** a denominação de PcD **só no C2**, para "Pessoa com Deficiência".

   **Esperado:** **exatamente um** IMPEDE, que nomeia as duas denominações e os Perfis de cada uma,
   e leva à etapa Perfis.
2. **Retificar** a denominação nos dois Perfis. A Retificação passa.
3. **Retificar** o laudo de transversal para "C1 · PcD" (campo "Modalidade em todos os Perfis" vazio,
   Perfil C1, modalidade C1 · PcD). Publicar.
4. **"O que mudou":** há uma linha *Documento exigido "Laudo médico" — Modalidade em todos os Perfis —
   alterado*.
5. **Mesa e consulta:** as duas inscrições do cenário A mostram **exatamente** o que mostravam.
6. **Portal:** uma nova inscrição PcD no C2 envia sem o laudo, porque agora ele é só do C1. A Mesa
   dela diz "Não se aplica: pedido de quem concorre ao Perfil C1 em Pessoas com Deficiência".

Repetir os passos 3 e 4 para acrescentar e para trocar o código, que são as outras duas operações de
`SC-267`.

## Cenário C — o 140/2025 (`SC-260`, `SC-261`)

Recompor a etapa de documentos do item 5.5, com os 16 Perfis e as quatro modalidades:

| Documento | Recorte | Obrigatório |
|---|---|---|
| h-I laudo, h-II autodeclaração PcD | PcD em todos os Perfis | sim |
| i-I autodeclaração étnico-racial | PPIQ em todos os Perfis | sim |
| k autodeclaração transgênero e travesti | PTT em todos os Perfis | sim |
| i-II, i-III (indígena), m (quilombola) | PPIQ em todos os Perfis | não, com instrução |
| e (serviço militar), l (servidor) | todos | não, com instrução (D2) |

**Esperado:**
- **7** linhas para os sete documentos condicionados à modalidade, contra 112.
- No PDF, **4** obrigatórios nos grupos de modalidade, **3** facultativos no grupo de PPIQ e **2**
  facultativos no grupo de todos.

## Cenário D — a inscrição anterior à feature (US4; `SC-265`)

No banco do estudo, onde está o 903/2026 original:

1. Abrir na Mesa a inscrição PcD do C2 (`INS-2026-WTBAMDBH`).

   **Esperado:** o aviso de lista reconstruída, e o laudo como *"Não se aplica: pedido de quem
   concorre ao Perfil C1 em Pessoas com Deficiência — o Edital publicado o exigia de todo candidato
   em Pessoas com Deficiência. O portal não o pediu a esta inscrição."*
2. Conferir o resumo criptográfico do documento publicado do 903: **o mesmo** de antes da feature.

Sem acesso ao banco do estudo, o mesmo cenário se monta publicando um Edital com o recorte ambíguo
**antes** de aplicar esta feature, numa árvore anterior. Os testes de integração o reproduzem por
fixture.

---

## A suíte

```bash
cd backend && make lint check test-pg POSTGRES_USER=<superusuário> DB_NAME=<banco da worktree>
```

As famílias novas ou tocadas:

| Família | O que prova |
|---|---|
| `tests/unit/inscricoes/test_aplicabilidade.py`, `tests/unit/editais/test_documentos_recusas.py` | as cinco formas, a regra do código, o veredito, o predicado da divergência, as recusas na gravação |
| `tests/unit/editais/test_validacao_inscricao.py` | os cinco achados, um por código, a mensagem com três saídas |
| `tests/contract/test_elevacao_degrau_17.py` | o conteúdo da 16 é lido como `modalityCode: null`, e o literal não muda |
| `tests/unit/publicacoes/test_pdf_documentos_exigidos.py` | um grupo por código |
| `tests/integration/inscricoes/test_lista_exigida*.py` | a gravação, a imutabilidade nas duas camadas, o `BEFORE INSERT`, a idempotência, a reconstrução |
| `tests/interface/test_mesa*.py`, consulta, portal | os três estados, a razão, o aviso, a leitura depois de Retificação |
| `tests/interface/test_retificar_documentos.py`, `test_campos_vem_do_contrato.py` | o campo na Retificação, e a guarda do contrato |
| `tests/migrations/test_migrations.py` | contagens, gatilhos, caminho reverso |
