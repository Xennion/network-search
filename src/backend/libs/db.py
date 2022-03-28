import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

from .config import config

_DATABASE_URL = config["db_connection"]

engine = sqlalchemy.create_engine(_DATABASE_URL)
SessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()


class NetworkDatabaseModel(Base):
    __tablename__ = "networks"

    id = Column(String, primary_key=True, unique=True)
    network = Column(String, index=True)
    datacenter = Column(String, nullable=False)
    description = Column(String)
    netmask = Column(String)
    bitmask = Column(Integer)
    gateway = Column(String)
    network_address = Column(String)
    broadcast_address = Column(String)
    first_usable_ip = Column(String)
    last_usable_ip = Column(String)
    vlan = Column(Integer, nullable=False)
    origin_device = Column(String)
