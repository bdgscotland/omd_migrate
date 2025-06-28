#!/usr/bin/env python3
"""
OpenMetadata Import Tool
Imports metadata entities from NDJSON files to OpenMetadata for restore or migration.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml
import click
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich import print as rprint
from dotenv import load_dotenv

try:
    from metadata.generated.schema.api.domains.createDataProduct import CreateDataProductRequest
    from metadata.generated.schema.api.domains.createDomain import CreateDomainRequest
    from metadata.generated.schema.api.teams.createTeam import CreateTeamRequest
    from metadata.generated.schema.api.teams.createUser import CreateUserRequest
    from metadata.generated.schema.api.policies.createPolicy import CreatePolicyRequest
    from metadata.ingestion.ometa.ometa_api import OpenMetadata
    from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig
    from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
except ImportError as e:
    rprint(f"[red]Error importing OpenMetadata SDK: {e}[/red]")
    rprint("[yellow]Please install the required dependencies with: pip install -r requirements.txt[/yellow]")
    sys.exit(1)

console = Console()

class OpenMetadataImporter:
    """Import OpenMetadata entities from NDJSON files."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the importer with configuration."""
        # Load environment variables from .env file
        load_dotenv()
        self.config = self._load_config(config_path)
        self._apply_env_overrides()
        self.om_client = self._create_client()
        self.import_stats = {}
        self.errors = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            console.print(f"[red]Configuration file {config_path} not found![/red]")
            sys.exit(1)
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing configuration file: {e}[/red]")
            sys.exit(1)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # OpenMetadata server configuration
        if os.getenv('OPENMETADATA_SERVER_URL'):
            self.config['openmetadata']['server_url'] = os.getenv('OPENMETADATA_SERVER_URL')
        
        if os.getenv('OPENMETADATA_JWT_TOKEN'):
            self.config['openmetadata']['auth']['jwt_token'] = os.getenv('OPENMETADATA_JWT_TOKEN')
        
        # Import configuration
        if os.getenv('IMPORT_INPUT_DIR'):
            self.config['import']['input_dir'] = os.getenv('IMPORT_INPUT_DIR')
        
        if os.getenv('IMPORT_UPDATE_EXISTING'):
            self.config['import']['update_existing'] = os.getenv('IMPORT_UPDATE_EXISTING').lower() == 'true'
        
        if os.getenv('IMPORT_SKIP_ON_ERROR'):
            self.config['import']['skip_on_error'] = os.getenv('IMPORT_SKIP_ON_ERROR').lower() == 'true'
        
        # Logging configuration
        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')
    
    def _create_client(self) -> OpenMetadata:
        """Create OpenMetadata client from configuration."""
        try:
            om_config = self.config['openmetadata']
            server_url = om_config['server_url']
            
            # Create authentication config
            auth_config = om_config.get('auth', {})
            
            if 'jwt_token' in auth_config and auth_config['jwt_token']:
                # JWT Token authentication
                auth_provider = 'openmetadata'
                auth_config_obj = OpenMetadataJWTClientConfig(
                    jwtToken=auth_config['jwt_token']
                )
            else:
                # No authentication for now (can be extended)
                auth_provider = None
                auth_config_obj = None
            
            # Create connection config
            metadata_connection = OpenMetadataConnection(
                hostPort=server_url,
                authProvider=auth_provider,
                securityConfig=auth_config_obj
            )
            
            # Create and return OpenMetadata client
            return OpenMetadata(metadata_connection)
            
        except Exception as e:
            console.print(f"[red]Error creating OpenMetadata client: {e}[/red]")
            sys.exit(1)
    
    def _load_ndjson(self, filepath: Path) -> List[Dict]:
        """Load entities from NDJSON file."""
        entities = []
        try:
            with filepath.open('r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            entity = json.loads(line)
                            entities.append(entity)
                        except json.JSONDecodeError as e:
                            console.print(f"[yellow]⚠[/yellow] Error parsing line {line_num} in {filepath}: {e}")
            return entities
        except FileNotFoundError:
            console.print(f"[yellow]⚠[/yellow] File not found: {filepath}")
            return []
        except Exception as e:
            console.print(f"[red]✗[/red] Error reading {filepath}: {e}")
            return []
    
    def _filter_entity_fields(self, entity_data: Dict, entity_type: str) -> Dict:
        """Filter entity data to only include fields valid for creation."""
        if entity_type == 'data_products':
            # Fields allowed in CreateDataProductRequest
            allowed_fields = {
                'name', 'displayName', 'description', 'fullyQualifiedName',
                'owners', 'experts', 'domain', 'assets', 'tags', 'extension'
            }
            filtered_data = {k: v for k, v in entity_data.items() if k in allowed_fields}
            
            # Convert domain from dict to string if needed
            if 'domain' in filtered_data and isinstance(filtered_data['domain'], dict):
                filtered_data['domain'] = filtered_data['domain'].get('fullyQualifiedName', str(filtered_data['domain'].get('name', '')))
            
            return filtered_data
        elif entity_type == 'domains':
            # Add domain-specific filtering here if needed
            allowed_fields = {
                'name', 'displayName', 'description', 'fullyQualifiedName',
                'domainType', 'parent', 'owners', 'experts', 'tags', 'extension'
            }
            return {k: v for k, v in entity_data.items() if k in allowed_fields}
        elif entity_type == 'teams':
            # Add team-specific filtering here if needed
            allowed_fields = {
                'name', 'displayName', 'description', 'fullyQualifiedName',
                'teamType', 'email', 'parents', 'users', 'owners', 'defaultRoles'
            }
            return {k: v for k, v in entity_data.items() if k in allowed_fields}
        else:
            # For other entity types, return as-is for now
            return entity_data

    def _import_entity(self, entity_data: Dict, entity_type: str) -> bool:
        """Import a single entity."""
        try:
            # Filter fields to only include those valid for creation
            filtered_data = self._filter_entity_fields(entity_data, entity_type)
            
            # Create appropriate API request based on entity type
            if entity_type == 'data_products':
                request = CreateDataProductRequest(**filtered_data)
                result = self.om_client.create_or_update(request)
            elif entity_type == 'domains':
                request = CreateDomainRequest(**filtered_data)
                result = self.om_client.create_or_update_domain(request)
            elif entity_type == 'teams':
                request = CreateTeamRequest(**filtered_data)
                result = self.om_client.create_or_update_team(request)
            elif entity_type == 'users':
                request = CreateUserRequest(**filtered_data)
                result = self.om_client.create_or_update_user(request)
            elif entity_type == 'policies':
                request = CreatePolicyRequest(**filtered_data)
                result = self.om_client.create_or_update_policy(request)
            else:
                console.print(f"[yellow]⚠[/yellow] Import method not implemented for {entity_type}")
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Error importing {entity_type} entity: {e}"
            self.errors.append(error_msg)
            
            if not self.config['import'].get('skip_on_error', True):
                console.print(f"[red]✗[/red] {error_msg}")
                raise
            else:
                console.print(f"[yellow]⚠[/yellow] {error_msg} (skipping)")
                return False
    
    def _import_entity_type(self, entity_type: str, input_dir: Path) -> int:
        """Import all entities of a specific type."""
        filepath = input_dir / f"{entity_type}.ndjson"
        
        if not filepath.exists():
            console.print(f"[yellow]⚠[/yellow] No file found for {entity_type}: {filepath}")
            return 0
        
        console.print(f"[blue]Importing {entity_type}...[/blue]")
        entities = self._load_ndjson(filepath)
        
        if not entities:
            console.print(f"[yellow]⚠[/yellow] No entities found in {filepath}")
            return 0
        
        success_count = 0
        
        with Progress() as progress:
            task = progress.add_task(f"[green]Importing {entity_type}...", total=len(entities))
            
            for entity in entities:
                if self._import_entity(entity, entity_type):
                    success_count += 1
                progress.advance(task)
        
        console.print(f"[green][/green] Imported {success_count}/{len(entities)} {entity_type}")
        return success_count
    
    def import_all(self):
        """Import all entities according to configured order."""
        console.print("[bold blue]Starting OpenMetadata Import[/bold blue]")
        console.print(f"Server: {self.config['openmetadata']['server_url']}")
        
        input_dir = Path(self.config['import']['input_dir'])
        
        if not input_dir.exists():
            console.print(f"[red]Input directory does not exist: {input_dir}[/red]")
            sys.exit(1)
        
        import_order = self.config['import']['import_order']
        total_imported = 0
        
        console.print(f"Input directory: {input_dir}")
        console.print(f"Import order: {' → '.join(import_order)}")
        
        # Import entities in specified order
        for entity_type in import_order:
            count = self._import_entity_type(entity_type, input_dir)
            self.import_stats[entity_type] = count
            total_imported += count
        
        # Create summary
        self._create_import_summary(input_dir, total_imported)
        
        console.print(f"\n[bold green]Import completed![/bold green]")
        console.print(f"Total entities imported: {total_imported}")
        
        if self.errors:
            console.print(f"[yellow]Errors encountered: {len(self.errors)}[/yellow]")
            
            # Show first few errors
            for i, error in enumerate(self.errors[:5]):
                console.print(f"[red]{i+1}.[/red] {error}")
            
            if len(self.errors) > 5:
                console.print(f"[yellow]... and {len(self.errors) - 5} more errors[/yellow]")
    
    def _create_import_summary(self, input_dir: Path, total_imported: int):
        """Create import summary file."""
        summary = {
            'import_timestamp': datetime.now().isoformat(),
            'server_url': self.config['openmetadata']['server_url'],
            'input_directory': str(input_dir),
            'total_entities_imported': total_imported,
            'entity_counts': self.import_stats,
            'errors_count': len(self.errors),
            'errors': self.errors[:10] if self.errors else [],  # First 10 errors
            'import_config': self.config['import']
        }
        
        summary_file = input_dir / 'import_summary.json'
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"[green][/green] Import summary saved to {summary_file}")
        
        # Display summary table
        table = Table(title="Import Summary")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Status", style="green")
        
        for entity_type, count in self.import_stats.items():
            status = "" if count > 0 else "⚠"
            table.add_row(entity_type.replace('_', ' ').title(), str(count), status)
        
        console.print(table)

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.option('--input-dir', '-i', help='Override input directory from config')
@click.option('--entity-type', '-e', help='Import only specific entity type')
@click.option('--dry-run', is_flag=True, help='Show what would be imported without actually importing')
def main(config: str, input_dir: Optional[str], entity_type: Optional[str], dry_run: bool):
    """Import OpenMetadata entities from NDJSON files."""
    try:
        importer = OpenMetadataImporter(config)
        
        # Override input directory if provided
        if input_dir:
            importer.config['import']['input_dir'] = input_dir
        
        if dry_run:
            console.print("[yellow]DRY RUN MODE - No entities will be imported[/yellow]")
            input_path = Path(importer.config['import']['input_dir'])
            
            if entity_type:
                filepath = input_path / f"{entity_type}.ndjson"
                if filepath.exists():
                    entities = importer._load_ndjson(filepath)
                    console.print(f"Would import {len(entities)} {entity_type} entities")
                else:
                    console.print(f"File not found: {filepath}")
            else:
                total = 0
                for et in importer.config['import']['import_order']:
                    filepath = input_path / f"{et}.ndjson"
                    if filepath.exists():
                        entities = importer._load_ndjson(filepath)
                        console.print(f"Would import {len(entities)} {et} entities")
                        total += len(entities)
                console.print(f"Total entities to import: {total}")
            return
        
        if entity_type:
            # Import specific entity type
            input_path = Path(importer.config['import']['input_dir'])
            count = importer._import_entity_type(entity_type, input_path)
            console.print(f"[green]Imported {count} {entity_type} entities[/green]")
        else:
            # Import all entities
            importer.import_all()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Import cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()