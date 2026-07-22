"""Apply pending Qdrant memory migrations and print the resulting schema version."""

from retailmind_api.config import get_settings
from retailmind_api.memory import QdrantMemoryRepository


repository = QdrantMemoryRepository(get_settings())
print(f"RetailMind Qdrant schema is at version {repository.schema_version}.")
