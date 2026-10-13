# Alterações da rodada 4 (2026-10-11) — consolidação

Rodada pedida depois de uma revisão das conclusões e das narrativas da rodada 3, com autorização para baixar e
consultar os documentos públicos listados. Não amplia o catálogo (continuam 316 identificadores), não inventaria
integralmente editais novos, não implementa funcionalidade, não recorta nem republica vídeos.

## 1. Fidelidade e cobertura

| Antes (rodada 3) | Depois (rodada 4) | Onde |
|---|---|---|
| O cabeçalho em imagem foi transcrito com “·” entre blocos de linhas e, depois, sem os “·”, para que casasse com o cabeçalho do sistema e a unidade LIB-0001 ficasse `EXATA` | Três registros separados: **transcrição fiel**, linha a linha, conferida contra a página renderizada; **normalização**, a mesma de toda linha, que é a que entra na comparação; **equivalência**, avaliada à parte. As palavras eram as mesmas; o método estava errado, e o erro está registrado no código | `ferramentas/linhas.py` (`IMAGENS`), `ferramentas/corpus.py`, `ferramentas/gerar.py` |
| 28/2026: “nas páginas seguintes, só o brasão” | a imagem com texto está só na página 1; as demais não têm cabeçalho; há um brasão sem texto na página 19 (Anexo III), registrado na linha E28-186 | `linhas.py` |
| 59/2026: a imagem “repete-se em 9 das 11 páginas”, com uma linha só | a imagem está nas páginas 1 e 9; a da página 9 (Anexo I) ganhou linha: **E59-090a** (sufixo para não renumerar as linhas que as narrativas citam). O 59/2026 tem 108 linhas de cobertura | `linhas.py`, `editais/edital-59-2026/cobertura.md` |
| — | conferência das imagens dos dois PDFs por `pdfimages -list`: no 28, páginas 1 e 19; no 59, páginas 1 e 9. Nenhuma outra imagem | manifestos |

## 2. Métricas e conclusões

| Antes | Depois | Onde |
|---|---|---|
| “Idêntico a simulado: 0% e 1%”, apresentado como prova de que o texto do sistema não reaparece | a medida foi nomeada pelo que é: linha idêntica a alguma linha simulada **da mesma unidade**, contra **todo** o texto simulado, inclusive o texto livre da auditoria | `ferramentas/medir.py`, `viabilidade.md` §2.3 |
| — | medida nova, contra as **frases que o sistema gera** (as 97 linhas de origem C pura dos simulados), sem restrição de unidade: 0,0% por linha e por frase; 0,5% e 0,3% por função, com o limite da atribuição do catálogo escrito ao lado | idem |
| “a hipótese de reuso do texto do sistema não se confirma”; “o reaproveitamento de gravações só é discutível no texto da casa” | retiradas: as métricas descrevem coincidência literal em português, e não permitem concluir sobre sentido, tradução ou gravação | `viabilidade.md` (cabeçalho, decisão, §2.3, §4, §6), `auditoria-sistema.md` §1, manifesto do 28 |
| Critério do experimento: “se só a tradução contínua funcionar, a biblioteca não se justifica” | um resultado negativo registra os limites daquela tentativa; o experimento separa preparação, solução e gravação, e testa gravações de blocos de mesmo sentido com português diferente | `viabilidade.md` §8, `comparacao-focalizada/protocolo-profissional.md` |

A análise da rodada 3 está preservada em [`viabilidade-rodada-3.md`](viabilidade-rodada-3.md).

## 3. Versões

Baixados com autorização, com origem, data de consulta, bytes, SHA-256 e data de geração registrados: a Retificação e
o Comunicado do 28/2026 e os seus seis anexos à parte; a Retificação e o Comunicado do 59/2026 e os seus dois anexos à
parte; os editais 19/2026 e 46/2026 e as três erratas do 46. As cópias do Drive e do `publicacoes.ifes.edu.br` dos
editais consolidados do 28 e do 59 eram **idênticas** às já inventariadas, e foram descartadas.

Achados:

- **28/2026:** a Retificação nº 01 (21/07) passou as vagas de 280 para 420 (60 por polo); a consolidada de 24/08 **não
  a incorporou**. O Comunicado de 24/08 mudou o início de 24/08 para 01/09 e acrescentou a aula inaugural; a
  consolidada o traz.
- **59/2026:** a Retificação (30/07) mudou os Eventos 7, 8 e 11; a consolidada, cinco horas anterior, traz o 7 e o 8 e
  **não** o 11. O Comunicado de 27/07 registra que **não houve sorteio**. A página do processo informa prazo de recurso
  e data de resultado diferentes dos do Cronograma.
