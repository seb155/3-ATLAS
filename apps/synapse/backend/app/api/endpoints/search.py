"""
Global Search API Endpoint
Provides unified search with MeiliSearch (primary) + thefuzz fallback

Features:
- MeiliSearch for fast, typo-tolerant full-text search (~10ms for 10K+ docs)
- Automatic fallback to thefuzz when MeiliSearch unavailable
- Search across assets, rules, cables, locations
- Categorized results with relevance scoring
- Quick actions and navigation shortcuts
- Re-indexing API for data sync

MeiliSearch: MIT License - 100% Free, Self-Hostable
"""

import logging
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from thefuzz import fuzz

from app.core.database import get_db
from app.models import Asset, Cable, RuleDefinition
from app.models.models import LBSNode
from app.services.meilisearch_service import (
    ALL_INDEXES,
    INDEX_ASSETS,
    INDEX_CABLES,
    INDEX_LOCATIONS,
    INDEX_RULES,
    get_meilisearch_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchResult(BaseModel):
    """Individual search result"""
    id: str
    type: Literal["asset", "rule", "cable", "location", "project", "action", "navigation"]
    title: str
    subtitle: str | None = None
    icon: str | None = None
    path: str | None = None
    score: int = 0
    metadata: dict | None = None


class SearchResponse(BaseModel):
    """Search response with categorized results"""
    query: str
    total: int
    results: list[SearchResult]
    categories: dict[str, int]
    search_engine: str = "meilisearch"  # or "thefuzz" when fallback
    processing_time_ms: int | None = None


class IndexStatus(BaseModel):
    """Status of search index"""
    available: bool
    engine: str
    indexes: dict[str, dict] | None = None
    message: str | None = None


# Navigation shortcuts (always available, not indexed)
NAVIGATION_SHORTCUTS = [
    SearchResult(
        id="nav-dashboard", type="navigation", title="Dashboard",
        subtitle="Go to main dashboard", icon="LayoutDashboard", path="/dashboard"
    ),
    SearchResult(
        id="nav-assets", type="navigation", title="Assets",
        subtitle="View all assets and instruments", icon="Box", path="/assets"
    ),
    SearchResult(
        id="nav-rules", type="navigation", title="Rules",
        subtitle="Manage business rules", icon="GitBranch", path="/rules"
    ),
    SearchResult(
        id="nav-cables", type="navigation", title="Cables",
        subtitle="Cable management", icon="Cable", path="/cables"
    ),
    SearchResult(
        id="nav-import", type="navigation", title="Import CSV",
        subtitle="Import data from CSV files", icon="Upload", path="/import"
    ),
    SearchResult(
        id="nav-export", type="navigation", title="Export Package",
        subtitle="Generate export packages", icon="Download", path="/export"
    ),
    SearchResult(
        id="nav-settings", type="navigation", title="Settings",
        subtitle="Application settings", icon="Settings", path="/settings"
    ),
    SearchResult(
        id="nav-metamodel", type="navigation", title="Metamodel Graph",
        subtitle="View system relationships", icon="Network", path="/metamodel"
    ),
]

# Quick actions (always available, not indexed)
QUICK_ACTIONS = [
    SearchResult(
        id="action-new-asset", type="action", title="Create New Asset",
        subtitle="Add a new instrument or equipment", icon="Plus",
        path="/assets/new", metadata={"action": "create", "entity": "asset"}
    ),
    SearchResult(
        id="action-new-rule", type="action", title="Create New Rule",
        subtitle="Define a new business rule", icon="Plus",
        path="/rules/new", metadata={"action": "create", "entity": "rule"}
    ),
    SearchResult(
        id="action-run-rules", type="action", title="Run All Rules",
        subtitle="Execute all active rules", icon="Play",
        path="/rules/run", metadata={"action": "execute", "entity": "rules"}
    ),
    SearchResult(
        id="action-ai-classify", type="action", title="AI Auto-Classify",
        subtitle="Classify untagged instruments with AI", icon="Sparkles",
        path="/assets/classify", metadata={"action": "ai", "entity": "assets"}
    ),
]


def calculate_fuzzy_score(query: str, text: str) -> int:
    """Calculate fuzzy match score (0-100) - used for fallback"""
    if not query or not text:
        return 0
    ratio = fuzz.ratio(query.lower(), text.lower())
    partial = fuzz.partial_ratio(query.lower(), text.lower())
    token_sort = fuzz.token_sort_ratio(query.lower(), text.lower())
    return int(ratio * 0.3 + partial * 0.5 + token_sort * 0.2)


def search_navigation_and_actions(query: str, type_filter: list[str] | None) -> list[SearchResult]:
    """Search through navigation shortcuts and quick actions"""
    results = []
    query_lower = query.lower()

    if not type_filter or "navigation" in type_filter:
        for nav in NAVIGATION_SHORTCUTS:
            score = calculate_fuzzy_score(query, nav.title)
            if score >= 40 or query_lower in nav.title.lower():
                nav_copy = nav.model_copy()
                nav_copy.score = score
                results.append(nav_copy)

    if not type_filter or "action" in type_filter:
        for action in QUICK_ACTIONS:
            score = calculate_fuzzy_score(query, action.title)
            if score >= 40 or query_lower in action.title.lower():
                action_copy = action.model_copy()
                action_copy.score = score
                results.append(action_copy)

    return results


async def search_with_meilisearch(
    query: str,
    type_filter: list[str] | None,
    project_id: str | None,
    limit: int
) -> tuple[list[SearchResult], dict[str, int], int]:
    """Search using MeiliSearch engine"""
    meili = get_meilisearch_service()

    # Map type filter to indexes
    indexes = []
    if not type_filter:
        indexes = ALL_INDEXES
    else:
        if "asset" in type_filter:
            indexes.append(INDEX_ASSETS)
        if "rule" in type_filter:
            indexes.append(INDEX_RULES)
        if "cable" in type_filter:
            indexes.append(INDEX_CABLES)
        if "location" in type_filter:
            indexes.append(INDEX_LOCATIONS)

    if not indexes:
        return [], {}, 0

    # Perform search
    meili_results = meili.search(
        query=query,
        indexes=indexes,
        project_id=project_id,
        limit=limit
    )

    # Convert to SearchResult format
    results = []
    for hit in meili_results.get("results", []):
        icon_map = {"asset": "Cpu", "rule": "GitBranch", "cable": "Cable", "location": "MapPin"}
        results.append(SearchResult(
            id=hit["id"],
            type=hit["type"],
            title=hit["title"],
            subtitle=hit.get("subtitle"),
            icon=icon_map.get(hit["type"], "File"),
            path=hit.get("path"),
            score=int(hit.get("score", 0) * 100),
            metadata=hit.get("metadata")
        ))

    # Map categories from MeiliSearch index names to types
    categories = {}
    for idx_name, count in meili_results.get("categories", {}).items():
        type_name = idx_name.replace("synapse_", "").rstrip("s")  # synapse_assets -> asset
        categories[type_name] = count

    return results, categories, meili_results.get("processingTimeMs", 0)


async def search_with_fallback(
    query: str,
    type_filter: list[str] | None,
    project_id: str | None,
    limit: int,
    db: Session
) -> tuple[list[SearchResult], dict[str, int]]:
    """Fallback search using thefuzz + database queries"""
    results = []
    categories = {}

    # Search Assets
    if not type_filter or "asset" in type_filter:
        asset_query = db.query(Asset).filter(
            or_(
                Asset.tag.ilike(f"%{query}%"),
                Asset.description.ilike(f"%{query}%"),
                Asset.system.ilike(f"%{query}%"),
                Asset.area.ilike(f"%{query}%")
            )
        )
        if project_id:
            asset_query = asset_query.filter(Asset.project_id == project_id)

        assets = asset_query.limit(limit).all()
        for asset in assets:
            score = max(
                calculate_fuzzy_score(query, asset.tag or ""),
                calculate_fuzzy_score(query, asset.description or ""),
                calculate_fuzzy_score(query, asset.system or "")
            )
            results.append(SearchResult(
                id=asset.id, type="asset",
                title=asset.tag or "Unknown",
                subtitle=f"{asset.description or ''} • {asset.system or 'Unclassified'}",
                icon="Cpu", path=f"/assets/{asset.id}", score=score,
                metadata={"area": asset.area, "system": asset.system}
            ))
        categories["asset"] = len(assets)

    # Search Rules
    if not type_filter or "rule" in type_filter:
        rule_query = db.query(RuleDefinition).filter(
            or_(
                RuleDefinition.name.ilike(f"%{query}%"),
                RuleDefinition.description.ilike(f"%{query}%")
            )
        )
        if project_id:
            rule_query = rule_query.filter(RuleDefinition.project_id == project_id)

        rules = rule_query.limit(limit).all()
        for rule in rules:
            score = max(
                calculate_fuzzy_score(query, rule.name or ""),
                calculate_fuzzy_score(query, rule.description or "")
            )
            results.append(SearchResult(
                id=rule.id, type="rule",
                title=rule.name or "Unnamed Rule",
                subtitle=rule.description or "No description",
                icon="GitBranch", path=f"/rules/{rule.id}", score=score,
                metadata={"enabled": rule.enabled, "priority": rule.priority}
            ))
        categories["rule"] = len(rules)

    # Search Cables
    if not type_filter or "cable" in type_filter:
        cable_query = db.query(Cable).filter(
            or_(
                Cable.tag.ilike(f"%{query}%"),
                Cable.description.ilike(f"%{query}%"),
                Cable.from_location.ilike(f"%{query}%"),
                Cable.to_location.ilike(f"%{query}%")
            )
        )
        if project_id:
            cable_query = cable_query.filter(Cable.project_id == project_id)

        cables = cable_query.limit(limit).all()
        for cable in cables:
            score = max(
                calculate_fuzzy_score(query, cable.tag or ""),
                calculate_fuzzy_score(query, cable.description or "")
            )
            results.append(SearchResult(
                id=cable.id, type="cable",
                title=cable.tag or "Unknown Cable",
                subtitle=f"{cable.from_location} → {cable.to_location}" if cable.from_location else cable.description,
                icon="Cable", path=f"/cables/{cable.id}", score=score,
                metadata={"cableType": cable.cable_type, "length": cable.length}
            ))
        categories["cable"] = len(cables)

    # Search Locations
    if not type_filter or "location" in type_filter:
        location_query = db.query(LBSNode).filter(
            or_(LBSNode.name.ilike(f"%{query}%"), LBSNode.code.ilike(f"%{query}%"))
        )
        if project_id:
            location_query = location_query.filter(LBSNode.project_id == project_id)

        locations = location_query.limit(limit).all()
        for loc in locations:
            score = max(
                calculate_fuzzy_score(query, loc.name or ""),
                calculate_fuzzy_score(query, loc.code or "")
            )
            results.append(SearchResult(
                id=loc.id, type="location",
                title=loc.name or loc.code or "Unknown Location",
                subtitle=f"Code: {loc.code}" if loc.code else None,
                icon="MapPin", path=f"/locations/{loc.id}", score=score,
                metadata={"type": str(loc.type) if loc.type else None, "code": loc.code}
            ))
        categories["location"] = len(locations)

    return results, categories


@router.get("/", response_model=SearchResponse)
async def global_search(
    q: str = Query("", min_length=0, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Max results"),
    types: str | None = Query(None, description="Filter by types: asset,rule,cable,navigation,action"),
    project_id: str | None = Query(None, description="Filter by project"),
    db: Session = Depends(get_db)
):
    """
    Global search across all entities.

    Uses MeiliSearch for fast, typo-tolerant search (~10ms).
    Falls back to database + thefuzz when MeiliSearch unavailable.
    """
    type_filter = types.split(",") if types else None

    # Empty query: return navigation shortcuts and actions
    if not q or len(q) < 1:
        results = []
        if not type_filter or "navigation" in type_filter:
            results.extend(NAVIGATION_SHORTCUTS)
        if not type_filter or "action" in type_filter:
            results.extend(QUICK_ACTIONS)

        return SearchResponse(
            query=q,
            total=len(results),
            results=results[:limit],
            categories={"navigation": len(NAVIGATION_SHORTCUTS), "action": len(QUICK_ACTIONS)},
            search_engine="static"
        )

    # Search navigation and actions first
    nav_results = search_navigation_and_actions(q, type_filter)

    # Try MeiliSearch first
    meili = get_meilisearch_service()
    search_engine = "meilisearch"
    processing_time = None

    if meili.is_available():
        try:
            entity_results, categories, processing_time = await search_with_meilisearch(
                q, type_filter, project_id, limit
            )
        except Exception as e:
            logger.warning(f"MeiliSearch failed, using fallback: {e}")
            entity_results, categories = await search_with_fallback(
                q, type_filter, project_id, limit, db
            )
            search_engine = "thefuzz_fallback"
    else:
        entity_results, categories = await search_with_fallback(
            q, type_filter, project_id, limit, db
        )
        search_engine = "thefuzz"

    # Combine results
    all_results = nav_results + entity_results
    all_results.sort(key=lambda x: x.score, reverse=True)

    # Add nav/action counts to categories
    categories["navigation"] = len([r for r in nav_results if r.type == "navigation"])
    categories["action"] = len([r for r in nav_results if r.type == "action"])

    return SearchResponse(
        query=q,
        total=len(all_results),
        results=all_results[:limit],
        categories=categories,
        search_engine=search_engine,
        processing_time_ms=processing_time
    )


@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get autocomplete suggestions for quick navigation."""
    suggestions = []
    query_lower = q.lower()

    # Check navigation shortcuts first
    for nav in NAVIGATION_SHORTCUTS:
        if query_lower in nav.title.lower():
            suggestions.append({"text": nav.title, "type": "navigation", "path": nav.path})

    # Try MeiliSearch for fast suggestions
    meili = get_meilisearch_service()
    if meili.is_available():
        try:
            results = meili.search(q, limit=limit)
            for hit in results.get("results", [])[:limit]:
                suggestions.append({
                    "text": hit["title"],
                    "type": hit["type"],
                    "path": hit.get("path", f"/{hit['type']}s/{hit['id']}")
                })
            return suggestions[:limit]
        except Exception:
            pass  # Fall through to database

    # Fallback to database
    assets = db.query(Asset.tag).filter(Asset.tag.ilike(f"{q}%")).distinct().limit(limit).all()
    for (tag,) in assets:
        if tag:
            suggestions.append({"text": tag, "type": "asset", "path": f"/assets?search={tag}"})

    rules = db.query(RuleDefinition.name).filter(
        RuleDefinition.name.ilike(f"{q}%")
    ).distinct().limit(limit).all()
    for (name,) in rules:
        if name:
            suggestions.append({"text": name, "type": "rule", "path": f"/rules?search={name}"})

    return suggestions[:limit]


@router.get("/recent")
async def get_recent_searches():
    """Get recent search queries (stored per-user in localStorage on frontend)."""
    return {"recent": [], "message": "Recent searches stored client-side in localStorage"}


# =============================================================================
# MeiliSearch Management Endpoints
# =============================================================================

@router.get("/status", response_model=IndexStatus)
async def get_search_status():
    """Get search engine status and index statistics."""
    meili = get_meilisearch_service()

    if meili.is_available():
        try:
            stats = meili.get_stats()
            return IndexStatus(
                available=True,
                engine="meilisearch",
                indexes=stats,
                message="MeiliSearch is healthy"
            )
        except Exception as e:
            return IndexStatus(
                available=False,
                engine="meilisearch",
                message=f"Error getting stats: {e}"
            )
    else:
        return IndexStatus(
            available=False,
            engine="thefuzz_fallback",
            message="MeiliSearch unavailable, using database fallback"
        )


@router.post("/reindex")
async def reindex_all(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Reindex all data from database to MeiliSearch.
    Runs in background for large datasets.
    """
    meili = get_meilisearch_service()

    if not meili.is_available():
        raise HTTPException(status_code=503, detail="MeiliSearch is not available")

    # Initialize indexes
    meili.initialize_indexes()

    # Schedule reindexing in background
    background_tasks.add_task(_reindex_all_data, db)

    return {
        "status": "started",
        "message": "Reindexing started in background. Check /search/status for progress."
    }


async def _reindex_all_data(db: Session):
    """Background task to reindex all data"""
    meili = get_meilisearch_service()

    try:
        # Reindex assets
        assets = db.query(Asset).all()
        if assets:
            asset_docs = [
                {
                    "id": a.id,
                    "tag": a.tag or "",
                    "description": a.description or "",
                    "system": a.system or "",
                    "area": a.area or "",
                    "io_type": str(a.io_type) if a.io_type else "",
                    "discipline": a.discipline or "",
                    "project_id": a.project_id or "",
                    "created_at": str(a.created_at) if a.created_at else ""
                }
                for a in assets
            ]
            meili.index_assets_batch(asset_docs)
            logger.info(f"Indexed {len(assets)} assets")

        # Reindex rules
        rules = db.query(RuleDefinition).all()
        if rules:
            rule_docs = [
                {
                    "id": r.id,
                    "name": r.name or "",
                    "description": r.description or "",
                    "trigger_type": r.trigger_type or "",
                    "enabled": r.enabled,
                    "priority": r.priority or 0,
                    "project_id": r.project_id or "",
                    "created_at": str(r.created_at) if r.created_at else ""
                }
                for r in rules
            ]
            meili.index_rules_batch(rule_docs)
            logger.info(f"Indexed {len(rules)} rules")

        # Reindex cables
        cables = db.query(Cable).all()
        if cables:
            cable_docs = [
                {
                    "id": c.id,
                    "tag": c.tag or "",
                    "description": c.description or "",
                    "from_location": c.from_location or "",
                    "to_location": c.to_location or "",
                    "cable_type": c.cable_type or "",
                    "length": c.length,
                    "project_id": c.project_id or "",
                    "created_at": str(c.created_at) if c.created_at else ""
                }
                for c in cables
            ]
            meili.index_cables_batch(cable_docs)
            logger.info(f"Indexed {len(cables)} cables")

        # Reindex locations
        locations = db.query(LBSNode).all()
        if locations:
            location_docs = [
                {
                    "id": loc.id,
                    "name": loc.name or "",
                    "code": loc.code or "",
                    "description": "",
                    "parent_id": loc.parent_id,
                    "project_id": loc.project_id or "",
                    "type": str(loc.type) if loc.type else ""
                }
                for loc in locations
            ]
            meili.client.index(INDEX_LOCATIONS).add_documents(location_docs)
            logger.info(f"Indexed {len(locations)} locations")

        logger.info("Reindexing completed successfully")

    except Exception as e:
        logger.error(f"Reindexing failed: {e}")
        raise


@router.post("/reindex/{entity_type}")
async def reindex_entity_type(
    entity_type: Literal["assets", "rules", "cables", "locations"],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reindex a specific entity type."""
    meili = get_meilisearch_service()

    if not meili.is_available():
        raise HTTPException(status_code=503, detail="MeiliSearch is not available")

    # Map entity type to reindex function
    if entity_type == "assets":
        assets = db.query(Asset).all()
        docs = [
            {
                "id": a.id,
                "tag": a.tag or "",
                "description": a.description or "",
                "system": a.system or "",
                "area": a.area or "",
                "project_id": a.project_id or ""
            }
            for a in assets
        ]
        meili.index_assets_batch(docs)
        return {"indexed": len(docs), "type": "assets"}

    elif entity_type == "rules":
        rules = db.query(RuleDefinition).all()
        docs = [
            {
                "id": r.id,
                "name": r.name or "",
                "description": r.description or "",
                "project_id": r.project_id or ""
            }
            for r in rules
        ]
        meili.index_rules_batch(docs)
        return {"indexed": len(docs), "type": "rules"}

    elif entity_type == "cables":
        cables = db.query(Cable).all()
        docs = [
            {
                "id": c.id,
                "tag": c.tag or "",
                "description": c.description or "",
                "project_id": c.project_id or ""
            }
            for c in cables
        ]
        meili.index_cables_batch(docs)
        return {"indexed": len(docs), "type": "cables"}

    elif entity_type == "locations":
        locations = db.query(LBSNode).all()
        docs = [
            {
                "id": loc.id,
                "name": loc.name or "",
                "code": loc.code or "",
                "project_id": loc.project_id or ""
            }
            for loc in locations
        ]
        meili.client.index(INDEX_LOCATIONS).add_documents(docs)
        return {"indexed": len(docs), "type": "locations"}
