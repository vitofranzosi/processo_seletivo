# Contrato: as superfícies do portal diante da convocação invisível

Incremento A (FR-3981 a FR-3990). **Invisível** é a convocação da FR-3981; **K-msg** continua como hoje.

| Superfície | Rota / leitura | Com a convocação invisível | Depois do registro |
|---|---|---|---|
| Minhas inscrições | `portal:inscricoes`, `_item_da_lista` | item sem convocação: sem indicação, ação *"Acompanhar"* (FR-1089, FR-1091 da `059`) | indicação e *"Ver convocação"* |
| Acompanhamento | `portal:acompanhamento` | sem seção *"Convocação"* (FR-1095 da `059`); sem obrigações da convocação | seção, com *"Publicada em ‹referência›"* |
| Tela da convocação | `portal:convocacao` | a de quem não tem convocação; *"houve convocação no recorte"* só com visíveis (FR-3984); sem leitura na trilha (FR-3983) | a chamada, com o prazo correndo |
| Endereço direto sem sessão | `portal:convocacao` | redireciona ao acesso, como hoje (FR-3876 da `121`): não lê nada antes do código | igual |
| Envio de documento | `portal:apresentar-documento-da-convocacao` → `documentos.apresentar` | `nao_encontrado()` no comando; nada gravado (FR-3985) | aceita, como hoje |
| Arquivo apresentado | `portal:documento-da-convocacao` | `nao_encontrado()` (FR-3985) | mostra |
| Requerimento da chamada | `portal:requerimento`, `preencher.apurar` → `chamada_em_aberto` | como para quem não foi convocado; envio recusado pela política (FR-3986, D-003) | abre |

**Resposta igual à ausência.** Nenhuma superfície pode responder diferente para *"não há convocação"* e
para *"há convocação invisível"*: nem texto, nem status, nem rota de redirecionamento.

**Número de consultas.** Lista e acompanhamento: o mesmo número fixo de hoje sem convocação pendente;
até três a mais, constantes, com alguma (R-002).
