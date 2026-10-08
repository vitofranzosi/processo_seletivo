"""O rascunho gravado das Etapas depois de "Salvar rascunho" (D-005).

Envia o corpo que a tela montaria (`ENVIO`, o JSON de pares que o `FormData` leu na página) para a
etapa Etapas do Edital `EDITAL`, como `ana.gestora`, e imprime o que ficou gravado: as linhas das
Etapas e o registro da gravação, sem o que muda a cada gravação por natureza (o instante, o
identificador do registro, a correlação e a revisão do Edital).

    DB_NAME=ps_058_polish DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true \
      EDITAL=<uuid> ENVIO=<arquivo.json> RASCUNHO_SAIDA=<arquivo.json> \
      uv run python manage.py shell < ../specs/058-polish-residuos/capturas/rascunho.py
"""

import json
import os

from django.conf import settings
from django.test import Client

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from processo_seletivo.interface import identidade

settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

edital = os.environ["EDITAL"]
envio = json.load(open(os.environ["ENVIO"]))
cliente = Client()
assert cliente.post(
    "/gestao/identificar", {"subject": "ana.gestora", "papeis": list(identidade.PAPEIS)}
).status_code == 302

corpo = {}
for chave, valor in envio["pares"]:
    corpo.setdefault(chave, []).append(valor)
resposta = cliente.post(f"/gestao/editais/{edital}/compor/etapas", corpo)

CAMPOS = (
    "id name order weight eliminatory classificatory minimum_score evaluations_per_registration "
    "maximum_score forma rotulo_favoravel rotulo_desfavoravel evento_id"
).split()
etapas = [
    {campo: str(getattr(etapa, campo)) for campo in CAMPOS}
    for etapa in EtapaAvaliacao.objects.filter(edital_id=edital).order_by("order")
]
registro = (
    RegistroAuditoria.objects.filter(aggregate_id=edital).order_by("-occurred_at").first()
)
gravado = {
    "status": resposta.status_code,
    "destino": resposta.get("Location", ""),
    "etapas": etapas,
    "registro": {
        campo: str(getattr(registro, campo))
        for campo in (
            "actor_subject permission institution_scope operation aggregate_type "
            "previous_state new_state reason idempotency_key detalhe"
        ).split()
    },
}
with open(os.environ["RASCUNHO_SAIDA"], "w") as arquivo:
    json.dump(gravado, arquivo, indent=1, ensure_ascii=False)
print(json.dumps(gravado, indent=1, ensure_ascii=False))
