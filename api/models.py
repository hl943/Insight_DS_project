from sqlalchemy import Column, Integer, Numeric, String
from database import Base


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    # query_date = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    air_temp = Column(Numeric(2, 2))
    rel_hum = Column(Numeric(2, 2))
    wind_speed = Column(Numeric(2, 2))
    soil_moisture = Column(Numeric(2, 2))
    incident_energy = Column(Numeric(2, 2))
    ETo = Column(Numeric(2, 2))
    day_of_the_year = Column(Numeric(2, 2))
    sunshine_duration = Column(Numeric(2, 2))
    #email = Column(String, unique=True, index=True)
    #hashed_password = Column(String)
    #is_active = Column(Boolean, default=True)


