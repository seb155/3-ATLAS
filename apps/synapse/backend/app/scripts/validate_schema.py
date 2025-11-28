"""
Database Schema Validation Script
==================================
Validates SQLAlchemy models against project standards.

Run: python -m app.scripts.validate_schema

Checks:
- Naming conventions (snake_case)
- Required fields (id, created_at, etc.)
- Data types consistency
- Duplicate table detection
"""

import sys
from difflib import SequenceMatcher

from app.core.database import Base


def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()


def validate_schema():
    """Validate all SQLAlchemy models against standards"""
    issues = []
    warnings = []

    print("=" * 60)
    print("Database Schema Validation")
    print("=" * 60)

    # Get all tables from metadata
    tables = Base.metadata.tables

    print(f"\nFound {len(tables)} tables\n")

    # 1. Check naming conventions
    print("[1/4] Checking naming conventions...")
    for table_name, table in tables.items():
        # Table names should be lowercase snake_case
        if not table_name.islower():
            issues.append(f"❌ Table '{table_name}' should be lowercase")

        if "-" in table_name:
            issues.append(f"❌ Table '{table_name}' should use underscores, not hyphens")

        # Column names should be snake_case
        for col in table.columns:
            if col.name != col.name.lower():
                warnings.append(f"⚠️  Column '{table_name}.{col.name}' should be lowercase")

            if any(char.isupper() for char in col.name):
                warnings.append(
                    f"⚠️  Column '{table_name}.{col.name}' uses camelCase (should be snake_case)"
                )

    # 2. Check required fields
    print(" [2/4] Checking required fields...")
    for table_name, table in tables.items():
        col_names = [col.name for col in table.columns]

        # All tables should have 'id'
        if "id" not in col_names:
            issues.append(f"❌ Table '{table_name}' missing 'id' column")

        # All tables should have created_at (except junction tables)
        if not table_name.endswith("_associations") and "created_at" not in col_names:
            warnings.append(f"⚠️  Table '{table_name}' missing 'created_at' column")

        # Check primary key exists
        if not table.primary_key:
            issues.append(f"❌ Table '{table_name}' has no primary key")

    # 3. Detect duplicate/similar tables
    print("[3/4] Detecting duplicate tables...")
    table_list = list(tables.keys())
    duplicates = []

    for i, t1 in enumerate(table_list):
        for t2 in table_list[i + 1 :]:
            # Compare column names
            cols1 = {col.name for col in tables[t1].columns}
            cols2 = {col.name for col in tables[t2].columns}

            # Calculate overlap
            if cols1 and cols2:
                overlap = len(cols1 & cols2) / len(cols1 | cols2)

                if overlap > 0.6:  # More than 60% similar
                    duplicates.append((t1, t2, overlap))
                    warnings.append(
                        f"⚠️  '{t1}' and '{t2}' are {overlap:.0%} similar - potential duplication"
                    )

    # 4. Check data type consistency
    print("[4/4] Checking data type consistency...")
    # Group columns by name across tables
    column_types = {}
    for table_name, table in tables.items():
        for col in table.columns:
            if col.name not in column_types:
                column_types[col.name] = []
            column_types[col.name].append((table_name, str(col.type)))

    # Check if same column name has different types
    for col_name, usages in column_types.items():
        types = {usage[1] for usage in usages}
        if len(types) > 1:
            warnings.append(f"⚠️  Column '{col_name}' has inconsistent types: {types}")

    # Print results
    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)

    if not issues and not warnings:
        print("✅ All checks passed! Schema is valid.")
        return 0

    if issues:
        print(f"\n❌ {len(issues)} issues found:\n")
        for issue in issues:
            print(f"  {issue}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:\n")
        for warning in warnings:
            print(f"  {warning}")

    print("\n" + "=" * 60)

    if issues:
        print("❌ Validation FAILED - fix issues above")
        return 1
    else:
        print("⚠️  Validation PASSED with warnings")
        return 0


if __name__ == "__main__":
    exit_code = validate_schema()
    sys.exit(exit_code)
