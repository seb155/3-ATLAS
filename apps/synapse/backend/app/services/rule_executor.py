"""
Rule Executor Service

Executes individual rules on assets with full audit trail logging.
"""

import time
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.metamodel import MetamodelEdge
from app.models.models import Asset
from app.models.rules import RuleDefinition, RuleExecution


class RuleExecutor:
    """
    Executes individual rules on assets.
    """

    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    @staticmethod
    def _get_asset_tag(asset) -> str:
        """Get tag from Asset or name from MetamodelNode"""
        return getattr(asset, 'tag', None) or getattr(asset, 'name', 'UNKNOWN')

    def execute_rule(self, rule: RuleDefinition, asset: Asset) -> RuleExecution:
        """
        Execute a single rule on a single asset.

        Args:
            rule: Rule to execute
            asset: Asset to apply rule to

        Returns:
            RuleExecution object (audit log entry)
        """
        start_time = time.time()

        try:
            # Evaluate condition
            condition_matched = self._evaluate_condition(rule.condition, asset)

            if not condition_matched:
                # Log SKIP
                return self._log_execution(
                    rule=rule,
                    asset=asset,
                    action_type="SKIP",
                    action_taken=f"Condition not matched for {self._get_asset_tag(asset)}",
                    condition_matched=False,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # Execute action based on action_type
            if rule.action_type.value == "CREATE_CHILD":
                return self._execute_create_child(rule, asset, start_time)
            elif rule.action_type.value == "CREATE_CABLE":
                return self._execute_create_cable(rule, asset, start_time)
            elif rule.action_type.value == "SET_PROPERTY":
                return self._execute_set_property(rule, asset, start_time)
            elif rule.action_type.value == "CREATE_RELATIONSHIP":
                return self._execute_create_relationship(rule, asset, start_time)
            elif rule.action_type.value == "CREATE_PACKAGE":
                return self._execute_create_package(rule, asset, start_time)
            elif rule.action_type.value == "ALLOCATE_IO":
                return self._execute_allocate_io(rule, asset, start_time)
            elif rule.action_type.value == "VALIDATE":
                return self._execute_validate(rule, asset, start_time)
            else:
                return self._log_execution(
                    rule=rule,
                    asset=asset,
                    action_type="SKIP",
                    action_taken=f"Action type {rule.action_type.value} not yet implemented",
                    condition_matched=True,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

        except Exception as e:
            # Capture IDs before rollback (objects may be detached after rollback)
            import traceback
            rule_id = str(rule.id) if hasattr(rule, 'id') else "unknown"
            asset_id = str(asset.id) if hasattr(asset, 'id') else "unknown"
            asset_tag = self._get_asset_tag(asset) if asset else "unknown"
            error_msg = str(e)
            stack = traceback.format_exc()
            exec_time = int((time.time() - start_time) * 1000)

            # Log ERROR
            self.db.rollback()

            # Create execution log with captured values
            execution = RuleExecution(
                rule_id=rule_id,
                project_id=self.project_id,
                asset_id=asset_id,
                action_type="ERROR",
                action_taken=f"Error executing rule: {error_msg}",
                condition_matched=True,
                error_message=error_msg,
                stack_trace=stack,
                execution_time_ms=exec_time,
            )
            self.db.add(execution)
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
            return execution

    def _evaluate_condition(self, condition: dict[str, Any], asset: Asset) -> bool:
        """
        Evaluate if condition matches asset.

        Condition example:
        {
            "asset_type": "PUMP",
            "property_filters": [
                {"key": "voltage", "op": "==", "value": "600V"}
            ]
        }
        """
        # Check asset_type
        if "asset_type" in condition:
            if asset.type != condition["asset_type"]:
                return False

        # Check node_type (for non-asset nodes like AREA)
        if "node_type" in condition:
            if asset.type != condition["node_type"]:
                return False

        # Check property filters
        if "property_filters" in condition and condition["property_filters"]:
            for filter_item in condition["property_filters"]:
                key = filter_item["key"]
                op = filter_item["op"]
                value = filter_item["value"]

                # Get property value from asset
                asset_value = asset.properties.get(key) if asset.properties else None

                # Evaluate operator
                if not self._evaluate_operator(asset_value, op, value):
                    return False

        return True

    def _evaluate_operator(self, asset_value: Any, op: str, expected_value: Any) -> bool:
        """Evaluate comparison operator"""
        if op == "==":
            return asset_value == expected_value
        elif op == "!=":
            return asset_value != expected_value
        elif op == ">":
            return asset_value is not None and asset_value > expected_value
        elif op == "<":
            return asset_value is not None and asset_value < expected_value
        elif op == ">=":
            return asset_value is not None and asset_value >= expected_value
        elif op == "<=":
            return asset_value is not None and asset_value <= expected_value
        elif op == "in":
            return asset_value in expected_value if isinstance(expected_value, list) else False
        elif op == "contains":
            return expected_value in asset_value if isinstance(asset_value, str | list) else False
        else:
            return False

    def _execute_create_child(
        self, rule: RuleDefinition, asset: Asset, start_time: float
    ) -> RuleExecution:
        """Execute CREATE_CHILD action"""
        action = rule.action.get("create_child", {})

        child_type = action["type"]
        relation = action.get("relation", "related_to")
        naming = action.get("naming", "{parent_tag}-{type}")
        semantic_type = action.get("semantic_type", "ASSET")

        # Generate child name
        # Support both Asset (tag) and MetamodelNode (name)
        parent_tag = getattr(asset, 'tag', None) or getattr(asset, 'name', 'UNKNOWN')
        child_name = naming.replace("{parent_tag}", parent_tag).replace("{type}", child_type[:1])

        # Check if child already exists (idempotency)
        existing_child = (
            self.db.query(Asset)
            .filter(Asset.tag == child_name, Asset.project_id == self.project_id)
            .first()
        )

        if existing_child:
            # Check if edge exists
            existing_edge = (
                self.db.query(MetamodelEdge)
                .filter(
                    MetamodelEdge.source_node_id == existing_child.id,
                    MetamodelEdge.target_node_id == asset.id,
                    MetamodelEdge.relation_type == relation,
                )
                .first()
            )

            if existing_edge:
                return self._log_execution(
                    rule=rule,
                    asset=asset,
                    action_type="SKIP",
                    action_taken=f"Child {child_name} already exists and is linked to {self._get_asset_tag(asset)}",
                    condition_matched=True,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

        # Create child properties
        child_properties = action.get("properties", {}).copy()

        # Inherit properties if specified
        if "inherit_properties" in action and asset.properties:
            for prop_key in action["inherit_properties"]:
                if prop_key in asset.properties:
                    child_properties[prop_key] = asset.properties[prop_key]

        # Create child asset (unified model!)
        # Get discipline (handle both string and enum)
        discipline_value = action.get("discipline")
        if not discipline_value and rule.discipline:
            discipline_value = rule.discipline.value if hasattr(rule.discipline, 'value') else rule.discipline

        child = Asset(
            tag=child_name,
            type=child_type,  # Now String, not Enum
            project_id=self.project_id,
            semantic_type=semantic_type,
            discipline=discipline_value,
            properties=child_properties,
        )

        self.db.add(child)
        self.db.flush()  # Get child.id

        # Create edge
        edge = MetamodelEdge(
            source_node_id=child.id,
            target_node_id=asset.id,
            relation_type=relation,
            discipline=rule.discipline,
        )
        self.db.add(edge)
        self.db.commit()

        return self._log_execution(
            rule=rule,
            asset=asset,
            action_type="CREATE",
            action_taken=f"Created {child_type} {child_name} for {self._get_asset_tag(asset)}",
            condition_matched=True,
            created_entity_id=child.id,
            created_entity_type=child_type,
            execution_time_ms=int((time.time() - start_time) * 1000),
        )

    def _execute_create_cable(
        self, rule: RuleDefinition, asset: Asset, start_time: float
    ) -> RuleExecution:
        """Execute CREATE_CABLE action"""
        from app.models.cables import Cable
        from app.services.cable_sizing import CableSizingService

        action = rule.action.get("create_cable", {})

        # 1. Parse configuration
        cable_tag_pattern = action.get("cable_tag", "{tag}-CBL")
        cable_type = action.get("cable_type", "UNKNOWN")
        sizing_method = action.get("sizing_method", "Manual")
        length_meters = action.get("length_meters", 50.0)
        voltage_str = action.get("voltage", "600V")

        # 2. Resolve tag
        cable_tag = cable_tag_pattern.replace("{tag}", self._get_asset_tag(asset))

        # 3. Check existence
        existing_cable = (
            self.db.query(Cable)
            .filter(Cable.tag == cable_tag, Cable.project_id == self.project_id)
            .first()
        )

        if existing_cable:
            return self._log_execution(
                rule=rule,
                asset=asset,
                action_type="SKIP",
                action_taken=f"Cable {cable_tag} already exists",
                condition_matched=True,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # 4. Perform Sizing (if Auto)
        sizing_result = {}
        if sizing_method == "Auto" and asset.type == "MOTOR":
            # Try to get HP from properties
            hp = asset.properties.get("hp")
            if hp:
                try:
                    hp_val = float(hp)
                    sizing_result = CableSizingService.size_cable(
                        hp=hp_val, length_meters=length_meters, voltage_str=voltage_str
                    )
                except Exception as e:
                    print(f"Error sizing cable for {self._get_asset_tag(asset)}: {e}")

        # 5. Create Cable Entity
        # Map sizing results to Cable model fields
        conductor_size = sizing_result.get("cable_size")
        voltage_drop_percent = sizing_result.get("voltage_drop_percent")
        voltage_drop_volts = sizing_result.get("voltage_drop_volts")

        cable = Cable(
            tag=cable_tag,
            project_id=self.project_id,
            cable_type=cable_type,
            description=f"Power cable for {self._get_asset_tag(asset)}",
            # Connections
            to_asset_id=asset.id,
            # from_asset_id would be set if we could resolve the source (e.g. MCC)
            # Specs
            length_meters=length_meters,
            conductor_size=conductor_size,
            voltage_drop_percent=voltage_drop_percent,
            voltage_drop_volts=voltage_drop_volts,
            # Standards
            code_standard="CEC-2021",
            # Rule tracking
            created_by_rule_id=rule.id,
            # Extra properties
            properties={
                "sizing_method": sizing_method,
                "insulation": action.get("insulation", "RW90 XLPE"),
                "voltage_drop_limit": action.get("voltage_drop_limit", 3.0),
                **sizing_result,
            },
        )

        self.db.add(cable)
        self.db.flush()

        # 5.5 Create Metamodel Node for Cable
        # Note: MetamodelService might need update to handle Cable model if it expects Asset
        # For now, we'll skip creating a MetamodelNode for the cable itself to avoid type issues,
        # or we treat it as a special node.
        # Let's create the edge directly between the source (if known) and target,
        # OR just leave it as a data entity for the schedule.
        # The original code created a node. Let's stick to creating the Cable entity first.

        self.db.commit()

        action_msg = f"Created Cable {cable_tag} for {self._get_asset_tag(asset)}"
        if sizing_result:
            action_msg += f" (Sized: {sizing_result.get('cable_size', 'Unknown')})"

        return self._log_execution(
            rule=rule,
            asset=asset,
            action_type="CREATE",
            action_taken=action_msg,
            condition_matched=True,
            created_entity_id=str(cable.id),
            created_entity_type="CABLE",
            execution_time_ms=int((time.time() - start_time) * 1000),
        )

    def _execute_set_property(
        self, rule: RuleDefinition, asset: Asset, start_time: float
    ) -> RuleExecution:
        """Execute SET_PROPERTY action"""
        action = rule.action.get("set_property", {})

        # Update properties
        if asset.properties is None:
            asset.properties = {}

        updated_keys = []
        for key, value in action.items():
            asset.properties[key] = value
            updated_keys.append(key)

        # Mark JSON field as modified for SQLAlchemy to track the change
        flag_modified(asset, "properties")
        self.db.commit()

        return self._log_execution(
            rule=rule,
            asset=asset,
            action_type="UPDATE",
            action_taken=f"Updated properties of {self._get_asset_tag(asset)}: {', '.join(updated_keys)}",
            condition_matched=True,
            execution_time_ms=int((time.time() - start_time) * 1000),
        )

    def _execute_create_relationship(
        self, rule: RuleDefinition, asset: Asset, start_time: float
    ) -> RuleExecution:
        """Execute CREATE_RELATIONSHIP action"""
        action = rule.action.get("create_relationship", {})

        relation_type = action.get("relation", "related_to")
        target_tag_pattern = action.get("target_tag")
        direction = action.get(
            "direction", "outgoing"
        )  # outgoing: asset -> target, incoming: target -> asset

        if not target_tag_pattern:
            return self._log_execution(
                rule=rule,
                asset=asset,
                action_type="ERROR",
                action_taken="Missing target_tag in create_relationship action",
                condition_matched=True,
                error_message="Missing target_tag",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Resolve target tag
        target_tag = target_tag_pattern.replace("{tag}", self._get_asset_tag(asset))

        # Find target asset
        target_asset = (
            self.db.query(Asset)
            .filter(Asset.tag == target_tag, Asset.project_id == self.project_id)
            .first()
        )

        if not target_asset:
            return self._log_execution(
                rule=rule,
                asset=asset,
                action_type="SKIP",
                action_taken=f"Target asset {target_tag} not found",
                condition_matched=True,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Check if edge exists
        if direction == "outgoing":
            source_id = asset.id
            target_id = target_asset.id
        else:
            source_id = target_asset.id
            target_id = asset.id

        existing_edge = (
            self.db.query(MetamodelEdge)
            .filter(
                MetamodelEdge.source_node_id == source_id,
                MetamodelEdge.target_node_id == target_id,
                MetamodelEdge.relation_type == relation_type,
            )
            .first()
        )

        if existing_edge:
            return self._log_execution(
                rule=rule,
                asset=asset,
                action_type="SKIP",
                action_taken=f"Relationship {relation_type} to {target_tag} already exists",
                condition_matched=True,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Create edge
        edge = MetamodelEdge(
            source_node_id=source_id,
            target_node_id=target_id,
            relation_type=relation_type,
            discipline=rule.discipline,
        )
        self.db.add(edge)
        self.db.commit()

        return self._log_execution(
            rule=rule,
            asset=asset,
            action_type="CREATE",
            action_taken=f"Created relationship {relation_type} to {target_tag}",
            condition_matched=True,
            created_entity_id=edge.id,
            created_entity_type="EDGE",
            execution_time_ms=int((time.time() - start_time) * 1000),
        )

    def _execute_validate(
        self, rule: RuleDefinition, asset: Asset, start_time: float
    ) -> RuleExecution:
        """Execute VALIDATE action"""
        action = rule.action.get("validate", {})
        severity = action.get("severity", "WARNING")
        message_template = action.get("message", "Validation failed")

        # Resolve message template
        message = message_template.replace("{tag}", self._get_asset_tag(asset))
        for key, value in asset.properties.items() if asset.properties else {}:
            message = message.replace(f"{{{key}}}", str(value))

        return self._log_execution(
            rule=rule,
            asset=asset,
            action_type="VALIDATION_FAIL" if severity == "ERROR" else "VALIDATION_WARN",
            action_taken=f"Validation {severity}: {message}",
            condition_matched=True,
            error_message=message,
            execution_time_ms=int((time.time() - start_time) * 1000),
        )

    def _log_execution(
        self,
        rule: RuleDefinition,
        asset: Asset,
        action_type: str,
        action_taken: str,
        condition_matched: bool,
        created_entity_id: str | None = None,
        created_entity_type: str | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        execution_time_ms: int = 0,
    ) -> RuleExecution:
        """Create audit log entry"""
        execution = RuleExecution(
            rule_id=rule.id,
            project_id=self.project_id,
            asset_id=asset.id,
            action_type=action_type,
            action_taken=action_taken,
            condition_matched=condition_matched,
            created_entity_id=created_entity_id,
            created_entity_type=created_entity_type,
            error_message=error_message,
            stack_trace=stack_trace,
            execution_time_ms=execution_time_ms,
        )

        self.db.add(execution)

        # Update rule stats
        rule.execution_count += 1
        rule.last_executed_at = datetime.utcnow()
        if action_type in ["CREATE", "UPDATE", "LINK"]:
            rule.success_count += 1
        elif action_type == "ERROR":
            rule.failure_count += 1

        self.db.commit()

        return execution
