# 4. Plano de implementação em entregas pequenas

Cada entrega é verificável sozinha e para em pé sem a seguinte. As cinco primeiras não dependem de
autorização normativa nova: põem no GPS o rito que o Ifes **já pratica**. O vídeo começa na sexta, e
roda só em desenvolvimento até haver protocolo.

| # | Entrega | Depende de | Como se verifica | Tamanho |
|---|---|---|---|---|
| **0** | **Prova de conceito isolada** (página estática, dados sintéticos, sem servidor do GPS) | nada | matriz de navegadores: grava, revisa, regrava, mede tamanho e formato, calcula o hash | pequeno |
| 1 | **Alcance da Etapa por Modalidade** (L-2) | decisão P-1 | Etapa com alcance L2 só distribui, consolida e mostra no portal quem declarou L2; snapshot e mutabilidade com guardião | médio, com migration e degrau do snapshot |
| 2 | **Efeito por lista** do desfecho desfavorável | 1, P-2, QC4 da concorrência concomitante, 158 | não confirmada sai da reservada, fica na ampla; ordem, corte e ocupação recalculam; ELIMINAR continua possível | médio a grande: toca ordem e ocupação |
| 3 | **Deliberação colegiada decisória**: regra de combinação, parecer às cegas, motivo | 1, P-3 | painel de 3 com unanimidade: 3 favoráveis confirmam, 2×1 não confirma; parecer alheio invisível antes do próprio | médio |
| 4 | **Orientação**: degrau no portal, natureza no Centro e em Minhas atividades, aviso por e-mail | 1–3 | percurso no navegador nos cenários de treinamento; varredura de vocabulário | médio, sem modelo |
| — | *Aqui a heteroidentificação do rito atual está no GPS. A entrevista continua na RNP; a comissão registra no sistema.* | | | |
| 5 | **Vídeo, lado do candidato**, atrás de `VERIFICACAO_POR_VIDEO` (recusada em produção) | 4, entrega 0 | grava, revisa, envia em partes retomáveis; comprovante com hash; CSP com `media-src 'self' blob:` só nessa página; `Permissions-Policy` só nela | médio |
| 6 | **Vídeo, lado da comissão**: Mesa com `<video>`, entrega mediada com `Range`, trilha de abertura, encaminhamento à entrevista | 5 | só o alocado com Atribuição abre; 1 evento por abertura; R-11 impede "não confirmada" pelo vídeo | médio |
| 7 | **Retenção** do arquivo de vídeo | P-10 | comando com prazo conferido, hash e trilha preservados | pequeno |
| 8 | **Piloto controlado** | protocolo aprovado (P-0), Edital que o cite | só depois de aprovação específica: chave liberada em produção por PR revisado, para um Edital | — |

## A prova de conceito (entrega 0)

> **Construída em 13/11.** O resultado está em [poc/README.md](poc/README.md). O que segue é o desenho
> original. A diferença é uma só: a página ganhou uma imagem de teste sintética, para ser
> verificada sem câmera e sem gravar ninguém.

**O que ela responde**: se a captura no navegador serve ao rito, em celulares reais, antes de gastar
uma linha no GPS.

**Como é isolada**:
- uma página HTML estática em `doc/estudo-verificacao-da-autodeclaracao-2026-11-13/poc/`;
- nenhuma rota, modelo ou dependência no `backend/`;
- nada sai do aparelho: o "envio" calcula o SHA-256 e mostra o comprovante simulado;
- quem a testa grava a si mesmo, ou uma imagem de teste, e o arquivo é descartado ao fechar a aba;
- nenhum candidato real, nenhum vídeo real.

**O que ela mede**, por navegador (Chrome e Firefox no computador, Chrome no Android, Safari no
iOS):
- formato que o `MediaRecorder` produz (WebM/VP8–VP9 ou MP4/H.264);
- tamanho por minuto em 720p a ~1 Mbit/s;
- se o vídeo gravado num navegador toca no navegador da comissão;
- câmera frontal em retrato;
- permissão negada e reconcedida;
- leitura do roteiro pelo VoiceOver e pelo TalkBack;
- o que acontece quando a tela apaga no meio da gravação.

**Como roda**: `getUserMedia` só funciona em contexto seguro. Funciona em `localhost` no computador.
No celular, precisa de HTTPS: a VM de testes serve, ou um túnel. A entrega 0 escolhe uma via e a
registra.

**Critério de saída**: a matriz preenchida. Ou o vídeo é viável nos quatro navegadores, ou a lista
do que não é viável vira restrição da entrega 5. Exemplo: "no iOS, só a partir da versão X".

## Riscos técnicos já visíveis no código

- **Tamanho.** Os uploads aceitam só PDF até 10 MiB (`shared/arquivos.py:56`,
  `ARQUIVOS_CANDIDATOS_LIMITE_BYTES`). O nginx limita `/selecoes/` a 12 MB, e o gunicorn é síncrono
  com 120 s. Dois minutos de vídeo a 1 Mbit/s dão ~15 MB. O envio em partes de ≤ 8 MiB resolve os
  três sem mexer nos limites globais.
- **CSP.** `shared/politica_de_conteudo.py` não declara `media-src`, que herda `default-src 'self'`.
  A prévia local do vídeo (`blob:`) seria recusada em silêncio, e a única pista é o console, como em
  todo caso de CSP deste projeto. A exceção vale só para a página de gravação.
- **Entrega mediada só de PDF.** `portal/arquivos.py` entrega o arquivo inteiro com
  `application/pdf`. Vídeo pede `Range` (sem ele, o `<video>` não avança nem volta no Safari) e
  registro de **uma** abertura por reprodução, e não por pedaço.
- **Integridade do "sem filtro".** O navegador não sabe se a câmera é virtual (OBS) ou se o sistema
  do celular aplica embelezamento. O GPS garante tomada única e sem edição **na página**, e não a
  ausência de filtro na origem. A garantia real é a R-11: na dúvida, ao vivo. Isto vai escrito no
  protocolo, e não prometido na tela.
