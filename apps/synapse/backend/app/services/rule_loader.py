"""
Rule Loader Service

Loads applicable rules for a project in priority order.
Implements hierarchical rule loading: CLIENT > PROJECT > COUNTRY > FIRM
"""


from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.auth import Project
from app.models.rules import RuleDefinition, RuleSource


class RuleLoader:
    """
    Loads applicable rules for a project in priority order.
    """

    @staticmethod
    def load_rules_for_project(db: Session, project_id: str) -> list[RuleDefinition]:
        """
        Load all applicable rules for a project.

        Priority order: CLIENT (100) > PROJECT (50) > COUNTRY (30) > FIRM (10)

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            List of RuleDefinition objects sorted by priority (descending)
        """
        # Get project context
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        client_id = project.client_id
        country = getattr(project, "country", None)

        # Build query for applicable rules
        query = db.query(RuleDefinition).filter(RuleDefinition.is_active.is_(True))

        # Filter by source - Include: FIRM rules + COUNTRY rules + PROJECT rules + CLIENT rules
        source_filters = [RuleDefinition.source == RuleSource.FIRM]

        if country:
            source_filters.append(
                (RuleDefinition.source == RuleSource.COUNTRY)
                & (RuleDefinition.source_id == country)
            )

        source_filters.append(
            (RuleDefinition.source == RuleSource.PROJECT) & (RuleDefinition.source_id == project_id)
        )

        if client_id:
            source_filters.append(
                (RuleDefinition.source == RuleSource.CLIENT)
                & (RuleDefinition.source_id == client_id)
            )

        # Combine filters with OR
        query = query.filter(or_(*source_filters))

        # Sort by priority (descending: highest priority first)
        query = query.order_by(RuleDefinition.priority.desc(), RuleDefinition.created_at.asc())

        rules = query.all()

        print(f"[RuleLoader] Loaded {len(rules)} rules for project {project_id}")
        if rules:
            print("[RuleLoader] Rule breakdown:")
            print(f"  - FIRM: {sum(1 for r in rules if r.source == RuleSource.FIRM)}")
            print(f"  - COUNTRY: {sum(1 for r in rules if r.source == RuleSource.COUNTRY)}")
            print(f"  - PROJECT: {sum(1 for r in rules if r.source == RuleSource.PROJECT)}")
            print(f"  - CLIENT: {sum(1 for r in rules if r.source == RuleSource.CLIENT)}")

        return rules

    @staticmethod
    def load_rules_by_action_type(
        db: Session, project_id: str, action_type: str
    ) -> list[RuleDefinition]:
        """
        Load rules for a specific action type.

        Args:
            db: Database session
            project_id: Project ID
            action_type: Action type to filter (e.g., "CREATE_CHILD")

        Returns:
            List of rules matching the action type
        """
        all_rules = RuleLoader.load_rules_for_project(db, project_id)
        return [r for r in all_rules if r.action_type.value == action_type]

    @staticmethod
    def load_rules_by_discipline(
        db: Session, project_id: str, discipline: str
    ) -> list[RuleDefinition]:
        """
        Load rules for a specific discipline.

        Args:
            db: Database session
            project_id: Project ID
            discipline: Discipline to filter (e.g., "ELECTRICAL")

        Returns:
            List of rules matching the discipline
        """
        all_rules = RuleLoader.load_rules_for_project(db, project_id)
        return [r for r in all_rules if r.discipline == discipline]
