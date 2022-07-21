# -*- coding: utf-8 -*-
from random import randint

from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
from mod.client.clientEvent import ClientEvent
from mod.server.serverEvent import ServerEvent
import Preset.Controller.PresetApi as presetApi

# server
ServerUpdateUIEvent = "UpdateUIEvent"
ServerStartLogicEvent = "StartLogicEvent"

# client
ClientOnLoadSuccess = "OnLoadSuccess"
ClientEnsureJoinGameEvent = "EnsureJoinGameEvent"
ClientUiInitFinished = "UiInitFinished"

# config
ModName = "StartLogicMod"
StartLogicUIName = "startLogicUI"
StartLogicUIScreenDef = "startLogicUI.main"


# 外部广播事件->开始游戏时广播 ServerStartLogicEvent 事件至预设系统
@registerGenericClass("StartLogicPart")
class StartLogicPart(PartBase):
	isUnique = True
	LastVersion = [0, 0, 4]

	def __init__(self):
		super(StartLogicPart, self).__init__()
		self.name = "开始游戏"
		# 玩家等待坐标
		self.startGameWaitPos = [50, 64, 50]
		self.area = {'min': (1.0, 0.0, 1.0), 'max': (5.0, 2.0, 5.0)}
		# 最低开局玩家人数
		self.gameMinPlayerNum = 1
		# 是否自动开始游戏标志
		self.autoStartFlag = False
		self.countDownTime = 5
		self.downTimeSecond = self.countDownTime
		# 是否清除掉落物标志
		self.clearDropsFlag = True
		self.posOption = 0
		self.teamPosList = [{'teamName': '', 'pos': (50.0, 64.0, 5.0)}, {'teamName': '', 'pos': (50.0, 64.0, 10.0)}]
		self.randomPointList = [{'pos': (50.0, 65.0, 5.0)}, {'pos': (50.0, 65.0, 10.0)}, {'pos': (55.0, 68.0, 5.0)}]
		self.startNum = 1
		# 0 等待, 1 确认, 2 倒计时, 3 游戏中
		self.state = 0
		self.players = {}
		self.playerAliveDict = {}
		self.playerEnsureDict = {}
		self.startGameCoroutineIter = None
		# 客户端UI
		self.startLogicUINode = None

	def InitServer(self):
		self.ListenForEngineEvent(ServerEvent.AddServerPlayerEvent, self, self.OnPlayerAdd)
		self.ListenForEngineEvent(ServerEvent.DelServerPlayerEvent, self, self.OnDelServerPlayer)
		self.ListenForEngineEvent(ServerEvent.PlayerDieEvent, self, self.OnPlayerDie)
		self.ListenForEngineEvent(ServerEvent.PlayerRespawnEvent, self, self.OnPlayerRespawn)
		self.ListenForEngineEvent(ServerEvent.DamageEvent, self, self.OnDamage)
		self.ListenSelfEvent(ClientEnsureJoinGameEvent, self, self.OnPlayerEnsureJoinGame)
		self.ListenSelfEvent(ClientOnLoadSuccess, self, self.OnLoadSuccess)
		self.ListenSelfEvent(ClientUiInitFinished, self, self.OnServerUiInitFinished)

		self.downTimeSecond = self.countDownTime

		# 处理已经加载的Player
		for player in self.GetManager().loadedPlayers:
			self.players[player] = True
			self.playerAliveDict[player] = True
			self.BroadcastData()

	def DestroyServer(self):
		self.UnListenForEngineEvent(ServerEvent.AddServerPlayerEvent, self, self.OnPlayerAdd)
		self.UnListenForEngineEvent(ServerEvent.DelServerPlayerEvent, self, self.OnDelServerPlayer)
		self.UnListenForEngineEvent(ServerEvent.PlayerDieEvent, self, self.OnPlayerDie)
		self.UnListenForEngineEvent(ServerEvent.PlayerRespawnEvent, self, self.OnPlayerRespawn)
		self.UnListenForEngineEvent(ServerEvent.DamageEvent, self, self.OnDamage)
		self.UnListenSelfEvent(ClientEnsureJoinGameEvent, self, self.OnPlayerEnsureJoinGame)
		self.UnListenSelfEvent(ClientOnLoadSuccess, self, self.OnLoadSuccess)
		self.UnListenSelfEvent(ClientUiInitFinished, self, self.OnServerUiInitFinished)

	# 正在游戏中
	def InGame(self):
		return self.state == 3

	# 结束游戏零件有调用
	def getPlayerEnsure(self):
		return self.playerEnsureDict

	def CheckState(self):
		lastState = -1
		while lastState != self.state:
			lastState = self.state
			if self.state == 0:  # 等待阶段
				if len(self.playerAliveDict) >= self.gameMinPlayerNum:
					self.state = 1
					self.playerEnsureDict = {}
					self.startNum = len(self.players)
			elif self.state == 1:  # 确认阶段
				self.startNum = max(self.startNum, len(self.players))
				if self.autoStartFlag:  # 自动确认
					for k in self.playerAliveDict.keys():
						self.playerEnsureDict[k] = True
				if len(self.playerAliveDict) < self.startNum:  # 人突然不够了
					self.state = 1
				elif len(self.playerEnsureDict) >= self.startNum:  # 确认人数够了
					self.state = 2
					self.downTimeSecond = int(self.countDownTime * 30)
			elif self.state == 2:  # 倒计时阶段
				if self.downTimeSecond <= 0:
					self.state = 3
					TeamServerPart = presetApi.GetGameObjectByTypeName("TeamPart")
					if TeamServerPart:
						TeamServerPart.ReQueueAllocation(list(self.playerEnsureDict.keys()))
						TeamServerPart.ShowTeamUI(True)
					self.StartGame()
				else:
					if len(self.playerAliveDict) < self.startNum or len(self.playerEnsureDict) < self.startNum:  # 人突然不够了
						self.state = 0
			elif self.state == 3:  # 游戏中
				pass

	def StartGame(self):
		self.BroadcastPresetSystemEvent(ServerStartLogicEvent, self.CreateEventData())# 其他系统需要的事件
		# 如果有结束游戏组件将结束组件数据重置
		endLogicServerPart = presetApi.GetGameObjectByTypeName("EndLogicPart")
		if endLogicServerPart is None:
			self.LogInfo("===== Get EndLogicPartSystem Fail=====")
		else:
			endLogicServerPart.ReSetDynamicData()
			endLogicServerPart.StartClock()
		TeamServerPart = presetApi.GetGameObjectByTypeName("TeamPart")
		if TeamServerPart is None:
			self.LogInfo("===== Get TeamPartSystem Fail=====")
		else:
			if endLogicServerPart.IsEndTeamType():
				TeamServerPart.ReQueueAllocation(list(self.playerEnsureDict.keys()))
				TeamServerPart.ShowTeamUI(True)
			else:
				TeamServerPart.ShowTeamUI(False)

		# 设置开始游戏位置
		playerList = []
		if self.autoStartFlag:
			playerList = list(self.playerAliveDict.keys())
		else:
			playerList = list(self.playerEnsureDict.keys())
		if self.posOption == 1:  # 根据队伍设置传送点
			if TeamServerPart is not None:
				for player in playerList:
					teamName = TeamServerPart.GetPlayerTeamName(player)
					teamPosDict = {}
					for i in self.teamPosList:
						teamPosDict[i['teamName']] = i['pos']
					if teamName:
						if teamName in teamPosDict:
							pos = list(teamPosDict[teamName])
							presetPos = [0, 0, 0]  # self.GetWorldPosition()相对父预设坐标
							self.SetEntityPos(player, (pos[0]+presetPos[0], pos[1]+presetPos[1]+2, pos[2]+presetPos[2]))
							self.LogInfo("set team pos: %s, %s", player, str(pos))
						else:
							self.LogInfo("can not find teamname in teamPosList, donn't set team pos:")
		else:  # 随机列表
			if self.randomPointList:
				for player in playerList:
					i = randint(0, len(self.randomPointList) - 1)
					pos = self.randomPointList[i]['pos']
					presetPos = [0, 0, 0]  # self.GetWorldPosition()相对父预设坐标
					self.SetEntityPos(player, (pos[0] + presetPos[0], pos[1] + presetPos[1] + 2, pos[2] + presetPos[2]))
					self.LogInfo("set random pos: %s, %s", player, str(pos))
		# 清除掉落物
		if self.clearDropsFlag:
			commandComp = self.CreateCommandComponent(self.GetLevelId())
			commandComp.command = "/kill @e[type=item]"
			self.GetApi().NeedsUpdate(commandComp)

	def GetGameStartState(self):
		return self.state == 3

	def ReStartGame(self):
		TeamServerPart = presetApi.GetGameObjectByTypeName("TeamPart")
		if TeamServerPart:
			TeamServerPart.ShowTeamUI(False)
		for player in self.players:
			self.SetPlayerInitPos(player)
		self.state = 0
		self.downTimeSecond = self.countDownTime
		self.playerEnsureDict = {}
		print ('ReStartGame')
		self.BroadcastData()

	def BroadcastData(self):
		self.CheckState()
		data = self.CreateEventData()
		data['playerAlive'] = self.playerAliveDict
		data['playerEnsure'] = self.playerEnsureDict
		data['state'] = self.state
		data['countDownTime'] = self.downTimeSecond
		data['startNum'] = self.startNum
		self.BroadcastToAllClient(ServerUpdateUIEvent, data)

	def OnPlayerAdd(self, data):
		playerId = data.get("id", '')
		if playerId:
			self.players[playerId] = True
			self.playerAliveDict[playerId] = True
			self.SetPlayerInitPos(playerId)
		self.BroadcastData()

	def OnDelServerPlayer(self, args):
		playerId = args["id"]
		del self.players[playerId]
		if playerId in self.playerAliveDict:
			del self.playerAliveDict[playerId]
		if playerId in self.playerEnsureDict:
			del self.playerEnsureDict[playerId]
		self.BroadcastData()

	def OnPlayerEnsureJoinGame(self, args):
		if self.state == 0 or self.state == 3:
			return
		playerId = args["playerId"]
		self.playerEnsureDict[playerId] = True
		self.BroadcastData()

	def OnPlayerDie(self, data):
		playerId = data['id']
		if playerId in self.playerAliveDict:
			del self.playerAliveDict[playerId]
		if self.state != 3 and playerId in self.playerEnsureDict:
			del self.playerEnsureDict[playerId]
		self.BroadcastData()

	def OnPlayerRespawn(self, data):
		playerId = data['id']
		# self.playerAliveDict[playerId] = True
		# if playerId not in self.playerEnsureDict:
		# 	self.SetPlayerInitPos(playerId)
		self.playerAliveDict[playerId] = True
		self.BroadcastData()

	def invincible(self, pos, startPoint=None, endPoint=None):
		if pos is None:
			return False
		if startPoint is None:
			startPoint = self.area['min']
		if endPoint is None:
			endPoint = self.area['max']
		for i in range(len(pos)):
			upperBound = max(startPoint[i], endPoint[i]) + 1
			lowerBound = min(startPoint[i], endPoint[i]) - 1
			value = pos[i]
			if i == 1:
				value -= 2
			value = int(value)
			if value < lowerBound or value > upperBound:
				return False
		return True

	def OnDamage(self, data):
		entityId = data['entityId']
		if entityId not in self.playerAliveDict:
			return
		pos = self.GetEntityPos(entityId)
		if self.invincible(pos):
			data['damage'] = 0

	def getRandomPoint(self, startPoint=None, endPoint=None):
		if startPoint is None:
			startPoint = self.area['min']
		if endPoint is None:
			endPoint = self.area['max']
		deltaX = endPoint[0] - startPoint[0]
		deltaY = endPoint[1] - startPoint[1]
		deltaZ = endPoint[2] - startPoint[2]
		dx = randint(min(0, abs(deltaX)), max(0, abs(deltaX)))
		dy = randint(min(0, abs(deltaY)), max(0, abs(deltaY)))
		dz = randint(min(0, abs(deltaZ)), max(0, abs(deltaZ)))
		point = [
			min(startPoint[0], endPoint[0]) + dx,
			min(startPoint[1], endPoint[1]) + dy,
			min(startPoint[2], endPoint[2]) + dz
		]
		return tuple(point)

	def isInside(self, pos, startPoint=None, endPoint=None):
		if pos is None:
			return False
		if startPoint is None:
			startPoint = self.area['min']
		if endPoint is None:
			endPoint = self.area['max']
		for i in range(len(pos)):
			upperBound = max(startPoint[i], endPoint[i])
			lowerBound = min(startPoint[i], endPoint[i])
			value = pos[i]
			if i == 1:
				value -= 2
			value = int(value)
			if value < lowerBound or value > upperBound:
				return False
		return True

	def SetPlayerInitPos(self, playerId):
		relativePos = self.GetEntityPos(playerId)
		if self.isInside(relativePos):
			return
		relativePos = self.getRandomPoint()
		presetPos = self.GetWorldPosition()
		self.SetEntityPos(playerId, (relativePos[0] + presetPos[0], relativePos[1] + presetPos[1] + 2, relativePos[2] + presetPos[2]))

	def OnLoadSuccess(self, args):
		playerId = args["id"]
		self.SetPlayerInitPos(playerId)
		TeamServerPart = presetApi.GetGameObjectByTypeName("TeamPart")
		if TeamServerPart:
			TeamServerPart.ShowTeamUI(False)
		self.BroadcastData()

	def OnServerUiInitFinished(self, args):
		TeamServerPart = presetApi.GetGameObjectByTypeName("TeamPart")
		if TeamServerPart:
			TeamServerPart.ShowTeamUI(False)
		self.BroadcastData()

	def OnLocalPlayerStopLoading(self, args):
		args['id'] = args['playerId']
		self.NotifyToServer(ClientOnLoadSuccess, args)

	def InitClient(self):
		self.ListenForEngineEvent(ClientEvent.UiInitFinished, self, self.OnClientUIInitFinished)
		self.ListenSelfEvent(ServerUpdateUIEvent, self, self.OnUpdateUI)
		self.ListenForEngineEvent("OnLocalPlayerStopLoading", self, self.OnLocalPlayerStopLoading)

	def DestroyClient(self):
		self.UnListenForEngineEvent(ClientEvent.UiInitFinished, self, self.OnClientUIInitFinished)
		self.UnListenSelfEvent(ServerUpdateUIEvent, self, self.OnUpdateUI)
		self.UnListenForEngineEvent("OnLocalPlayerStopLoading", self, self.OnLocalPlayerStopLoading)

	def OnUpdateUI(self, args):
		if not self.isClient or self.startLogicUINode is None:
			return
		self.startLogicUINode.UpdateUI(args)

	def OnClientUIInitFinished(self, args):
		from startLogicUI import StartLogicUIScreen
		cls = '{}.{}'.format(StartLogicUIScreen.__module__, StartLogicUIScreen.__name__)
		uiApi = self.GetApi()
		uiApi.RegisterUI(ModName, StartLogicUIName, cls, StartLogicUIScreenDef)
		uiApi.CreateUI(ModName, StartLogicUIName, {"isHud": 1})
		self.startLogicUINode = uiApi.GetUI(ModName, StartLogicUIName)
		if self.startLogicUINode:
			self.startLogicUINode.Init()
		else:
			self.LogError("create ui %s failed!" % StartLogicUIScreenDef)
		self.NotifyToServer(ClientUiInitFinished, args)

	def ClickStart(self):
		data = self.CreateEventData()
		data["playerId"] = self.GetApi().GetLocalPlayerId()
		self.NotifyToServer(ClientEnsureJoinGameEvent, data)

	def TickServer(self):
		if self.state == 2:
			if self.downTimeSecond >= 0 and self.downTimeSecond % 30 == 0:
				self.BroadcastData()
			self.downTimeSecond -= 1

	def TickClient(self):
		pass
