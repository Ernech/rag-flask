from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
@dataclass
class IndexedDocumentModel:
    document_id: Optional[int] = None
    file_name: Optional[str] = None
    file_hash: Optional[str] = None
    file_path: Optional[str] = None
    file_source: Optional[str] = None
    indexed_at: Optional[datetime] = None
    indexed_by: Optional[str] = None
    status: Optional[str] = None
    embedding_model: Optional[str] = None
    chunk_count: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: tuple):
        return cls(*row)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        return asdict(self)
