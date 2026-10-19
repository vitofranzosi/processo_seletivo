# Fase 3 — instrução de pendências e preparação da homologação

Data: 16/10/2026. Base: `001-decisoes-pendentes` @ `6fc3a85a`.
Referência de decisões: [consolidação da Fase 2](../fase-2-consolidacao-dec-15.md).

**FASE 3 — EVIDÊNCIAS PREPARADAS; DECISÕES PENDENTES DE RATIFICAÇÃO.**

## Entrega

- [Dossiê técnico](dossie-tecnico.md): DEC-15.01, .06, .07 e .15.
- [Dossiê institucional](dossie-institucional.md): consultas .04, .12 e .13, não enviadas.
- [Plano DEC-14 e proposta de protocolo .16](homologacao-e-protocolo.md).
- [Matriz de evidências, dependências e limitações](matriz-e-limitacoes.md): oito pendências.
- [Reprodutor em memória](reproduzir-em-memoria.py) e [resultado observado](resultado-em-memoria.json).

Legenda: **O** observado em execução pura; **L** constatado por leitura de código/histórico;
**H** hipótese a demonstrar; **R** recomendação; **D** decisão humana já registrada.
Ausência de erro específico não comprova publicação válida. Resultado de memória não equivale a
ato persistido, percurso de navegador, autorização administrativa ou homologação.

## Verificação realizada

Comando executado em `backend/`, sem fixtures de banco nos dois módulos selecionados:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/editais/test_publicacao_com_periodo_cancelado.py tests/contract/test_elevacao_degrau_10.py -q -p no:cacheprovider
```

Resultado: **11 passando em 0,51 s**. Não houve preparação de banco de teste ou migrations; a
fixture autouse de unidades só usa banco quando o caso requer banco. Não é suíte PostgreSQL nem
evidência de produto em SQLite: estes são testes puros de conteúdo em memória.

Da raiz do repositório foi executado:

```powershell
backend/.venv/Scripts/python.exe doc/saneamento-2026-10-16/fase-3/reproduzir-em-memoria.py --salvar
```

O script bloqueia `BaseDatabaseWrapper.ensure_connection` antes de inicializar Django e usa
estruturas sintéticas em memória. `--salvar` grava somente JSON documental novo, sem sobrescrever.
Para reproduzir sem gravar outro arquivo, omitir `--salvar`. Não é código funcional da aplicação.

## Limitações e autorizações ainda necessárias

Nenhum banco, dado real, serviço externo ou API paga foi acessado. Nenhum fluxo de publicação,
geração de arquivo com trilha, sorteio ou seed foi executado em banco. Sem migrations, alteração
funcional, spec, Constituição, permissões, commit, push, merge ou envio de consulta.

Os cenários completos exigem persistência de atos, inscrições e auditoria. Por restrição expressa
do usuário, seus procedimentos estão preparados no dossiê, aguardando autorização específica.
Não se pede execução de migrations sob esta autorização; se ambiente previamente preparado não
estiver disponível, a demonstração completa fica pendente ou exige autorização nova para preparação.

**Nenhuma nova regra foi ratificada nesta Fase 3.** Mantêm-se as oito ratificações delimitadas da
Fase 2; as oito pendências instruídas aqui continuam sujeitas às decisões humanas indicadas.
