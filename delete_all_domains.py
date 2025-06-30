import os
from dotenv import load_dotenv
from rich import print

try:
    from metadata.generated.schema.entity.domains.domain import Domain
    from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
    from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig
    from metadata.ingestion.ometa.ometa_api import OpenMetadata
except ImportError as e:
    print(f"[red]Error importing OpenMetadata SDK: {e}[/red]")
    print("[yellow]Please install the required dependencies with: pip install -r requirements.txt[/yellow]")
    exit(1)

load_dotenv()

server_url = os.getenv("OPENMETADATA_SERVER_URL")
jwt_token = os.getenv("OPENMETADATA_JWT_TOKEN")

if not server_url or not jwt_token:
    print("[red]OPENMETADATA_SERVER_URL and OPENMETADATA_JWT_TOKEN must be set in .env for the target instance.[/red]")
    exit(1)

print(f"[yellow]Connecting to: {server_url}[/yellow]")

connection = OpenMetadataConnection(
    hostPort=server_url,
    authProvider="openmetadata",
    securityConfig=OpenMetadataJWTClientConfig(jwtToken=jwt_token),
)
metadata = OpenMetadata(connection)

domains = metadata.list_entities(entity=Domain, limit=10000)
if not hasattr(domains, "entities"):
    print("[red]No domains found or error fetching domains.[/red]")
    exit(1)

entities = domains.entities
print(f"[blue]Found {len(entities)} domains. Deleting...[/blue]")

for domain in entities:
    try:
        print(f"Deleting: {domain.fullyQualifiedName} (id={domain.id})")
        metadata.delete(entity=Domain, entity_id=domain.id)
    except Exception as e:
        print(f"[red]Failed to delete {domain.fullyQualifiedName}: {e}[/red]")

print("[green]All domains deleted (or attempted).[/green]")
