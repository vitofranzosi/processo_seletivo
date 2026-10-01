# O "vaga(s)" que a 057 não trocou

**Data:** 2026-09-30
**Origem:** implementação da `057` (polish das telas de operação), item F8 da
[auditoria de polish](auditoria-polish-ui-2026-09-30.md).
**Natureza:** registro do que ficou de fora de propósito. Não é defeito novo, e nada aqui virou
escopo.
**Situação:** **aberto** — decidir se, quando e como é do usuário.

## O que a 057 trocou

O F8 pedia números, datas e plurais como uma pessoa os escreve, **só no texto que a interface compõe
para ser lido na tela** (7ª decisão recebida da `057`). Trocou-se, em `interface/`:

- `revisao.py`: percentual, Peso, Nota mínima e Pontuação máxima sem zeros à direita; a versão da
  norma em dd/mm/aaaa; "vaga(s)" e "nesse(s) recorte(s)";
- `supervisao.py`: o "vaga(s) imediata(s)" da mensagem do sinal de acervo sem quadro;
- `conducao_do_marco.py`: "vaga(s) publicada(s)" e "posição(ões) divulgada(s)", que só a
  conferência do gesto lê;
- `retificacao.py`: as duas linhas "N vaga(s)" do resumo de acréscimo, que só a conferência mostra.

## O que ficou, e por quê

### Sai da tela

- **`retificacao.objeto_legivel`** — "Admite recurso em N dia(s) corrido(s)" e "N vaga(s)". Além da
  tela de detalhe da Retificação, a função alimenta `aplicacao_na_retificacao._legivel`, cuja saída
  vai para a impressão de cada destino do gesto, e `aplicacao_na_retificacao.registro` grava essa
  impressão no registro do ato. Mudar a grafia mudaria o que os atos novos gravam ao lado dos antigos.
- **`editais/domain/validation.py`** — "publica N vaga(s) imediata(s)" em quatro mensagens de
  pendência (l. 3074, 3126, 3163 e 3230). São do domínio, e não da interface: a mesma mensagem é a
  que a publicação recusa ou adverte. Fora da lista do F8.
- **`ocupacao.html`, l. 207** — "O déficit apurado de N vaga(s) será a causa do ato". A frase
  anuncia o motivo que o ato grava (`test_causar_faixa.py` confere `continuacao.motivo`); trocar só a
  tela faria ela prometer um texto e o ato gravar outro.

### Valor enviado por formulário

- **Os campos numéricos da etapa Etapas** (Peso, Nota mínima, Pontuação máxima) recebem o valor
  gravado, `2.0000`, que o navegador mostra como "2,0000". Escrever `2` no atributo mudaria o valor
  que o "Salvar rascunho" envia, e a 7ª decisão exige o POST das etapas idêntico.

### Fora da lista do F8, na tela

Templates que compõem plural com parênteses e que o F8 não nomeava: `distribuicao.html`
("consolidada(s)", "recusada(s)"), `ocupacao.html` e `ocupacao_historico.html` ("Reversão de cota:
N vaga(s)"), `matriculas.html` ("linha(s)") e `recurso.html` ("ato(s) de instrução"); e
`compor_base.html`, l. 70, preso por `test_compor_quadro.py`.

## Testes ajustados pela troca

Sete asserções prendiam a grafia antiga do texto que a 7ª decisão manda trocar, e foram reescritas
para a nova, sem mudar o que verificam: `test_revisao.py` (três), `test_advertencias_do_quadro.py`,
`test_retificar_modalidade.py`, `test_sinal_do_acervo_sem_quadro.py` e
`test_us1_declaracao_unica_de_vagas.py`.
