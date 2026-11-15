# Data Model: O polimento das telas do candidato na verificação por vídeo

Nenhuma tabela, coluna, migration ou estado persistido. O vídeo, o envio, as marcas, a versão do
roteiro e a trilha da `166` ficam exatamente como estão (FR-7887).

## O único acréscimo, em memória

### `Situacao` (`verificacao/application/disponibilidade.py`)

| Campo | Tipo | Origem | Uso |
|---|---|---|---|
| `modalidade` | `str`, padrão `""` | `alcance.nome_da_modalidade(conteudo, inscricao.profile_id, inscricao.modality_id)`, em `envio.contexto_do_titular` | a frase "Você se inscreveu em {modalidade}" na escolha, no lugar do texto fixo (FR-7853) |

Vazio quando a Modalidade não tem nome nem código no conteúdo vigente; a frase, então, cai para "Quem
se inscreveu na sua lista passa também por esta etapa", a mesma regra do degrau da `171`.

## O que as telas leem, sem mudança

| Fonte | O que a tela usa |
|---|---|
| `Situacao.estado`, `inicio`, `fim`, `video`, `eliminado_em`, `nome_da_etapa` | o estado, o prazo, o comprovante, a frase da eliminação, o título |
| `roteiro.PASSOS`, `roteiro.VERSAO`, `roteiro.TETO_SEGUNDOS` | os títulos e as instruções do palco, a versão enviada, o teto declarado |
| `VideoDaVerificacao.duracao`, `formato`, `sha256`, `id`, `recebido_em` | a confirmação e os dados para conferência |
| `Passo` de `portal/passo_da_etapa.py` | o degrau do acompanhamento (a `171`), com o prazo em campo próprio |

## Estado da página no aparelho (script, não persistido)

| Estado | Telas | Transição |
|---|---|---|
| escolha | `escolha`, `ao-vivo` | "Gravar um vídeo curto" → preparo |
| preparo | `acolhimento`, `menor` | "Continuar" com 18 anos ou mais → palco (abre a câmera); menos de 18 → `menor` |
| palco · preparo | `palco` com `data-estado="preparo"` | câmera concedida; "Começar a gravar" → palco · gravando; recusa → `permissao` |
| palco · gravando | `palco` com `data-estado="gravando"` | "Próximo" × 3, "Terminar a gravação" → revisão; página escondida → palco · preparo com o aviso (a FR-7115 da `166`); "Parar e recomeçar" → palco · preparo |
| revisão | `revisao` | "Enviar este vídeo" → envio; "Gravar de novo" → palco · preparo |
| envio | `envio` | concluído → comprovante (outra página); três falhas → sugestão da entrevista |

O pedido de tela acesa vale nos dois estados do palco e é solto nas outras telas (T-004).
