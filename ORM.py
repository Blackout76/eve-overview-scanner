from sqlalchemy import create_engine, func, Column, DateTime, String, Boolean, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
import pandas as pd
from ESI import getPilotIDFromName, getPilot, getCorporation, getAlliance

DATABASE_URL = 'sqlite:///database/database.sqlite'
ESI_SEARCH_CHARATER = 'https://esi.evetech.net/dev/search/?categories=character&datasource=tranquility&language=en-us&search={}&strict=true'
Base = declarative_base()

class Region(Base):
	__tablename__ = 'region'
	index = Column(Integer, primary_key=True)
	region_id = Column(Integer)
	region_name = Column(String)

class Constellation(Base):
	__tablename__ = 'constellation'
	index = Column(Integer, primary_key=True)
	constellation_id = Column(Integer)
	constellation_name = Column(String)
	region_id = Column(Integer, ForeignKey('region.region_id'))

class Solarsystem(Base):
	__tablename__ = 'solarsystem'
	index = Column(Integer, primary_key=True)
	solarsystem_id = Column(Integer)
	solarsystem_name = Column(String)
	constellation_id = Column(Integer, ForeignKey('constellation.constellation_id'))
	region_id = Column(Integer, ForeignKey('region.region_id'))

class Ship(Base):
	__tablename__ = 'ship'
	index = Column(Integer, primary_key=True)
	type_id = Column(Integer)
	type_name = Column(String)
"""
class Alliance(Base):
	__tablename__ = 'alliance'
	id = Column(Integer, primary_key=True)
	eve_id = Column(Integer)
	name = Column(String)
	member_count = Column(Integer)
	war_eligible = Column(Boolean)
	last_update = Column(DateTime, default=func.now())

class Corporation(Base):
	__tablename__ = 'corporation'
	id = Column(Integer, primary_key=True)
	eve_id = Column(Integer)
	name = Column(String)
	member_count = Column(Integer)
	war_eligible = Column(Boolean)
	last_update = Column(DateTime, default=func.now())
	alliance_id = Column(Integer, ForeignKey('alliance.eve_id'))
"""
class Pilot(Base):
	__tablename__ = 'pilot'
	id = Column(Integer, primary_key=True)
	eve_id = Column(Integer)
	name = Column(String)
	corporation_id = Column(Integer)
	corporation_name = Column(String)
	alliance_id = Column(Integer)
	alliance_name = Column(String)
	war_eligible = Column(Boolean)

class Jump(Base):
	__tablename__ = 'jump'
	id = Column(Integer, primary_key=True)
	pilot_id = Column(Integer, ForeignKey('pilot.id'))
	ship_id = Column(Integer, ForeignKey('ship.type_id'))
	system_from_id = Column(Integer, ForeignKey('solarsystem.solarsystem_id'))
	system_to_id = Column(Integer, ForeignKey('solarsystem.solarsystem_id'))
	jump_on = Column(DateTime, default=func.now())

engine = create_engine(DATABASE_URL,connect_args={'check_same_thread':False})
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

def loadShips(ships):
	print ("Loading ressources: ships ...")
	chunks = pd.read_csv(ships, chunksize=100000)
	for c in chunks:
		c.to_sql(name='ship', if_exists='replace', con=engine)

def loadRegions(regions):
	print ("Loading ressources: regions ...")
	chunks = pd.read_csv(regions, chunksize=100000)
	for c in chunks:
		c.to_sql(name='region', if_exists='replace', con=engine)

def loadConstellations(constellations):
	print ("Loading ressources: constellations ...")
	chunks = pd.read_csv(constellations, chunksize=100000)
	for c in chunks:
		c.to_sql(name='constellation', if_exists='replace', con=engine)

def loadSolarSystems(solarsystems):
	print ("Loading ressources: solarsystems ...")
	chunks = pd.read_csv(solarsystems, chunksize=100000)
	for c in chunks:
		c.to_sql(name='solarsystem', if_exists='replace', con=engine)

def getSolarSystemsName():
	s = session()
	return s.query(Solarsystem.solarsystem_name).all()

def valideSystems(system_in, system_out):
	s = session()
	system_in_r = s.query(Solarsystem).filter(func.lower(Solarsystem.solarsystem_name)==func.lower(system_in))
	system_out_r = s.query(Solarsystem).filter(func.lower(Solarsystem.solarsystem_name)==func.lower(system_out))
	if system_in_r.count() > 0 and system_out_r.count() > 0:
		return True
	else:
		return False

def saveJump(shipname, pilotname, system_in, system_out):
	s = session()
	error = None
	jump = None
	pilot = None

	# Get systems
	system_in_id = s.query(Solarsystem).filter(func.lower(Solarsystem.solarsystem_name)==func.lower(system_in)).one().solarsystem_id
	system_out_id = s.query(Solarsystem).filter(func.lower(Solarsystem.solarsystem_name)==func.lower(system_out)).one().solarsystem_id

	# Get the ship
	ship = s.query(Ship).filter(func.lower(Ship.type_name)==func.lower(shipname))

	# Get the jump
	if ship.count() > 0:
		# Get the pilot
		pilot = s.query(Pilot).filter(Pilot.name==pilotname)
		if pilot.count() == 0:
			pilot = Pilot(name=pilotname, war_eligible=False)
			#ESI
			pilot_id = getPilotIDFromName(pilotname)
			if not pilot_id:
				# FIX "g" to "y" error from tesseract
				pilot_id = getPilotIDFromName(pilotname.replace("g","y"))
			if not pilot_id:
				# FIX "ii" to "ji" error from tesseract
				pilot_id = getPilotIDFromName(pilotname.replace("ii","ji"))

			if pilot_id:
				esi_pilot = getPilot(pilot_id)
				if not esi_pilot:
					return error, jump, pilot
				esi_corporation = getCorporation(esi_pilot['corporation_id'])
				if not esi_corporation:
					return error, jump, pilot

				pilot.eve_id = pilot_id
				pilot.corporation_id = esi_pilot['corporation_id']
				pilot.corporation_name = esi_corporation['name']

				if "alliance_id" in esi_pilot.keys():
					esi_alliance = getAlliance(esi_pilot['alliance_id'])
					if esi_alliance:
						pilot.alliance_id = esi_pilot['alliance_id']
						pilot.alliance_name = esi_alliance['name']
						if "war_eligible" in esi_alliance.keys():
							pilot.war_eligible = esi_alliance['war_eligible']

				if "war_eligible" in esi_corporation.keys() and not pilot.war_eligible:
					pilot.war_eligible = esi_corporation['war_eligible']

				s.add(pilot)
				s.commit()

				# Save jump
				jump = Jump(pilot_id=pilot.id, ship_id=ship.one().type_id, system_from_id=system_in_id, system_to_id=system_out_id)
				s.add(jump)
				s.commit()
			else:
				error = "No pilot found for name: " + pilotname
		else:
			pilot = pilot.one()


	return error, jump, pilot

