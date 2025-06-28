#!/usr/bin/env python3
"""
Tests for OpenMetadata Migration Tool
"""

# Import the import module by loading it as a module
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from export import OpenMetadataExporter

# Load the import.py module
spec = importlib.util.spec_from_file_location(
    "import_module", os.path.join(os.path.dirname(__file__), "import.py")
)
import_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_module)
OpenMetadataImporter = import_module.OpenMetadataImporter


class TestOpenMetadataExporter:
    """Test cases for OpenMetadata Exporter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "openmetadata": {
                "server_url": "http://test.example.com",
                "auth": {"jwt_token": "test_token"},
            },
            "export": {
                "output_dir": "./test_exports",
                "entities": {"domains": True, "teams": True, "data_products": False},
                "selective": {
                    "domains": [],
                    "linked_data_products_only": False,
                    "linked_assets_only": False,
                },
                "batch_size": 10,
            },
            "logging": {"level": "INFO"},
        }

    def test_load_config(self):
        """Test configuration loading."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        try:
            with patch("export.load_dotenv"):
                with patch.object(OpenMetadataExporter, "_create_client"):
                    exporter = OpenMetadataExporter(config_path)
                    assert (
                        exporter.config["openmetadata"]["server_url"]
                        == "http://test.example.com"
                    )
                    assert exporter.config["export"]["batch_size"] == 10
        finally:
            os.unlink(config_path)

    def test_env_overrides(self):
        """Test environment variable overrides."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "OPENMETADATA_SERVER_URL": "http://env.example.com",
                    "EXPORT_BATCH_SIZE": "50",
                },
            ):
                with patch("export.load_dotenv"):
                    with patch.object(OpenMetadataExporter, "_create_client"):
                        exporter = OpenMetadataExporter(config_path)
                        exporter._apply_env_overrides()
                        assert (
                            exporter.config["openmetadata"]["server_url"]
                            == "http://env.example.com"
                        )
                        assert exporter.config["export"]["batch_size"] == 50
        finally:
            os.unlink(config_path)

    @patch("export.OpenMetadata")
    def test_write_ndjson(self, mock_om):
        """Test NDJSON file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                test_config = self.test_config.copy()
                test_config["export"]["output_dir"] = temp_dir
                yaml.dump(test_config, f)
                config_path = f.name

            try:
                with patch("export.load_dotenv"):
                    exporter = OpenMetadataExporter(config_path)

                    test_entities = [
                        {"id": "1", "name": "test1"},
                        {"id": "2", "name": "test2"},
                    ]

                    count = exporter._write_ndjson(
                        test_entities, "test_entities", Path(temp_dir)
                    )
                    assert count == 2

                    # Verify file content
                    ndjson_file = Path(temp_dir) / "test_entities.ndjson"
                    assert ndjson_file.exists()

                    with open(ndjson_file, "r") as f:
                        lines = f.readlines()
                        assert len(lines) == 2
                        entity1 = json.loads(lines[0])
                        assert entity1["name"] == "test1"
            finally:
                os.unlink(config_path)

    @patch("export.OpenMetadata")
    def test_export_entity_type_sdk(self, mock_om):
        """Test SDK-based entity export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                test_config = self.test_config.copy()
                test_config["export"]["output_dir"] = temp_dir
                yaml.dump(test_config, f)
                config_path = f.name

            try:
                with patch("export.load_dotenv"):
                    # Mock the SDK entities response
                    mock_entity1 = Mock()
                    mock_entity1.model_dump.return_value = {
                        "id": "1",
                        "name": "Test Domain 1",
                    }
                    mock_entity2 = Mock()
                    mock_entity2.model_dump.return_value = {
                        "id": "2",
                        "name": "Test Domain 2",
                    }

                    mock_response = Mock()
                    mock_response.entities = [mock_entity1, mock_entity2]

                    exporter = OpenMetadataExporter(config_path)
                    exporter.om_client.list_entities.return_value = mock_response

                    # Test exporting with mock entity class
                    from metadata.generated.schema.entity.domains.domain import \
                        Domain

                    count = exporter._export_entity_type(
                        "domains", Domain, Path(temp_dir)
                    )

                    assert count == 2
                    assert exporter.om_client.list_entities.called

                    # Verify file was created
                    ndjson_file = Path(temp_dir) / "domains.ndjson"
                    assert ndjson_file.exists()
            finally:
                os.unlink(config_path)

    def test_selective_export_entities(self):
        """Test selective export using entity list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        try:
            with patch("export.load_dotenv"):
                with patch.object(OpenMetadataExporter, "_create_client"):
                    with patch.object(
                        OpenMetadataExporter, "_export_entity_type"
                    ) as mock_export:
                        mock_export.return_value = 5

                        exporter = OpenMetadataExporter(config_path)
                        exporter.export_all(selected_entities=["domains", "teams"])

                        # Should only export the selected entities
                        assert mock_export.call_count == 2
                        call_args = [call[0] for call in mock_export.call_args_list]
                        entity_names = [args[0] for args in call_args]
                        assert "domains" in entity_names
                        assert "teams" in entity_names
        finally:
            os.unlink(config_path)


