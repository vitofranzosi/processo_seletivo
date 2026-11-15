# Implementation Plan: A detecção do giro do rosto na gravação do vídeo

**Branch**: `claude/176-deteccao-do-giro-do-rosto`, sobre a `main` em `34e5f8bd` | **Date**: 2026-11-15
| **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/176-deteccao-do-giro-do-rosto/spec.md`, com as respostas
Q-1 a Q-4 do usuário (as recomendações).

## Summary

Comportamento no aparelho, e nada no servidor além da chave e da política de conteúdo.

1. **O motor, servido pela própria origem.** Três arquivos do `@mediapipe/tasks-vision` 1.2.0 e o modelo
   dos pontos do rosto, sem alteração, em `portal/static/portal/deteccao/`, com o manifesto de resumos
   em `portal/deteccao.py` e o teste que os confere (T-001, T-002).
2. **`deteccao.js`, um script novo do portal.** As funções puras — o giro a partir dos pontos, o rosto
   no oval, a decisão do giro mantido, o orçamento — e a ligação com o motor: carregar depois da
   câmera, ler a cada 150 ms só no preparo e nos perfis, desligar quando passa do orçamento ou quando a
   pessoa escolhe o toque (T-003, T-005 a T-008).
3. **`gravacao.js` consome a detecção, se houver.** Quatro ganchos: o palco aberto (começar a ler), o
   passo mudou (ler ou não), o giro visto (confirmar e chamar o mesmo `avancar()`), a saída do palco
   (parar e soltar). Sem a detecção, nada muda nele (FR-8016, SC-2751).
4. **A página.** A frase do que a tela faz e "Prefiro avançar só tocando" no topo do preparo, o estado
   do oval, a linha de confirmação sobre a instrução — tudo `hidden` até a detecção estar pronta; a
   política com `'wasm-unsafe-eval'` só com a chave (T-004); a chave em `settings`, recusada em
   produção (T-009).
5. **A imagem de teste gira**, e a detecção simulada lê o giro desenhado (T-010).
6. **A prova.** As funções puras no `node --test`; o manifesto, o guardião, a política e a página no
   pytest; a jornada no navegador com o motor de verdade (carrega sem violar a política, sem rede de
   fora) e com a imagem de teste (avança sozinha nos perfis, mesmo corpo de envio) (T-011, T-012).

## Technical Context

**Language/Version**: Python 3.13, Django 5.2; JavaScript sem empacotador, como o resto do portal.

**Primary Dependencies**: uma nova, **no navegador**: `@mediapipe/tasks-vision` 1.2.0 (Apache 2.0) e o
modelo `face_landmarker` float16/1 (Apache 2.0), copiados, sem gerenciador de pacotes JS. Nenhuma
dependência Python nova; o guardião continua recusando visão computacional no lock.

**Storage**: nenhuma migration, nenhuma tabela, nenhum campo. O `M` da preparação não muda.

**Testing**: pytest contra PostgreSQL com `DB_NAME` próprio, rodando os diretórios que a mudança toca;
`node --test` para `deteccao.js` e `gravacao.js`; a jornada no navegador (`navegador`); a suíte
inteira uma vez, no fim.

**Target Platform**: o portal do candidato — Safari no iPhone (16.4+, pelo SIMD), Chrome no Android, e
os três navegadores do computador.

**Project Type**: aplicação web, backend com templates.

**Performance Goals**: palco no mesmo tempo com e sem a detecção (o motor fora do caminho); leitura a
6,7 por segundo, com teto de 120 ms por leitura; nenhuma consulta a mais na página.

**Constraints**: CSP sem `unsafe-inline` e sem `unsafe-eval`; `'wasm-unsafe-eval'` só na gravação e só
com a chave (FR-8022); nada da detecção sai do aparelho (FR-8000); os testes de envio da `166` e da
`174` sem mudança (FR-8030); tudo em português.

**Scale/Scope**: um script novo, um módulo Python pequeno, um template, uma folha, uma chave; quatro
arquivos copiados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como a feature o cumpre |
|---|---|
| I. Linguagem ubíqua | frases do candidato em "você", sem "biometria" nem "prova de vida" (FR-8006); os passos pelo título do roteiro |
| II. Integridade normativa e imutabilidade | o roteiro, a versão e as marcas não mudam; nada do conteúdo publicado, do vídeo nem da trilha muda (FR-8030) |
| III. Segurança, proteção de dados e auditoria | dado sensível tratado só na memória do aparelho, minimizado (só nos passos que precisam), sem envio nem guarda (FR-8000, FR-8001); a pessoa é informada e pode recusar (FR-8004, FR-8005); a exceção de CSP é a menor possível e só na gravação; a avaliação da LGPD é feita na spec e a validação fica com quem decide (P-13) |
| IV. Regras explícitas | o limiar, o instante e o orçamento num só lugar; a detecção nunca decide mérito, nunca bloqueia, e o toque vale em todos os passos (FR-8014) |
| V. Rastreabilidade e simplicidade | sem dado novo persistido; motor fixado por versão e resumo, conferido por teste; funções puras testadas fora do navegador |
| VI. Completude de jornada | do palco ao comprovante, com e sem a detecção, provado no navegador com o motor de verdade e com a imagem de teste |

**Gate: aprovado, com uma revisão de regra declarada.** A FR-7150 e a FR-7112 da `166`, a R-19 e a R-21
do estudo e a FR-7890 da `174` são revistas de forma estreita, por decisão do usuário (Q-1, Q-2; D-001,
D-002). Nenhum princípio da Constituição é excepcionado: o III pede necessidade, finalidade e
minimização, e o desenho as cumpre.

**Re-check depois do desenho: aprovado.** O desenho acrescentou uma chave, um parâmetro na política da
gravação e um script; nenhuma rota, permissão, tabela ou campo enviado.

## Project Structure

### Documentation (this feature)

```text
specs/176-deteccao-do-giro-do-rosto/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/pagina.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── config/settings/
│   ├── base.py                    # VERIFICACAO_DETECCAO_DO_GIRO (T-009)
│   ├── production.py              # a recusa (FR-8021)
│   └── test.py                    # desligada; os testes da 176 a ligam
├── processo_seletivo/
│   ├── shared/politica_de_conteudo.py   # com_midia_local(compilar_wasm=) (T-004)
│   └── portal/
│       ├── deteccao.py            # o manifesto do motor e o giro de cada passo (T-002)
│       ├── verificacao.py         # o contexto da página e a política
│       ├── templates/portal/verificacao.html
│       └── static/portal/
│           ├── deteccao.js        # as funções puras e a ligação com o motor (novo)
│           ├── gravacao.js        # os ganchos e a imagem de teste que gira
│           ├── portal.css         # o oval, a confirmação, o aviso
│           └── deteccao/
│               ├── tasks-vision-1.2.0/{vision_bundle.mjs, vision_wasm_internal.js, vision_wasm_internal.wasm, LICENSE}
│               └── face_landmarker-float16-1.task
└── tests/
    ├── javascript/deteccao.test.js          # novo
    ├── portal/test_deteccao_do_giro.py      # novo: manifesto, chave, política, página
    ├── test_sem_inferencia_sobre_o_video.py # o guardião ampliado (T-011)
    └── navegador/test_jornada_do_video.py   # dois casos novos (T-010, T-012)
doc/
├── verificacao-por-video-porta-do-piloto.md # a P-13 e a compressão (FR-8042)
└── deteccao-do-giro-2026-11/README.md       # o que foi medido (FR-8041)
```

**Structure Decision**: o motor é do portal, e só da página da gravação; por isso mora em
`portal/static/portal/deteccao/`, e o manifesto em `portal/`, e não em `verificacao/`, que é o domínio
do servidor e continua sem visão computacional.

## Complexity Tracking

| Exceção | Por que é preciso | Alternativa mais simples descartada |
|---|---|---|
| `'wasm-unsafe-eval'` na gravação | o motor é WebAssembly, e a compilação dele é bloqueada por `script-src 'self'` | nenhuma: sem compilar, não há motor; `'unsafe-eval'` abriria mais |
| 18 MB de arquivos copiados no repositório | o navegador precisa deles na própria origem, em todo ambiente | baixar na implantação: um passo a mais que pode falhar, e o mesmo arquivo servido |
