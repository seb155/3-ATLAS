import hashlib
import os

import pandas as pd
from sqlalchemy.orm import Session
from thefuzz import fuzz, process

from app.models.ingestion import DataSource, DetectedType, IngestStatus, StagedRow


class IngestionService:
    CONCEPTS = {
        "TAG": ["Tag", "Component ID", "Equip Tag", "Item Tag", "Asset ID", "Tag Number"],
        "PID": ["P&ID", "PID#", "P&ID Drawing", "PID Tag", "Drawing No", "P&ID No"],
        "DESC": ["Description", "Desc", "Service", "Item Name", "Function"],
        "TYPE": ["Equipment", "Device Type", "Class", "Asset Type"],
        "FROM": ["From", "Source", "Origin"],
        "TO": ["To", "Destination", "Target"],
        "CABLE": ["Cable Tag", "Cable No", "Cable ID"],
    }

    FINGERPRINTS = {
        DetectedType.BBA_INSTRUMENT_LIST: ["TAG", "PID", "TYPE"],
        DetectedType.CABLE_SCHEDULE: ["CABLE", "FROM", "TO"],
        DetectedType.GENERIC_LIST: ["TAG", "DESC"],
    }

    @staticmethod
    def scan_folder(path: str = "/app/Data_raw") -> list[str]:
        if not os.path.exists(path):
            return []
        return [f for f in os.listdir(path) if f.endswith((".xlsx", ".xls", ".csv"))]

    @staticmethod
    def ingest_file(db: Session, project_id: str, file_path: str) -> DataSource:
        filename = os.path.basename(file_path)

        # 1. Calculate Hash
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Check duplicate
        existing = db.query(DataSource).filter(DataSource.file_hash == file_hash).first()
        if existing:
            return existing

        # 2. Read File
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

        # 3. Detect Type
        headers = list(df.columns)
        detected_type, confidence = IngestionService._detect_type(headers)

        # 4. Create DataSource
        data_source = DataSource(
            project_id=project_id,
            filename=filename,
            file_hash=file_hash,
            ingest_status=IngestStatus.STAGED,
            detected_type=detected_type,
            metadata_json={"row_count": len(df), "headers": headers, "confidence": confidence},
        )
        db.add(data_source)
        db.commit()
        db.refresh(data_source)

        # 5. Create StagedRows (Bulk Insert)
        staged_rows = []
        for index, row in df.iterrows():
            # Convert row to dict and handle NaN
            row_data = row.where(pd.notnull(row), None).to_dict()
            staged_rows.append(
                StagedRow(data_source_id=data_source.id, row_index=index, raw_data=row_data)
            )

        db.bulk_save_objects(staged_rows)
        db.commit()

        return data_source

    @staticmethod
    def _detect_type(headers: list[str]) -> tuple[DetectedType, float]:
        # 1. Map Headers to Concepts
        found_concepts = set()
        for header in headers:
            # Fuzzy match header against all concepts
            best_concept = None
            best_score = 0

            for concept, aliases in IngestionService.CONCEPTS.items():
                # Extract best match for this concept
                match, score = process.extractOne(header, aliases, scorer=fuzz.token_sort_ratio)
                if score > 80 and score > best_score:
                    best_score = score
                    best_concept = concept

            if best_concept:
                found_concepts.add(best_concept)

        # 2. Check Fingerprints
        best_type = DetectedType.UNKNOWN
        max_matches = 0

        for type_enum, required_concepts in IngestionService.FINGERPRINTS.items():
            matches = sum(1 for c in required_concepts if c in found_concepts)
            if matches == len(required_concepts):
                # Perfect match of requirements
                return type_enum, 1.0

            if matches > max_matches:
                max_matches = matches
                best_type = type_enum

        # Partial match logic could go here
        return best_type, 0.5 if max_matches > 0 else 0.0
