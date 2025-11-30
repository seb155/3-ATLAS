"""
MeiliSearch Service - Full-Text Search Integration

Provides fast, typo-tolerant search across all entities:
- Assets (instruments, equipment)
- Rules (business rules)
- Cables (electrical cables)
- Locations (LBS nodes)

License: MeiliSearch is MIT licensed (100% free, self-hostable)
"""

import logging
import os
from datetime import datetime
from typing import Literal, TypedDict

import meilisearch
from meilisearch.errors import MeilisearchApiError

logger = logging.getLogger(__name__)

# Configuration
# Default uses Docker DNS (forge-meilisearch) for containerized environments
# Override with MEILISEARCH_URL env var for local development
MEILISEARCH_URL = os.getenv("MEILISEARCH_URL", "http://forge-meilisearch:7700")
MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY", "synapse_dev_key_change_in_prod")

# Index names
INDEX_ASSETS = "synapse_assets"
INDEX_RULES = "synapse_rules"
INDEX_CABLES = "synapse_cables"
INDEX_LOCATIONS = "synapse_locations"

ALL_INDEXES = [INDEX_ASSETS, INDEX_RULES, INDEX_CABLES, INDEX_LOCATIONS]


class SearchHit(TypedDict):
    """Search result hit from MeiliSearch"""
    id: str
    type: Literal["asset", "rule", "cable", "location"]
    title: str
    subtitle: str | None
    path: str | None
    score: float
    project_id: str | None
    metadata: dict | None


