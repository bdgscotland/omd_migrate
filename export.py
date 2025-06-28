#!/usr/bin/env python3
"""
Working OpenMetadata Export Tool with proper SDK integration
"""

import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import yaml
import click
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table as RichTable
from rich import print as rprint
from dotenv import load_dotenv

try:
    from metadata.generated.schema.entity.services.databaseService import DatabaseService
    from metadata.generated.schema.entity.data.database import Database
    from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
    from metadata.generated.schema.entity.data.table import Table
    from metadata.generated.schema.entity.teams.team import Team
    from metadata.generated.schema.entity.teams.user import User
    from metadata.generated.schema.entity.policies.policy import Policy
    from metadata.generated.schema.entity.domains.domain import Domain
    from metadata.generated.schema.entity.domains.dataProduct import DataProduct
    from metadata.generated.schema.entity.data.glossary import Glossary
    from metadata.generated.schema.entity.data.glossaryTerm import GlossaryTerm
    from metadata.ingestion.ometa.ometa_api import OpenMetadata
    from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig
    from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
except ImportError as e:
    rprint(f"[red]Error importing OpenMetadata SDK: {e}[/red]")
    rprint("[yellow]Please install the required dependencies with: pip install -r requirements.txt[/yellow]")
    sys.exit(1)

console = Console()

