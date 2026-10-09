# Verificação — 066 · Avisos complementares aos candidatos

*Percurso pela interface do ator (Princípio VI), em 09/10/2026, no servidor local `avisos-066` (porta
8066, banco `ps_demo_066` preparado com `make preparar` e `seed_demo`, correio de console). Os casos
que precisam de servidor de correio simulado — falha, queda, concorrência, interrupção no meio do
envio — são provados pela suíte, e estão na [rastreabilidade](rastreabilidade.md).*

## 1. Resultado, pela tela (US1)

| Passo | O que se viu |
|---|---|
| `make preparar` | `40 de 40` tabelas protegidas e `Modelos de aviso: 3 criados`; na segunda passada, `0 criados` |
| Entrar como `vera.publicadora` (papel Publicador) | o seletor lista `aviso:enviar` no Publicador e no Gestor, e em nenhum outro papel |
| Resultados divulgados do marco "Classificação final" do Edital 51/2026 | seção "Avisar candidatos", com "Nenhum aviso enviado sobre este marco." e o botão "Avisar candidatos — resultado preliminar" |
| A prévia | "Esta é uma prévia: nada foi gravado"; a origem por extenso, "As inscrições consideradas no resultado preliminar de Classificação final, em 1 publicação"; **4** com endereço e **0** sem; o modelo "Divulgação de resultado" escolhido; a orientação do assunto; as dez variáveis com o significado; o rodapé fixo; a mensagem como sai para **Ana Silva**, com o link da publicação no rodapé |
| "Enviar a 4 pessoas" | o histórico do aviso: "Aviso confirmado para 4 pessoas. O envio começa no próximo minuto", **4 — pendente**, o texto congelado com `{nome_do_candidato}` por resolver, e "editar o modelo não muda este aviso" |
| `manage.py despachar_avisos` | quatro mensagens no terminal do comando, cada uma com um `To` só e `Auto-Submitted: auto-generated`; o assunto vem codificado e dobrado, como todo cabeçalho com acento |
| O histórico, recarregado | **4 — aceita pelo servidor de correio**. Em lugar nenhum "entregue", "recebida" ou "lida" |

**SC-485.** Do clique em "Avisar candidatos" ao histórico do aviso confirmado: **~68 s**, partindo do
modelo inicial, sem editar o texto. O percurso foi automatizado, e não feito por uma operadora que
nunca viu a tela; a medida com pessoa é do teste com usuário que a Lei 15.263 pede, e fica para ele.

## 2. Largura de 375 px

Medida por `iframe` de 375 px com o HTML de cada tela, comparando `scrollWidth` e `clientWidth`:

| Tela | `scrollWidth` × `clientWidth` |
|---|---|
| Histórico do aviso | 371 × 371 |
| Prévia (reenvio justificado, com justificativa) | 371 × 371 |
| Avisos do Edital | 371 × 371 |
| Modelos de aviso | 371 × 371 |
| Interromper | 371 × 371 |
| Resultados divulgados do marco (com a seção nova) | 371 × 371 |

Nenhuma rolagem horizontal. Console sem erro; log do servidor sem erro.

## 3. Ajustes que a verificação produziu

- **O rodapé e os modelos iniciais perderam as quebras de linha fixas.** Na caixa da prévia, a quebra
  em ~80 colunas deixava palavra sozinha na linha seguinte ("prazos / e"). No e-mail, quem quebra a
  linha é o leitor, na largura da tela — e a do celular é mais estreita que 80 colunas.
- **Os botões ganharam respiro** (`.botoes-do-aviso`): "Usar este modelo" e "Atualizar a prévia"
  encostavam no bloco seguinte.
- **O banco de demonstração ficou com os modelos iniciais da versão anterior**, com as quebras: o
  sistema não os sobrescreve, como a `FR-1260a` manda. É o comportamento pretendido, visto ao vivo.

## 4. O que esta verificação não cobre

- **Servidor de correio real.** Nada aqui saiu da máquina, e nada deve sair antes da validação de LGPD
  e do limite da conta institucional (`D-009`, runbook §16.4).
- **A chamada por publicação pela tela.** O `seed_demo` convoca por mensagem individual; o caminho por
  publicação está provado pela suíte (`test_aviso_da_chamada.py`, inclusive a tela da convocação).