class TestOpenMetadataImporter:
    """Test cases for OpenMetadata Importer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "openmetadata": {
                "server_url": "http://test.example.com",
                "auth": {"jwt_token": "test_token"},
            },
            "import": {
                "input_dir": "./test_imports",
                "update_existing": True,
                "skip_on_error": True,
                "import_order": ["teams", "domains", "data_products"],
            },
            "logging": {"level": "INFO"},
        }

    def test_load_ndjson(self):
        """Test NDJSON file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ndjson_file = Path(temp_dir) / "test.ndjson"

            test_data = [{"id": "1", "name": "entity1"}, {"id": "2", "name": "entity2"}]

            with open(ndjson_file, "w") as f:
                for entity in test_data:
                    json.dump(entity, f)
                    f.write("\n")

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(self.test_config, f)
                config_path = f.name

            try:
                with patch.object(import_module, "load_dotenv"):
                    with patch.object(OpenMetadataImporter, "_create_client"):
                        importer = OpenMetadataImporter(config_path)
                        entities = importer._load_ndjson(ndjson_file)

                        assert len(entities) == 2
                        assert entities[0]["name"] == "entity1"
                        assert entities[1]["name"] == "entity2"
            finally:
                os.unlink(config_path)

    def test_env_overrides_import(self):
        """Test environment variable overrides for import."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "IMPORT_INPUT_DIR": "/custom/import/dir",
                    "IMPORT_SKIP_ON_ERROR": "false",
                },
            ):
                with patch.object(import_module, "load_dotenv"):
                    with patch.object(OpenMetadataImporter, "_create_client"):
                        importer = OpenMetadataImporter(config_path)
                        importer._apply_env_overrides()
                        assert (
                            importer.config["import"]["input_dir"]
                            == "/custom/import/dir"
                        )
                        assert importer.config["import"]["skip_on_error"] == False
        finally:
            os.unlink(config_path)


class TestIntegration:
    """Integration tests for export/import workflow."""

    def test_export_import_workflow(self):
        """Test a complete export/import cycle with mock data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up test configuration
            test_config = {
                "openmetadata": {
                    "server_url": "http://test.example.com",
                    "auth": {"jwt_token": "test_token"},
                },
                "export": {
                    "output_dir": temp_dir,
                    "entities": {"teams": True, "domains": True},
                    "selective": {
                        "domains": [],
                        "linked_data_products_only": False,
                        "linked_assets_only": False,
                    },
                },
                "import": {"input_dir": temp_dir, "import_order": ["teams", "domains"]},
                "logging": {"level": "INFO"},
            }

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(test_config, f)
                config_path = f.name

            try:
                # Mock export data
                mock_teams = [
                    {"id": "t1", "name": "Team 1"},
                    {"id": "t2", "name": "Team 2"},
                ]
                mock_domains = [{"id": "d1", "name": "Domain 1"}]

                # Test export
                with patch("export.load_dotenv"):
                    with patch.object(OpenMetadataExporter, "_create_client"):
                        exporter = OpenMetadataExporter(config_path)

                        # Write test data
                        exporter._write_ndjson(mock_teams, "teams", Path(temp_dir))
                        exporter._write_ndjson(mock_domains, "domains", Path(temp_dir))

                # Verify exported files exist
                teams_file = Path(temp_dir) / "teams.ndjson"
                domains_file = Path(temp_dir) / "domains.ndjson"
                assert teams_file.exists()
                assert domains_file.exists()

                # Test import
                with patch.object(import_module, "load_dotenv"):
                    with patch.object(OpenMetadataImporter, "_create_client"):
                        importer = OpenMetadataImporter(config_path)

                        # Load and verify data
                        teams_data = importer._load_ndjson(teams_file)
                        domains_data = importer._load_ndjson(domains_file)

                        assert len(teams_data) == 2
                        assert len(domains_data) == 1
                        assert teams_data[0]["name"] == "Team 1"
                        assert domains_data[0]["name"] == "Domain 1"

            finally:
                os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