class OpenMetadataExporter:
    """Export OpenMetadata entities to NDJSON files using OpenMetadata SDK."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the exporter with configuration."""
        load_dotenv()
        self.config = self._load_config(config_path)
        self._apply_env_overrides()
        self.om_client = self._create_client()
        self.export_stats = {}
        
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
        if os.getenv('OPENMETADATA_SERVER_URL'):
            self.config['openmetadata']['server_url'] = os.getenv('OPENMETADATA_SERVER_URL')
        if os.getenv('OPENMETADATA_JWT_TOKEN'):
            self.config['openmetadata']['auth']['jwt_token'] = os.getenv('OPENMETADATA_JWT_TOKEN')
        if os.getenv('EXPORT_OUTPUT_DIR'):
            self.config['export']['output_dir'] = os.getenv('EXPORT_OUTPUT_DIR')
    
    def _create_client(self) -> OpenMetadata:
        """Create OpenMetadata client from configuration."""
        try:
            om_config = self.config['openmetadata']
            server_url = om_config['server_url']
            auth_config = om_config.get('auth', {})
            
            if 'jwt_token' in auth_config and auth_config['jwt_token']:
                auth_provider = 'openmetadata'
                auth_config_obj = OpenMetadataJWTClientConfig(
                    jwtToken=auth_config['jwt_token']
                )
            else:
                auth_provider = None
                auth_config_obj = None
            
            metadata_connection = OpenMetadataConnection(
                hostPort=server_url,
                authProvider=auth_provider,
                securityConfig=auth_config_obj
            )
            
            return OpenMetadata(metadata_connection)
            
        except Exception as e:
            console.print(f"[red]Error creating OpenMetadata client: {e}[/red]")
            sys.exit(1)
    
    def _ensure_output_dir(self) -> Path:
        """Ensure output directory exists."""
        output_dir = Path(self.config['export']['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _write_ndjson(self, entities: List[Dict], filename: str, output_dir: Path):
        """Write entities to NDJSON file."""
        filepath = output_dir / f"{filename}.ndjson"
        
        try:
            with filepath.open('w', encoding='utf-8') as f:
                for entity in entities:
                    json.dump(entity, f, ensure_ascii=False, default=str)
                    f.write('\n')
            
            console.print(f"[green]✓[/green] Exported {len(entities)} {filename} to {filepath}")
            return len(entities)
            
        except Exception as e:
            console.print(f"[red]✗[/red] Error writing {filename}: {e}")
            return 0
    
    def _export_entity_type(self, entity_name: str, entity_class, output_dir: Path) -> int:
        """Generic method to export any entity type using OpenMetadata SDK."""
        try:
            console.print(f"[blue]Exporting {entity_name}...[/blue]")
            
            # Use the OpenMetadata SDK to get all entities
            entities_response = self.om_client.list_entities(entity=entity_class, limit=10000)
            
            if hasattr(entities_response, 'entities'):
                entities = entities_response.entities
            else:
                entities = []
            
            console.print(f"[green]Retrieved {len(entities)} {entity_name}[/green]")
            
            # Convert entities to dictionaries using modern Pydantic
            entity_dicts = []
            for entity in entities:
                if hasattr(entity, 'model_dump'):
                    # Modern Pydantic v2
                    entity_dict = entity.model_dump()
                elif hasattr(entity, 'dict'):
                    # Legacy Pydantic v1 
                    entity_dict = entity.dict()
                else:
                    entity_dict = entity.__dict__ if hasattr(entity, '__dict__') else dict(entity)
                
                entity_dicts.append(entity_dict)
            
            return self._write_ndjson(entity_dicts, entity_name, output_dir)
                
        except Exception as e:
            console.print(f"[red]✗[/red] Error exporting {entity_name}: {e}")
            return 0
    
    def export_all(self, selected_entities: Optional[List[str]] = None):
        """Export all configured entities."""
        console.print("[bold blue]Starting OpenMetadata Export[/bold blue]")
        console.print(f"📍 Server: {self.config['openmetadata']['server_url']}")
        console.print(f"🔧 API Method: OpenMetadata SDK")
        
        output_dir = self._ensure_output_dir()
        
        # Define entity mappings (entity_name -> entity_class)
        entity_mappings = {
            'teams': Team,
            'users': User, 
            'policies': Policy,
            'domains': Domain,
            'glossaries': Glossary,
            'glossary_terms': GlossaryTerm,
            'databases': Database,
            'database_schemas': DatabaseSchema,
            'tables': Table,
            'data_products': DataProduct
        }
        
        # Determine what to export
        if selected_entities:
            entities_to_export = {name: entity_mappings[name] 
                                for name in selected_entities 
                                if name in entity_mappings}
        else:
            # Export based on config
            export_config = self.config['export']['entities']
            entities_to_export = {name: entity_class 
                                for name, entity_class in entity_mappings.items()
                                if export_config.get(name, False)}
        
        total_exported = 0
        
        with Progress() as progress:
            task = progress.add_task("[green]Exporting entities...", total=len(entities_to_export))
            
            for entity_name, entity_class in entities_to_export.items():
                count = self._export_entity_type(entity_name, entity_class, output_dir)
                self.export_stats[entity_name] = count
                total_exported += count
                progress.advance(task)
        
        # Create summary
        self._create_export_summary(output_dir, total_exported)
        
        console.print(f"\n[bold green]✅ Export completed![/bold green]")
        console.print(f"📊 Total entities exported: {total_exported}")
        console.print(f"📁 Output directory: {output_dir}")
    
    def _create_export_summary(self, output_dir: Path, total_exported: int):
        """Create export summary file."""
        summary = {
            'export_timestamp': datetime.now().isoformat(),
            'server_url': self.config['openmetadata']['server_url'],
            'api_method': 'openmetadata_sdk',
            'total_entities_exported': total_exported,
            'entity_counts': self.export_stats,
            'export_config': self.config['export']
        }
        
        summary_file = output_dir / 'export_summary.json'
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"[green]✓[/green] Export summary saved to {summary_file}")
        
        # Display summary table
        table = RichTable(title="Export Summary")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        
        for entity_type, count in self.export_stats.items():
            if count > 0:
                table.add_row(entity_type.replace('_', ' ').title(), str(count))
        
        console.print(table)

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.option('--output-dir', '-o', help='Override output directory from config')
@click.option('--entities', '-e', multiple=True, help='Specific entity types to export (e.g., -e data_products -e domains)')
@click.option('--clear', is_flag=True, help='Clear existing export state before starting')
def main(config: str, output_dir: Optional[str], entities: tuple, clear: bool):
    """Export OpenMetadata entities to NDJSON files using the OpenMetadata SDK."""
    try:
        exporter = OpenMetadataExporter(config)
        
        # Override output directory if provided
        if output_dir:
            exporter.config['export']['output_dir'] = output_dir
        
        # Clear export state if requested
        if clear:
            output_path = Path(exporter.config['export']['output_dir'])
            if output_path.exists():
                console.print(f"[yellow]🗑️  Clearing existing export state: {output_path}[/yellow]")
                shutil.rmtree(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✅ Clean export directory created[/green]")
        
        # Run export
        if entities:
            console.print(f"[blue]📤 Selective export: {list(entities)}[/blue]")
            exporter.export_all(selected_entities=list(entities))
        else:
            console.print(f"[blue]📤 Exporting all configured entities[/blue]")
            exporter.export_all()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Export cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()