# Quickstart: verificar a leitura do não publicado

## Automático

```bash
cd backend && make lint check test-pg
```

O que prova cada parte está na [rastreabilidade](rastreabilidade.md). Os três arquivos desta feature,
isolados:

```bash
cd backend && PYTEST_ADDOPTS="tests/publicacoes/test_leitura_do_nao_publicado.py tests/authorization/test_leitura_do_nao_publicado.py tests/authorization/test_papel_da_leitura_do_rascunho.py tests/test_rotas_do_nao_publicado.py tests/test_gramatica_das_portas.py" make test-pg PYTEST_WORKERS=0
```

## À mão (SC-1063, SC-1066)

Pré-requisitos: banco migrado e preparado (`make preparar`), `INTERFACE_SELETOR_IDENTIDADE=true`,
`seed_demo` aplicado — ele traz Edital publicado e Edital em elaboração.

1. **Uma Retificação em curso.** Como elaborador, abra "Retificar" num Edital publicado e submeta
   uma prorrogação. Anote o endereço do detalhe dela e o do detalhe e da prévia de um Edital em
   elaboração.
2. **Integrante sem vínculo.** Entre pelo seletor só com o papel de integrante (ou julgador).
   - A lista não mostra o Edital em elaboração nem a marca da Retificação.
   - Cole cada endereço anotado: todos respondem "não encontrado", com a mesma página de um
     identificador inventado.
   - O detalhe do Edital publicado abre, sem a seção de Retificações em curso.
3. **Presidência sem papel sistêmico.** Entre como a presidente da comissão do Processo do Edital
   em elaboração.
   - A lista mostra o Edital, sem ações de conteúdo; o detalhe é o reduzido.
   - A prévia responde a recusa explicada, com "Peça a alguém com a permissão de ler o Edital antes
     da publicação".
   - Comissão e alocações abrem como antes.
4. **Publicador.** Entre como publicador: a prévia, o PDF e os anexos do Edital homologado abrem;
   publique-o.
5. **Auditor.** A lista mostra o Edital em elaboração; a trilha dele abre; a prévia responde a recusa
   explicada.

Resultado esperado: nenhuma identidade dos passos 2 e 3 lê conteúdo não publicado; nenhuma jornada
dos passos 3 a 5 perde uma tela que tinha.
