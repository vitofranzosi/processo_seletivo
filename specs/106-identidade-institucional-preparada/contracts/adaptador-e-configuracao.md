# Contrato: adaptador institucional, rotas e configuração

## O adaptador (FR-3022 a FR-3024)

Uma classe, apontada por `GESTAO_PROVEDOR_INSTITUCIONAL` (caminho pontuado), instanciada sem
argumentos.

```text
nome: str                              # vai a IdentidadeExterna.provedor; não muda depois de usado
apenas_para_testes: bool = False       # produção recusa a classe que o declare verdadeiro

iniciar(request, *, retorno: str, estado: str) -> HttpResponse
    # a ida ao provedor; tipicamente um redirecionamento que leva `estado` e volta a `retorno`

concluir(request, *, estado: str) -> IdentidadeAutenticada | None
    # o retorno. Valida o que o protocolo exigir (assinatura, emissor, audiência, nonce,
    # validade) e devolve a identidade, ou None. Nunca lança por credencial ruim.

IdentidadeAutenticada(provedor: str, identificador: str, nome: str, email: str)
```

**O que a gestão garante em volta do adaptador:**

- o `estado` é criado pela gestão, guardado na sessão e conferido no retorno **antes** de chamar
  `concluir`; é descartado na conferência, e por isso não vale duas vezes;
- `IdentidadeAutenticada.provedor` precisa ser o `nome` do adaptador configurado;
- nada do pedido além do que `concluir` devolve vira identidade.

## Rotas (D-012)

| Rota | Método | Resposta |
|---|---|---|
| `/gestao/entrar/institucional` | GET | a de `iniciar`; sem provedor, 503 com a página de entrada não configurada |
| `/gestao/entrar/institucional/retorno` | GET | 302 ao destino pedido ou à Lista; estado ausente, divergente ou repetido, ou `concluir` vazio: 403 pela recusa do domínio; sem provedor, 503 |
| `/gestao/unidade-ativa` | POST | 302 à Lista; sem vínculo vigente no escopo pedido: 403; sem sessão institucional: 403 |

A página `/gestao/identificar` ganha o botão "Entrar com a conta institucional" **só** quando há
provedor. Sem ele, o HTML é o de hoje.

## Configuração por ambiente (FR-3026 a FR-3028)

| Variável | Desenvolvimento | Homologação | Testes | Produção |
|---|---|---|---|---|
| `INTERFACE_SELETOR_IDENTIDADE` | `true` | `true` | ligado por *fixture* | **recusado** no *boot*; ignorado em execução |
| `GESTAO_PROVEDOR_INSTITUCIONAL` | vazio | vazio, até haver provedor de homologação | o simulado, por `settings` | **obrigatório para abrir a gestão**; vazio mantém 503 |
| `AUTHENTICATION_BACKENDS` | o institucional | o institucional | o institucional | só o institucional, ou recusa |

Recusas de produção, cada uma nomeando a variável:

1. seletor ligado (já existia);
2. provedor que não se importa;
3. provedor em `tests.` ou com `apenas_para_testes`;
4. `AUTHENTICATION_BACKENDS` diferente de só o institucional.

## Comando de implantação (FR-3029)

```bash
ps-manage conceder_administracao_institucional --provedor P --identificador X --motivo "Portaria nº …" [--nome N] [--email E] [--adicional]
```

Cria a pessoa e a identidade externa se não existirem, concede `administrador-institucional` no
escopo `institucional`, grava `ACESSO_CONCEDER` sob o ator `implantacao`. Recusa sem motivo; recusa
quando já há administrador institucional vigente e `--adicional` não foi dado; recusa quando a
pessoa já o tem.
