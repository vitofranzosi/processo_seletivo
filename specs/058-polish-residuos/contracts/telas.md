# Contrato das telas

Cada linha é o que a tela promete depois da feature, e a medida que a prende. **V** = linha da
[verificação](../verificacao.md); **TP** = `tests/interface/test_polish_da_058.py`.

| Tela | Elemento | Contrato | Prende |
|---|---|---|---|
| Processo | "O que fazer agora" | nenhum ato do Processo com `class="botao"` sem `secundario`; Encerrar e Cancelar em `ul.lista-acoes.em-linha.terminais`, por último, com `span.marca-irreversivel`; "Ativar" `botao secundario`; o aviso de impedimento depois | TP; V 1 |
| Detalhe do Edital e Processo | estilo | `.lista-acoes.em-linha`, `.lista-acoes+.terminais`, `.terminais .botao` no parcial `_estilo_das_terminais.html`, e não na folha comum | TP; o teste da `057` |
| Lista de Editais | tabela de cada Processo | dentro de `div.rolavel-no-estreito`; a 375 px, `scrollWidth` do documento = 375, `scrollWidth` da moldura ≥ borda direita do último botão; a 1280 px, sem rolagem interna | TP; V 2, 3 |
| Condução | "Recortes deste marco" | dentro de `div.rolavel-no-estreito`; a 375 px, documento = 375 | TP; V 4 |
| Alocação | matriz | `thead` fixo ao rolar a página, a 1280 px | V 5 |
| Folha | moldura | `.rolavel-no-estreito{overflow-x:auto}` só em `@media (max-width:60rem)`, na mesma regra da `.distribuicao-moldura` | TP |
| Matrículas | "O que sairá vazio, e por quê" | a `section` sem `.resumo`; título, nota, lista e confirmação empilhados | TP; V 6 |
| Resultados | tabela | `class="tabela"`; `td.numero` só na nota pontuada | TP; V 7 |
| Distribuição, Matrículas, Recurso, Ocupação, histórico, assistente | plurais | sem "(s)" no texto que o template compõe; `plural`/`contagem` | TP; V 8 |
| Etapas | Peso, Nota mínima, Pontuação máxima | `value` sem zeros à direita, ponto decimal; rascunho gravado idêntico | TP; V 9, 10 |
| Revisão | pares | coluna de rótulos `min(Nrem, 40%)`; primeiro valor de cada `dl` no mesmo x | TP; V 11 |
| Ocupação e Sorteio | motivo de sucessão | `textarea rows="3"` em `p.campo`, `name="motivo"`, mesma largura da Ordenação e do Corte | TP; V 12 |
| Todas as tocadas | destinos e envio | idênticos antes e depois, por papel | `acoes-antes.json` × `acoes-depois.json`; V 13, 14 |