class MeiliSearchService:
    """MeiliSearch client wrapper for SYNAPSE"""

    def __init__(self):
        self._client: meilisearch.Client | None = None
        self._initialized = False

    @property
    def client(self) -> meilisearch.Client:
        """Lazy client initialization"""
        if self._client is None:
            self._client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
        return self._client

    def is_available(self) -> bool:
        """Check if MeiliSearch is available"""
        try:
            health = self.client.health()
            return health.get("status") == "available"
        except Exception as e:
            logger.warning(f"MeiliSearch not available: {e}")
            return False

    def initialize_indexes(self) -> dict[str, str]:
        """Create and configure all indexes with proper settings"""
        if self._initialized:
            return {"status": "already_initialized"}

        results = {}

        try:
            # Assets index
            self.client.create_index(INDEX_ASSETS, {"primaryKey": "id"})
            self.client.index(INDEX_ASSETS).update_settings({
                "searchableAttributes": [
                    "tag",
                    "description",
                    "system",
                    "area",
                    "io_type",
                    "discipline"
                ],
                "filterableAttributes": [
                    "project_id",
                    "discipline",
                    "system",
                    "area",
                    "io_type",
                    "type"
                ],
                "sortableAttributes": ["tag", "created_at"],
                "rankingRules": [
                    "words",
                    "typo",
                    "proximity",
                    "attribute",
                    "sort",
                    "exactness"
                ],
                "typoTolerance": {
                    "enabled": True,
                    "minWordSizeForTypos": {"oneTypo": 3, "twoTypos": 6}
                }
            })
            results[INDEX_ASSETS] = "configured"

            # Rules index
            self.client.create_index(INDEX_RULES, {"primaryKey": "id"})
            self.client.index(INDEX_RULES).update_settings({
                "searchableAttributes": ["name", "description", "trigger_type"],
                "filterableAttributes": ["project_id", "enabled", "priority", "trigger_type"],
                "sortableAttributes": ["name", "priority", "created_at"],
                "typoTolerance": {"enabled": True}
            })
            results[INDEX_RULES] = "configured"

            # Cables index
            self.client.create_index(INDEX_CABLES, {"primaryKey": "id"})
            self.client.index(INDEX_CABLES).update_settings({
                "searchableAttributes": [
                    "tag",
                    "description",
                    "from_location",
                    "to_location",
                    "cable_type"
                ],
                "filterableAttributes": [
                    "project_id",
                    "cable_type",
                    "from_location",
                    "to_location"
                ],
                "sortableAttributes": ["tag", "created_at"],
                "typoTolerance": {"enabled": True}
            })
            results[INDEX_CABLES] = "configured"

            # Locations index
            self.client.create_index(INDEX_LOCATIONS, {"primaryKey": "id"})
            self.client.index(INDEX_LOCATIONS).update_settings({
                "searchableAttributes": ["name", "code", "description"],
                "filterableAttributes": ["project_id", "type", "parent_id"],
                "sortableAttributes": ["name", "code"],
                "typoTolerance": {"enabled": True}
            })
            results[INDEX_LOCATIONS] = "configured"

            self._initialized = True
            logger.info("MeiliSearch indexes initialized successfully")

        except MeilisearchApiError as e:
            if "already exists" in str(e).lower():
                results["status"] = "indexes_already_exist"
                self._initialized = True
            else:
                logger.error(f"Failed to initialize indexes: {e}")
                raise

        return results

    def index_asset(self, asset: dict) -> dict:
        """Index a single asset"""
        doc = {
            "id": asset["id"],
            "type": "asset",
            "tag": asset.get("tag", ""),
            "description": asset.get("description", ""),
            "system": asset.get("system", ""),
            "area": asset.get("area", ""),
            "io_type": asset.get("io_type", ""),
            "discipline": asset.get("discipline", ""),
            "project_id": asset.get("project_id", ""),
            "created_at": asset.get("created_at", datetime.utcnow().isoformat()),
            "_entity_type": "asset"
        }
        return self.client.index(INDEX_ASSETS).add_documents([doc])

    def index_assets_batch(self, assets: list[dict]) -> dict:
        """Index multiple assets in batch (more efficient)"""
        docs = []
        for asset in assets:
            docs.append({
                "id": asset["id"],
                "type": "asset",
                "tag": asset.get("tag", ""),
                "description": asset.get("description", ""),
                "system": asset.get("system", ""),
                "area": asset.get("area", ""),
                "io_type": asset.get("io_type", ""),
                "discipline": asset.get("discipline", ""),
                "project_id": asset.get("project_id", ""),
                "created_at": str(asset.get("created_at", "")),
                "_entity_type": "asset"
            })
        return self.client.index(INDEX_ASSETS).add_documents(docs)

    def index_rule(self, rule: dict) -> dict:
        """Index a single rule"""
        doc = {
            "id": rule["id"],
            "type": "rule",
            "name": rule.get("name", ""),
            "description": rule.get("description", ""),
            "trigger_type": rule.get("trigger_type", ""),
            "enabled": rule.get("enabled", False),
            "priority": rule.get("priority", 0),
            "project_id": rule.get("project_id", ""),
            "created_at": str(rule.get("created_at", "")),
            "_entity_type": "rule"
        }
        return self.client.index(INDEX_RULES).add_documents([doc])

    def index_rules_batch(self, rules: list[dict]) -> dict:
        """Index multiple rules in batch"""
        docs = []
        for rule in rules:
            docs.append({
                "id": rule["id"],
                "type": "rule",
                "name": rule.get("name", ""),
                "description": rule.get("description", ""),
                "trigger_type": rule.get("trigger_type", ""),
                "enabled": rule.get("enabled", False),
                "priority": rule.get("priority", 0),
                "project_id": rule.get("project_id", ""),
                "created_at": str(rule.get("created_at", "")),
                "_entity_type": "rule"
            })
        return self.client.index(INDEX_RULES).add_documents(docs)

    def index_cable(self, cable: dict) -> dict:
        """Index a single cable"""
        doc = {
            "id": cable["id"],
            "type": "cable",
            "tag": cable.get("tag", ""),
            "description": cable.get("description", ""),
            "from_location": cable.get("from_location", ""),
            "to_location": cable.get("to_location", ""),
            "cable_type": cable.get("cable_type", ""),
            "length": cable.get("length"),
            "project_id": cable.get("project_id", ""),
            "created_at": str(cable.get("created_at", "")),
            "_entity_type": "cable"
        }
        return self.client.index(INDEX_CABLES).add_documents([doc])

    def index_cables_batch(self, cables: list[dict]) -> dict:
        """Index multiple cables in batch"""
        docs = []
        for cable in cables:
            docs.append({
                "id": cable["id"],
                "type": "cable",
                "tag": cable.get("tag", ""),
                "description": cable.get("description", ""),
                "from_location": cable.get("from_location", ""),
                "to_location": cable.get("to_location", ""),
                "cable_type": cable.get("cable_type", ""),
                "length": cable.get("length"),
                "project_id": cable.get("project_id", ""),
                "created_at": str(cable.get("created_at", "")),
                "_entity_type": "cable"
            })
        return self.client.index(INDEX_CABLES).add_documents(docs)

    def index_location(self, location: dict) -> dict:
        """Index a single location"""
        doc = {
            "id": location["id"],
            "type": "location",
            "name": location.get("name", ""),
            "code": location.get("code", ""),
            "description": location.get("description", ""),
            "parent_id": location.get("parent_id"),
            "project_id": location.get("project_id", ""),
            "_entity_type": "location"
        }
        return self.client.index(INDEX_LOCATIONS).add_documents([doc])

    def search(
        self,
        query: str,
        indexes: list[str] | None = None,
        project_id: str | None = None,
        filters: dict | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """
        Multi-index search across all entity types.

        Args:
            query: Search query (typo-tolerant)
            indexes: List of indexes to search (default: all)
            project_id: Filter by project
            filters: Additional filters per index
            limit: Max results per index
            offset: Pagination offset

        Returns:
            Combined search results from all indexes
        """
        if indexes is None:
            indexes = ALL_INDEXES

        # Build filter string
        filter_parts = []
        if project_id:
            filter_parts.append(f'project_id = "{project_id}"')

        filter_str = " AND ".join(filter_parts) if filter_parts else None

        # Multi-search query
        queries = []
        for index_name in indexes:
            search_params = {
                "indexUid": index_name,
                "q": query,
                "limit": limit,
                "offset": offset,
                "attributesToHighlight": ["*"],
                "highlightPreTag": "<mark>",
                "highlightPostTag": "</mark>"
            }
            if filter_str:
                search_params["filter"] = filter_str

            queries.append(search_params)

        results = self.client.multi_search(queries)

        # Format combined results
        all_hits: list[SearchHit] = []
        categories = {}

        for result in results.get("results", []):
            index_uid = result.get("indexUid", "")
            hits = result.get("hits", [])
            categories[index_uid] = len(hits)

            for hit in hits:
                entity_type = self._get_entity_type(index_uid)
                all_hits.append({
                    "id": hit.get("id"),
                    "type": entity_type,
                    "title": self._get_title(hit, entity_type),
                    "subtitle": self._get_subtitle(hit, entity_type),
                    "path": self._get_path(hit, entity_type),
                    "score": hit.get("_rankingScore", 0),
                    "project_id": hit.get("project_id"),
                    "metadata": self._get_metadata(hit, entity_type),
                    "_formatted": hit.get("_formatted", {})
                })

        # Sort by ranking score
        all_hits.sort(key=lambda x: x.get("score", 0), reverse=True)

        return {
            "query": query,
            "total": sum(categories.values()),
            "results": all_hits[:limit],
            "categories": categories,
            "processingTimeMs": sum(
                r.get("processingTimeMs", 0) for r in results.get("results", [])
            )
        }

    def _get_entity_type(self, index_uid: str) -> str:
        """Map index UID to entity type"""
        mapping = {
            INDEX_ASSETS: "asset",
            INDEX_RULES: "rule",
            INDEX_CABLES: "cable",
            INDEX_LOCATIONS: "location"
        }
        return mapping.get(index_uid, "unknown")

    def _get_title(self, hit: dict, entity_type: str) -> str:
        """Extract title based on entity type"""
        if entity_type == "asset":
            return hit.get("tag", "Unknown Asset")
        elif entity_type == "rule":
            return hit.get("name", "Unnamed Rule")
        elif entity_type == "cable":
            return hit.get("tag", "Unknown Cable")
        elif entity_type == "location":
            return hit.get("name") or hit.get("code", "Unknown Location")
        return hit.get("id", "Unknown")

    def _get_subtitle(self, hit: dict, entity_type: str) -> str | None:
        """Extract subtitle based on entity type"""
        if entity_type == "asset":
            parts = []
            if hit.get("description"):
                parts.append(hit["description"])
            if hit.get("system"):
                parts.append(hit["system"])
            return " • ".join(parts) if parts else None
        elif entity_type == "rule":
            return hit.get("description")
        elif entity_type == "cable":
            from_loc = hit.get("from_location", "")
            to_loc = hit.get("to_location", "")
            if from_loc and to_loc:
                return f"{from_loc} → {to_loc}"
            return hit.get("description")
        elif entity_type == "location":
            return f"Code: {hit.get('code')}" if hit.get("code") else None
        return None

    def _get_path(self, hit: dict, entity_type: str) -> str:
        """Generate navigation path"""
        return f"/{entity_type}s/{hit.get('id')}"

    def _get_metadata(self, hit: dict, entity_type: str) -> dict:
        """Extract relevant metadata"""
        if entity_type == "asset":
            return {
                "area": hit.get("area"),
                "system": hit.get("system"),
                "discipline": hit.get("discipline"),
                "io_type": hit.get("io_type")
            }
        elif entity_type == "rule":
            return {
                "enabled": hit.get("enabled"),
                "priority": hit.get("priority"),
                "trigger_type": hit.get("trigger_type")
            }
        elif entity_type == "cable":
            return {
                "cable_type": hit.get("cable_type"),
                "length": hit.get("length"),
                "from_location": hit.get("from_location"),
                "to_location": hit.get("to_location")
            }
        elif entity_type == "location":
            return {
                "code": hit.get("code"),
                "type": hit.get("type")
            }
        return {}

    def delete_document(self, index_name: str, doc_id: str) -> dict:
        """Delete a document from an index"""
        return self.client.index(index_name).delete_document(doc_id)

    def delete_all_documents(self, index_name: str) -> dict:
        """Delete all documents from an index"""
        return self.client.index(index_name).delete_all_documents()

    def get_stats(self) -> dict:
        """Get statistics for all indexes"""
        stats = {}
        for index_name in ALL_INDEXES:
            try:
                index_stats = self.client.index(index_name).get_stats()
                stats[index_name] = index_stats
            except MeilisearchApiError:
                stats[index_name] = {"error": "index_not_found"}
        return stats


# Singleton instance
_meilisearch_service: MeiliSearchService | None = None


def get_meilisearch_service() -> MeiliSearchService:
    """Get singleton MeiliSearch service instance"""
    global _meilisearch_service
    if _meilisearch_service is None:
        _meilisearch_service = MeiliSearchService()
    return _meilisearch_service
