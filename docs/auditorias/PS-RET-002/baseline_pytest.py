"""Compara falhas fora do escopo com os dois módulos originais de HEAD, sem restaurar arquivos."""
import importlib.abc,importlib.util,sys,pytest
class Originais(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        nomes={'processo_seletivo.interface.views':'views','processo_seletivo.editais.domain.validation':'validation'}
        if fullname in nomes:
            return importlib.util.spec_from_file_location(fullname,'/evidencias/HEAD-'+nomes[fullname]+'.py')
sys.meta_path.insert(0,Originais())
sys.exit(pytest.main(['-p','no:cacheprovider','-q','-ra','tests/interface/test_shell_da_gestao.py','tests/integration/test_foundation.py::test_models_have_no_pending_migrations']))
