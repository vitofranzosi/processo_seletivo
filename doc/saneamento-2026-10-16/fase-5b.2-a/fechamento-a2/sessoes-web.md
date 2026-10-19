# Proposta de controle das sessões web

Situação: nenhuma sessão iniciada, nenhum usuário/permissão criado ou alterado. A proposta
depende de deliberação do produto, Cefor e responsável pela homologação; não aprova DEC-14/15.16.

## Restrições técnicas presentes nos artefatos

- Operador bloqueia `iniciar`/`demonstrar`, mesmo com ação incluída em arquivo local de autorização.
- Launcher montado recusa partida sem importar Django. Há bloqueio de acesso ao ensaio por essa
  entrada, não implementação de uma sessão limitada por cenário.
- Manifesto declara loopback `127.0.0.1:18084`, rede interna, filesystem read-only, mídia própria,
  runtime, console de e-mail e integrações desativadas. São configurações não exercitadas.
- Permissões e escopos de domínio existentes continuam vigentes; não foram alterados nem
  homologados nesta fase. O seletor de identidade de demonstração continua configurado como true.

**Não há ACL de cenário implementada.** Imprimir receita, autorizar uma URL, bind loopback ou
escolher uma lista de subcasos não limita tecnicamente todos os endpoints da aplicação.
Quem controla o daemon/host continua podendo contornar o operador; ele não é sandbox de administrador.

## Restrições técnicas propostas, ainda não aplicadas

| Mecanismo | Finalidade / decisão requerida | Limitação e aceite futuro |
|---|---|---|
| Contas sintéticas por ator/escopo | Usar autorização existente sem permissão global, separar elaborador/homologador/publicador/candidato | Manifesto de concessões explícitas e recusas observadas; não conceder exportação em lote a outros papéis |
| Desligar seletor de identidade | Evitar troca livre de ator em sessão de homologação | Antes definir provedor de autenticação de laboratório e caminho completo de cada ator; não presumir que desligar a flag basta |
| Proxy de laboratório | Allowlist revisada de métodos/rotas por cenário e bloqueio de administração fora do escopo | Não modifica domínio; não substitui permissões/CSRF nem cobre efeitos internos só pela rota. Exige imagem/digest/manifesto/autorização novos, ainda não selecionados |
| Instância ou namespace por variante | Evitar alteração de pré-condições de um caso pelo anterior | Instância nova exige identidade, nomes, arquivos, hashes e recursos exclusivos aprovados; Compose atual não oferece instâncias concorrentes só mudando o nome do projeto |
| Janela de sessão e contenção | Expirar acesso, parar só app e manter evidências | Política de expiração/operador ainda não implementada; não usar encerramento de sessão como descarte |

Recomendação para decisão: contas restritas e instância/namespace próprio por grupo incompatível,
com gate de sessão somente depois de demonstrado o isolamento. Avaliar proxy se o responsável
exigir bloqueio técnico por subcaso; não reabilitar web antes de escolher e revisar a estratégia.
Nenhuma alteração funcional foi feita para viabilizar essa proposta.

## Controles procedimentais a pactuar

Antes da sessão: responsável técnico confirma ambiente/hash/URL, ator, variante, janela e destino
de evidência. Facilitador lê a tarefa sem antecipar solução; observador registra horário, dificuldade,
intervenção e resultado. Não usar contas/sistemas/arquivos reais. Dados sensíveis do cenário devem
ser fictícios; capturas não devem conter credencial, OTP, cookie, rosto ou nome real desnecessário.

Adotar a distinção proposta na DEC-15.16: conclusão autônoma, assistida, desistência e tarefa não
concluída; registrar tempo, tipo e momento da intervenção. Dez minutos é referência proposta,
não limite aprovado. Os critérios devem ser pactuados antes, sem alteração retroativa.

Durante a sessão: um operador por vez; somente passos aprovados. Diante de dificuldade prolongada,
registrar o estado e oferecer ajuda segundo protocolo previamente aprovado. Não aumentar permissão,
editar SQL, trocar dado, invocar shell/API para completar tarefa de navegador ou corrigir código
durante a medição. Uma demonstração técnica por API deve ser identificada separadamente.

Interromper se houver dado real, rede/ambiente inesperado, ato fora da variante, falha de autorização,
acesso indevido ou perda de evidência. Contenção só por ação própria autorizada, preservando banco,
volumes e trilha. Não apagar erro para reiniciar cronômetro. Cefor deve indicar participantes,
observadores e critérios de aceite; custodiante e prazo de retenção das evidências permanecem a definir.

## Riscos residuais

Loopback permite acesso por outros processos/usuários locais; rede interna declarada ainda precisa
de verificação; GET pode escrever trilha/sessão; geração não prova download; ambiente sintético não
prova licitude de atos em certame real. Controle procedimental pode ser descumprido. Restrição por
rota pode omitir endpoints ou efeitos indiretos. Configuração/código montado no host permanece
mutável por administrador. Nenhum desses riscos foi demonstrado como eliminado em execução.
