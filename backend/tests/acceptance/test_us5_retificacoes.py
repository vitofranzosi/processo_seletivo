from tests.integration.publicacoes.test_retificacoes import (
    test_published_retification_preserves_original_and_creates_consolidated_version,
)


def test_us5_retification_flow(api_client, manager_headers, process_payload, transactional_db):
    test_published_retification_preserves_original_and_creates_consolidated_version(
        api_client, manager_headers, process_payload
    )
