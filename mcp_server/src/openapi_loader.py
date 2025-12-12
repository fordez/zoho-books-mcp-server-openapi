import glob
import logging
import os

import yaml
from src.constants import ALLOWED_TOOLS
from src.openapi_utils import (
    add_missing_request_schemas,
    filter_openapi_paths,
    fix_missing_parameters,
    fix_parameter_schemas,
    remove_all_refs_from_schemas,
)

logger = logging.getLogger(__name__)


def remove_response_schemas(spec):
    """Elimina todos los schemas de respuesta para evitar validación"""
    logger.info("🔥 Removing response schemas...")
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue
            if "responses" in operation:
                for status_code, response_def in operation["responses"].items():
                    if "content" in response_def:
                        response_def.pop("content")
    logger.info("Response schemas removed")
    return spec


def load_and_process_openapi():
    """Carga todos los YAML de OpenAPI, los mergea y aplica la pipeline de procesamiento"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OPENAPI_DIR = os.path.join(BASE_DIR, "../openapi-all")

    yaml_files = sorted(
        glob.glob(os.path.join(OPENAPI_DIR, "*.yaml"))
        + glob.glob(os.path.join(OPENAPI_DIR, "*.yml")),
        key=lambda x: (
            0
            if "invoices" in x.lower()
            else 1
            if "customer-debit-notes" in x.lower()
            else 2
        ),
    )

    logger.info(f"📄 Found {len(yaml_files)} YAML files")

    combined_paths = {}
    combined_tags = []
    combined_schemas = {}
    combined_parameters = {}
    info = {"title": "Zoho Books AI Agent API", "version": "1.0.0"}

    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)
            if not spec:
                continue
            # Merge paths
            if "paths" in spec:
                for spec_path, path_item in spec["paths"].items():
                    if spec_path not in combined_paths:
                        combined_paths[spec_path] = path_item
                    else:
                        for key, value in path_item.items():
                            if key in combined_paths[spec_path] and key.lower() in [
                                "get",
                                "post",
                                "put",
                                "patch",
                                "delete",
                            ]:
                                continue
                            combined_paths[spec_path][key] = value
            # Merge tags
            if "tags" in spec:
                combined_tags.extend(spec["tags"])
            # Merge components
            if "components" in spec:
                combined_schemas.update(spec["components"].get("schemas", {}))
                combined_parameters.update(spec["components"].get("parameters", {}))
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    combined_spec = {
        "openapi": "3.0.0",
        "info": info,
        "paths": combined_paths,
        "tags": combined_tags,
        "components": {
            "schemas": combined_schemas,
            "parameters": combined_parameters,
        },
    }

    # Pipeline de procesamiento
    combined_spec = fix_missing_parameters(combined_spec)
    combined_spec = add_missing_request_schemas(combined_spec)
    combined_spec = remove_all_refs_from_schemas(combined_spec)
    combined_spec = fix_parameter_schemas(combined_spec)
    combined_spec = filter_openapi_paths(combined_spec, ALLOWED_TOOLS)
    combined_spec = remove_response_schemas(combined_spec)

    logger.info(f"Filtered paths: {len(combined_spec['paths'])}")
    return combined_spec
