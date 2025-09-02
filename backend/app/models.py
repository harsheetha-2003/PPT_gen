from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from app.db import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True)        # which service used (classification, export, etc.)
    input_data = Column(String)                 # could be filename or text snippet
    output_file = Column(String, nullable=True) # path to generated file (PDF/PPT/etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    def set_expiry(self, minutes: int = 10):
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
