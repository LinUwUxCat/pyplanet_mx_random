from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.apps.contrib.mx.api import MXApi
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
import requests, json
import os
import aiohttp
from datetime import datetime
from .models import UserPoints
from .views.buttons import MXRButtons
import logging

class MxRandomApp(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	mode_dependencies = ['TimeAttack']
	app_dependencies = ['core.maniaplanet']
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.api = None
		self.isFinished = False
		self.pointsToGive = 1.0
		self.players_points = dict()
		self.currentMapStartTime = 0
		self.view = MXRButtons(self)

	async def on_init(self):
		await super().on_init()
		self.api = MXApi()
		self.api.site = "tm"
		await self.view.display()

	async def on_start(self):
		await super().on_start()
		self.context.signals.listen(tm_signals.finish, self.on_finish)
		self.context.signals.listen(mp_signals.map.map_end, self.on_end)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)
		await self.instance.command_manager.register(Command(command='brokenskip', target=self.brokenskip, admin=True, description='Skip map because it\'s broken'))	
		await self.instance.command_manager.register(Command(command='mxrhelp', target=self.randhelp, admin=False, description='Get some information about the MX Random plugin'))	
		await self.instance.command_manager.register(Command(command='mxrrank', target=self.randrank, admin=False, description='Get current MX Random ranking'))	


	async def on_stop(self):
		await super().on_stop()

	async def on_destroy(self):
		await super().on_destroy()

	async def get_next_map(self):
		mxmap = json.loads(requests.get(f"https://tm.mania.exchange/mapsearch2/search?api=on&random=1&tpack=TMCanyon&tpack=TMValley&tpack=TMStadium&tpack=TMLagoon&tpack=TMAll").text)["results"][0]
		mapid = mxmap["TrackID"]
		mapname = mxmap["GbxMapName"]
		mapuid = mxmap["TrackUID"]
		try:
			if not await self.instance.storage.driver.exists(os.path.join('UserData', 'Maps', 'PyPlanet-MX')):
				await self.instance.storage.driver.mkdir(os.path.join('UserData', 'Maps', 'PyPlanet-MX'))
		except Exception as e:
			message = '$f00Error: Can\'t check or create folder: {}'.format(str(e))
			await self.instance.chat(message)
			return
		logging.getLogger(__name__).info("about to make a session")
		session = aiohttp.ClientSession(
			headers={
				'User-Agent': 'MX Random plugin for pyplanet by linuxcat',
				'X-ManiaPlanet-ServerLogin': 'linuxcatserver'
			}
		)

		resp = await session.get(f"https://tm.mania-exchange.com/maps/download/{mapid}")
		
		map_filename = os.path.join('PyPlanet-MX', '{}-{}.Map.Gbx'.format(
					self.instance.game.game.upper(), mapid
		))
		async with self.instance.storage.open_map(map_filename, 'wb+') as map_file:
			await map_file.write(await resp.read())
			await map_file.close()
		session.close()
		result = await self.instance.map_manager.add_map(map_filename, save_matchsettings=True)
		if result:
			try:
				await self.instance.map_manager.remove_map(self.instance.map_manager.current_map, True)
				logging.getLogger(__name__).info("Removed the current map!")
			except:
				pass #do nothing if it doesn't work
			try:
				await self.instance.map_manager.update_list(full_update=True)
				logging.getLogger(__name__).info(f"Updated the list!")
			except:
				pass
			logging.getLogger(__name__).info(f"Added {mapname} to be played...")
			#await self.instance.map_manager.load_matchsettings("MatchSettings/maplist.txt")
			#logging.getLogger(__name__).info(mapuid)
			await self.instance.map_manager.set_next_map(mapuid)
		else :
			await self.instance.chat(f"There was an error adding a new map - current map not removed from pool!")
		
		#https://tm.mania.exchange/mapsearch2/search?api=on&random=1&tpack=TMCanyon&tpack=TMValley&tpack=TMStadium&tpack=TMLagoon&tpack=TMAll
		#get results[0]["TrackID"]
		#use it in tm.mania-exchange.com/maps/download/TRACKID

	async def brokenskip(self, player, **kwargs):
		if 'admin' in self.instance.apps.apps:
			await self.instance.apps.apps['admin'].map.next_map(player, None)

	async def on_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		if not self.isFinished:
			if race_time < self.instance.map_manager.current_map.time_author:
				self.isFinished = True
				self.players_points[player.login] = self.pointsToGive
				mode_settings = await self.instance.mode_manager.get_settings()
				mode_settings["S_TimeLimit"] = int((datetime.now() - self.currentMapStartTime).total_seconds()) + 20
				await self.instance.mode_manager.update_settings(mode_settings)
		else :
			if race_time < self.instance.map_manager.current_map.time_author:
				if not player.login in self.players_points:
					self.pointsToGive /= 2
					self.players_points[player.login] = self.pointsToGive

	async def on_end(self, **kwargs):
		for key in self.players_points:
			try:
				instance = await UserPoints.get(login=key)
			except:
				instance = UserPoints(login=key, points=0.0)
			instance.points += self.players_points[key]
			await instance.save()
		

	async def map_start(self, **kwargs):
		self.currentMapStartTime = datetime.now()
		self.isFinished = False
		self.players_points = dict()
		self.pointsToGive = 1.0
		mode_settings = await self.instance.mode_manager.get_settings()
		mode_settings["S_TimeLimit"] = -1
		await self.instance.mode_manager.update_settings(mode_settings)
		await self.get_next_map()

	async def randhelp(self, player, **kwargs):
		await self.instance.chat("$bMX Random plugin help$z\nWhen someone in the server gets an author medal on the current map, the remaining drivers have 20 seconds to get one as well\nOnce the time is over, the first finisher with Author Time gets 1 point, the second 0.5, the third 0.25, etc.\nAfterwards, the map gets chosen randomly from mania-exchange.", player)
	
	async def randrank(self, player, **kwargs):
		await self.instance.chat("TODO : Implement this")
		e = await UserPoints.execute(UserPoints.select().order_by(UserPoints.points.desc()))
		for i in e:
			logging.getLogger(__name__).info(i)

	#async def get_all_points(self, **kwargs):
		