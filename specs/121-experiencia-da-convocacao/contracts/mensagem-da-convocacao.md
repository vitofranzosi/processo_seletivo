# Contrato: a mensagem individual de convocação

**Requisitos**: FR-3882 a FR-3890 · **Pesquisa**: R-001, R-002, R-005

## Onde mora cada parte

| Parte | Onde | Por quê |
|---|---|---|
| a escolha do modelo e da variante | `convocacao/domain/mensagem.py`, nova e pura | é chamada no envio e no teste de reconstrução (R-002) |
| os quatro arquivos de modelo | `convocacao/templates/convocacao/mensagem/{inicial,correcao}.{html,txt}` | o texto é arquivo versionado, e o resumo de cada par identifica a versão (R-009) |
| a montagem e o envio | `convocacao/application/comunicar.py`, que já é a situação declarada | o guardião de `tests/test_situacoes_de_mensagem.py` aceita `EmailMultiAlternatives` só nos quatro módulos declarados |
| a identificação do modelo | `identificacao_do_modelo`, em `convocacao/domain/mensagem.py`, sobre as fontes que renderizaram | R-009; gravada em `ComunicacaoEmitida.modelo_da_mensagem` |

Nenhum módulo novo envia. O guardião das quatro situações não muda (FR-3888, SC-1161).

## Entradas do envio

`enviar_mensagem_de_convocacao(para=, dados=)` continua a ser o ponto de envio. O dicionário `dados`
ganha três chaves; nada nele é dado pessoal. Ela passa a devolver, além do detalhe da falha, a
identificação do modelo que renderizou, para o comando gravá-la na `ComunicacaoEmitida`:

| Chave | Origem |
|---|---|
| `edital`, `vencimento`, `atendimento`, `assinatura` | como hoje |
| `processo` | o título do Processo, já carregado pelo `select_related` da convocação |
| `link` | a rota da convocação da inscrição, juntada à origem do `endereco_do_portal`, com recaída para o caminho relativo quando a base é vazia |
| `escolha` | o valor de `escolha_da_mensagem` (R-002) |

## Saída

Uma `EmailMultiAlternatives` com:

- **assunto** da tabela da FR-3884 ou da FR-3885, no máximo uma linha, começando por *"Ifes ·
  Convocação"*. A instituição sai de `Identificacao.instituicao` e de `nome_da_instituicao`
  (`unidades/application/identificacao.py`), e a unidade, de `Identificacao.sigla`. Nada disso é
  literal no modelo (FR-3887);
- **corpo em texto**: o modelo `.txt`, com o endereço completo do link;
- **alternativa** `text/html`: o modelo `.html`, com CSS só em `style` inline, sem `<style>` externo,
  sem `src=` e sem fonte remota. A CSP da aplicação não alcança mensagem de e-mail. Quem impõe estas
  regras é o teste da SC-1159.

## Invariantes verificadas

1. Toda frase do HTML está no texto (SC-1159), comparadas depois de remover a marcação e normalizar
   os espaços.
2. Zero `src=`, zero `http` fora do link e do canal, zero nome, CPF ou nome de documento da fixture
   (FR-3886).
3. Zero `HH:MM` no prazo, nas quatro variantes e nos dois modelos (SC-1155).
4. A da correção traz o quadro com o `enviado_em` e o `vencimento` da citada, e nunca o motivo, nem
   *"novo prazo"*, nem *"prorrogação"* (FR-3885).
5. A repetição com a mesma chave não renderiza nem envia (FR-3888).
6. Toda comunicação individual, `ENVIADA` ou `FALHA`, grava `modelo_da_mensagem` igual ao resumo das
   fontes que a renderizaram. A publicação grava `""`, e a mudança de um modelo não altera linha já
   gravada (SC-1172).
