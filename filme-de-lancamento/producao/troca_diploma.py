import hashlib
from django.core.files.base import ContentFile
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from processo_seletivo.inscricoes.storage import caminho_do_documento
data=open("/private/tmp/claude-501/-Users-saymoncastro-Projetos-processo-seletivo--claude-worktrees-ifes-launch-film-cabb9f/c2cdae9c-f6fb-4083-b2ee-2f8555e837dd/scratchpad/film/diploma_ficticio.pdf","rb").read()
d=DocumentoSubmetido.objects.get(inscricao_id="4a64c39e-e9de-468f-a477-6de0d28cb69d", requirement_id="00000000-0000-0000-0051-0000000000d2")
st=d.arquivo.storage
novo=st.save(caminho_do_documento(d,"diploma.pdf"), ContentFile(data))
DocumentoSubmetido.objects.filter(pk=d.pk).update(arquivo=novo, content_hash=hashlib.sha256(data).hexdigest(), tamanho=len(data), nome_original="ana_diploma.pdf")
print("trocado", d.pk, novo)
