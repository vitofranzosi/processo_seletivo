# Baseline sintética planejada — não gerada

Identificador proposto: `f4-sintetico-v1`. Não há dump, volume, carga ou hash de baseline criada.
Referência: cenários P01/P06/P07/P15 da F4 e condições das oito ratificações.

## Manifesto necessário para aprovação

Commit/lock/imagens e versões; instante T0 e fuso; gerador/comandos e opções; IDs/números/ano;
atores e permissões; quantidade por entidade; origem fictícia de campos/arquivos; estados antes/
depois; sementes/ocorrências sintéticas; hashes de artefatos; operações persistentes previstas;
limites, responsável, aprovação e evidência de ausência de dados reais. Não preencher hashes antes
da geração ou declarar reprodutibilidade bit a bit de timestamps/UUIDs dinâmicos.

Reprodução pretendida: mesmos caminhos, regras, relações e resultados esperados para parâmetros
fixados; diferenças legítimas de relógio/IDs devem ser declaradas. `seed_demo` usa relógio simulado
para alguns atos: registrar o deslocamento e não confundir com data histórica de certame real.

## Cobertura das dez famílias

| Família | Conteúdo planejado / fonte reutilizável | Critério e limitação |
|---|---|---|
| 1 Processo | Código institucional sintético exclusivo, título marcado; seed ou fixture seleção | Sem carga de Processo real; separar processos quando cenários não compartilham estados |
| 2 Edital | Casos em elaboração, homologado, publicado e retificado | Número/ano válidos para gerador; não usar número ocupado ou prefixo textual onde só aceita dígitos |
| 3 Eventos/períodos | Aberto, futuro, cancelado e substituído, uma designação válida | P01-A/B/C; preservar evento antigo; T0/datas parametrizados |
| 4 Retificações | Cancelamento, redesignação, operação/normalização, método e fundamento | Comando real com atores segregados; sem reescrever publicação |
| 5 Perfis/Modalidades | Dois Perfis, modalidades independentes e código transversal; regra com fundamento fictício | P07 e .08; dois significados independentes não pressupõem catálogo global |
| 6 Inscrições | Rascunho/enviada, antes/depois de Retificação e negativas de permissão/escopo | Fixtures candidato/seleção; identidades fictícias, nunca importar cadastros |
| 7 Documentos | Obrigatório/facultativo/não aplicável, recorte exato/transversal e arquivo com marca sintética | Lista congelada por envio, chave estável; sem documento pessoal real |
| 8 Pontuação/classificação | Notas sintéticas, ordem, obsolescência e sucessor; dependentes de corte/recurso/convocação | Fixtures resultado/recursos/ocupação; não afirmar que seed cobre todas as condições |
| 9 Sorteio | Sem método histórico, método declarado, relação congelada e tentativas por fase | Fonte de demonstração; sem Caixa/OpenRouter; casos com ordenação existente isolados |
| 10 Atos/auditoria | Publicação original, Retificação, versões, eventos e geração de matrícula | Dataset privado sem valor oficial; verificar IDs/hashes e ausência de mutação histórica |

Matrículas incluem Requerimento enviado e dados fictícios suficientes às 34 colunas, agregado,
lacuna nominal e erro; deficiência/raça/renda são valores inventados, não atributos de participantes.
E-mail somente no coletor local. CPFs de fixture são sintéticos e usados apenas para formato;
não alegar que uma sequência numérica prova inexistência de titular real. Não pesquisar pessoas
para validar dataset: evitar qualquer vínculo entre esses valores e participantes.

## Estratégia de preparação, a escolher

**A — cluster novo + esquema + carga autorizados:** preparação documentada, provisionar papéis,
migrar e provisionar novamente; unidades/autoridades e dados sintéticos em etapas explícitas.
Necessita autorização futura de cada escrita/esquema. É viável pelo código existente, mas não foi
executada. Não herdar autorização da F4, que excluía migrations.

**B — artefato sintético previamente preparado:** aceitar somente com manifesto, procedência,
hash, versão e teste de restauração autorizado em recurso novo. Nenhum foi localizado/comprovado
nesta inspeção; não recorrer a dump de desenvolvimento para preencher a lacuna.

Seed existente pode servir à navegação de base; complementos devem ser desenhados com helpers
existentes/API ou roteiro manual, sem adicionar regra funcional. `seed_demo` produz múltiplos
atos e não permite inferir cobertura dos cenários negativos. Primeiro revisar opções/efeitos,
aprovar contagens, executar uma vez por namespace e preservar resultados. Complemento novo como
runner não é criado nem autorizado aqui; exige revisão antes de executar.

Limites propostos da F4: até 20 Editais, 100 inscrições e 5000 eventos novos na execução, sujeitos
à confirmação após inventário da carga. Se o seed exceder ou não for mensurável antes, não executá-lo
sob aquele teto; reduzir o escopo por decisão ou preparar carga menor para aprovação. Não apagar
atos para caber no limite. Banco da suíte é separado da baseline interativa.
