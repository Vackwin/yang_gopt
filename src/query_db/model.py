from typing import List, Optional, Union
from pydantic import BaseModel, Field

class DateRange(BaseModel):
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)

class Range(BaseModel):
    gte: int
    lte: int

class Sort(BaseModel):
    field: str = Field(...)
    order: int = Field(...)

class Aggregation(BaseModel):
    op: Optional[str]
    field: str

class DistinctAggregation(BaseModel):
    field_names: List[str] = Field(..., alias="fields")

class Where(BaseModel):
    id: Optional[List[int]] = Field(default=None)
    user_id: Optional[List[int]] = Field(default=None)
    source_id: Optional[List[int]] = Field(default=None)
    created_at: Optional[DateRange] = Field(default=None)
    # deleted_at: Optional[DateRange] = Field(default=None)
    source: List[str] = Field(...)
    sentence: Optional[str] = Field(default=None)
    gop: Optional[Range] = Field(default=None)

class Query(BaseModel):
    db_name: str = Field(...)
    select: Union[List[Aggregation], DistinctAggregation, List[str], str] = Field(...)
    collection_name: str = Field(...)
    where: Where = Field(...)
    skip: int = Field(0)
    limit: int = Field(0)
    sort: Optional[Sort] = Field(default=None)
