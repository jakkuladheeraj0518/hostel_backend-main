from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base

class SearchQuery(Base):
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_text = Column(String(500))
    city = Column(String(100), index=True)
    filters = Column(Text)  # JSON string of applied filters
    results_count = Column(Integer)
    searched_at = Column(DateTime, default=datetime.utcnow, index=True)