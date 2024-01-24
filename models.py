import os
import subprocess
from datetime import datetime

import pytz
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import TIMEZONE, DUMPS_FOLDER, DB_URL, DB_USER, DB_HOST, DB_PORT, DB_NAME, DB_PASSWORD
from logger import info_logger, error_logger

Base = declarative_base()


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    price_usd = Column(Float)
    odometer = Column(Integer)
    username = Column(String)
    phone_number = Column(String)
    image_url = Column(String)
    images_count = Column(Integer)
    car_number = Column(String)
    car_vin = Column(String)
    datetime_found = Column(DateTime, default=datetime.now(pytz.timezone(TIMEZONE)))

    engine = create_engine(DB_URL)

    @classmethod
    def create_table(cls):
        Base.metadata.create_all(cls.engine, checkfirst=True)

    @classmethod
    def connect_db(cls):
        Session = sessionmaker(bind=cls.engine)
        return Session()

    @classmethod
    def insert_data(cls, session, data):
        car = cls(**data)
        session.add(car)
        session.commit()

    @classmethod
    def dump_database(cls):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(DUMPS_FOLDER, exist_ok=True)
        dump_file = os.path.join(DUMPS_FOLDER, f"dump_{timestamp}.sql")
        try:
            os.environ["PGPASSWORD"] = DB_PASSWORD
            pg_dump_command = [
                'pg_dump',
                '-U', DB_USER,
                '-h', DB_HOST,
                '-p', DB_PORT,
                '-d', DB_NAME,
                '-f', dump_file
            ]
            subprocess.run(pg_dump_command, check=True, env=os.environ)
            info_logger.info(f"Database dumped to {dump_file}")
            del os.environ["PGPASSWORD"]
        except subprocess.CalledProcessError as e:
            error_logger.info(f"Error dumping database: {e}")

    @classmethod
    def check_car_exists(cls, session: Session, url: str) -> bool:
        try:
            return session.query(cls).filter_by(url=url).first() is not None
        finally:
            session.close()
