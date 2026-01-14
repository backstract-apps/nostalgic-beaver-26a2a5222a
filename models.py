from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import class_mapper
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, Text, ForeignKey, JSON, Numeric, Date, \
    TIMESTAMP, UUID, LargeBinary, text, Interval
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base


@as_declarative()
class Base:
    id: int
    __name__: str

    # Auto-generate table name if not provided
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Generic to_dict() method
    def to_dict(self):
        """
        Converts the SQLAlchemy model instance to a dictionary, ensuring UUID fields are converted to strings.
        """
        result = {}
        for column in class_mapper(self.__class__).columns:
            value = getattr(self, column.key)
                # Handle UUID fields
            if isinstance(value, uuid.UUID):
                value = str(value)
            # Handle datetime fields
            elif isinstance(value, datetime):
                value = value.isoformat()  # Convert to ISO 8601 string
            # Handle Decimal fields
            elif isinstance(value, Decimal):
                value = float(value)

            result[column.key] = value
        return result




class MaysonRequestLogger(Base):
    __tablename__ = 'mayson_request_logger'
    id = Column(Integer, primary_key=True, autoincrement=True )
    ts_utc = Column(Time, primary_key=False )
    method = Column(String, primary_key=False )
    path = Column(String, primary_key=False )
    status_code = Column(Integer, primary_key=False )
    duration_ms = Column(Float, primary_key=False )
    client_ip = Column(String, primary_key=False )
    user_agent = Column(String, primary_key=False )
    content_length = Column(Integer, primary_key=False )
    style = Column(String, primary_key=False )
    message = Column(String, primary_key=False )


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True )
    name = Column(String, primary_key=False )
    email = Column(String, primary_key=False )


class ItemsSold(Base):
    __tablename__ = 'items_sold'
    item_id = Column(Integer, primary_key=True, autoincrement=True )
    quantity = Column(Integer, primary_key=False )
    price_per_item = Column(Integer, primary_key=False )
    price = Column(Float, primary_key=False )