- **46/2026:** o arquivo do link “edital de 03/08” é uma versão de 14/09, com as erratas; a original não está
  disponível. O vídeo em Libras (11/07) é anterior à publicação.

Arquivos: [`../editais/edital-28-2026/retificacoes.md`](../editais/edital-28-2026/retificacoes.md),
[`../editais/edital-59-2026/retificacoes.md`](../editais/edital-59-2026/retificacoes.md),
[`../comparacao-focalizada/fontes.md`](../comparacao-focalizada/fontes.md).

## 4. Narrativas

| Antes | Depois |
|---|---|
| Pendências só nas ambiguidades; respostas esperadas fechadas, inclusive onde a mesma narrativa registrava a questão aberta (o recurso contra o sorteio no 59/2026 tinha a resposta “Não”) | cada enunciado tem um campo de **pendência** (13 dos 86 enunciados reais) e a lista dos **documentos fora da versão inventariada** que o mudam; cada pergunta tem **estado** — 21 *definitivas*, 13 *com pendência* — e a pergunta com pendência não tem gabarito fechado |
| Datas da versão consolidada apresentadas como definitivas | as divergências entre a consolidada, os atos e a página do processo entram no enunciado e na resposta (prazos de recurso do 28 e do 59; início do 59; vagas do 28) |
| — | dois acréscimos: uma pergunta sobre as vagas do 28/2026, e o enunciado CLA-59-12 (não houve sorteio) |

Nada da rodada 3 se apagou: as mudanças estão num bloco próprio no fim de `ferramentas/narrativas.py` e no
*Histórico* de cada narrativa gerada. O mapa de cada edital passou a distinguir **cobertura documental**, **narrativa
preparada** e **tradução validada**.

## 5. Comparação focalizada (novo)

[`../comparacao-focalizada/`](../comparacao-focalizada/README.md): Eliminação e Inscrição, por situação comunicativa,
com 19/2026, 46/2026, 28/2026 e 59/2026; o mapa das seções dos três vídeos, lido do rótulo na tela; e o protocolo para
os profissionais de Libras. O achado que justifica o pacote: no §9 dos editais técnicos, doze alíneas idênticas e uma
— a **g**, “nota zero em uma ou mais disciplinas” × “em todas as disciplinas” — com regra oposta.

## 6. Ferramentas

Novas: `comparar_anexos.py`, `comparar_secoes.py`, `rotulos_de_video.js`. Alteradas: `corpus.py` (linhas de imagem
inseridas com `depois_de`), `linhas.py`, `gerar.py` (transcrição fiel no roteiro), `medir.py` (as três comparações
com conjunto, denominador e limites), `narrativas.py` e `narrar.py` (pendência e estado). `ruff check` e `ruff format`
limpos.

## Pendências e responsáveis

| Pendência | Responsável |
|---|---|
| Vagas vigentes no 28/2026: 420 (Retificação nº 01) ou 280 (consolidada e item 4.1) | área responsável pelo processo seletivo do Cefor |
| Início do curso no 59/2026: 24/08 (Retificação) ou 10/08 (consolidada) | idem |
| Prazos de recurso que a página informa diferentes do Cronograma (28: 05/07 × 06/07; 59: 02/08 × 03/08) | idem |
| O ano “2025” no Cronograma do 28/2026, em todas as versões | idem |
| Nome e nível do curso no 59/2026 | idem |
| A versão original do 28/2026 (07/04), para delimitar o que o vídeo traduz | idem, e a equipe de produção de vídeos do Cefor |
| A versão que o vídeo do 46/2026 traduz | área responsável pelos processos seletivos técnicos do Ifes, e a produção do Cefor |
| A alínea g do §9 do 46/2026 | área responsável pelos processos seletivos técnicos do Ifes |
| Equivalência de regra das situações G1, G2 e G4 do protocolo | áreas responsáveis pelas regras de cada edital |
| Alcance das proibições de recurso e vias fora do edital (Lei nº 9.784/1999) | área jurídica |
| Tradução das Retificações em Libras (LBI, art. 30, VII) | área jurídica e coordenação de Libras |
| Fases 1 e 2 do protocolo; terminologia | profissionais de Libras, com a comunidade surda na terminologia |
| Autorização para recorte e recomposição dos vídeos (CC BY-NC-ND) | Cefor/Ifes |
| Fase 3 do protocolo | profissionais de Libras e participantes surdos |
