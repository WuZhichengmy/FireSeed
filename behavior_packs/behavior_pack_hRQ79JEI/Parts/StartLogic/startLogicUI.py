# -*- coding: utf-8 -*-

from mod.client.ui.screenNode import ScreenNode
from mod.client.ui.screenController import ViewBinder, ViewRequest
import mod.client.extraClientApi as clientApi
import Preset.Controller.PresetApi as presetApi


class StartLogicUIScreen(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.mPlayerId = clientApi.GetLocalPlayerId()
		self.autoStartFlag = self.GetParentPart().autoStartFlag

	def Create(self):
		self.waitNotifyPanal = "/waitNotifyPanal"
		self.waitNotifyLabel = self.waitNotifyPanal + "/waitNotifyLabel"
		self.startGameBtn = "/startGameBtn"
		self.countDownLabel = "/countDownLabel"

	def Init(self):
		self.SetVisible(self.countDownLabel, False)
		if self.autoStartFlag:
			self.SetVisible(self.startGameBtn, False)
		buttonUIControl = self.GetBaseUIControl(self.startGameBtn).asButton()
		if buttonUIControl is not None:
			buttonUIControl.AddTouchEventParams({"isSwallow": True})
			buttonUIControl.SetButtonTouchUpCallback(self.OnStartGameBtnClick)

	def GetParentPart(self):
		return presetApi.GetGameObjectByTypeName("StartLogicPart")

	def UpdateWaitUI(self, playerAlive):
		num = len(playerAlive)
		startlogicpart = self.GetParentPart()
		text = "需§a{0}§f名玩家开始游戏（当前§c{1}§f名）".format(startlogicpart.gameMinPlayerNum, num)
		if num >= startlogicpart.gameMinPlayerNum:
			text = "需§a{0}§f名玩家开始游戏（当前§a{1}§f名）".format(startlogicpart.gameMinPlayerNum, num)
		self.SetText(self.waitNotifyLabel, text)
		self.SetVisible(self.waitNotifyPanal, True)
		if not self.autoStartFlag:
			self.SetVisible(self.startGameBtn, True)
			buttonDefaultPath = self.startGameBtn + "/default"
			buttonHoverPath = self.startGameBtn + "/hover"
			buttonPressedPath = self.startGameBtn + "/pressed"
			# 将开始按钮改为不可点击状态
			self.SetSprite(buttonDefaultPath, "textures/ui/off")
			self.SetSprite(buttonHoverPath, "textures/ui/off")
			self.SetSprite(buttonPressedPath, "textures/ui/off")

	def UpdateEnsureUI(self, playerEnsure, startNum):
		ensureNum = len(playerEnsure)
		self.SetVisible(self.waitNotifyPanal, True)
		if not self.autoStartFlag:
			buttonDefaultPath = self.startGameBtn + "/default"
			buttonHoverPath = self.startGameBtn + "/hover"
			buttonPressedPath = self.startGameBtn + "/pressed"
			# 将开始按钮改为可点击状态
			if self.mPlayerId not in playerEnsure:
				self.SetVisible(self.startGameBtn, True)
				self.SetSprite(buttonDefaultPath, "textures/ui/off")
				self.SetSprite(buttonHoverPath, "textures/ui/on")
				self.SetSprite(buttonPressedPath, "textures/ui/click")
			else:
				self.SetVisible(self.startGameBtn, False)
			if ensureNum < startNum:
				text = "即将开始游戏（已确认§c{0}§f/§a{1}§f）".format(ensureNum, startNum)
			else:
				text = "即将开始游戏（已确认§a{0}§f/§a{1}§f）".format(ensureNum, startNum)
			self.SetText(self.waitNotifyLabel, text)

	def WaitNextGame(self):
		text = "游戏正在进行中，请等待下一轮......"
		self.SetVisible(self.waitNotifyPanal, True)
		self.SetText(self.waitNotifyLabel, text)

	@ViewBinder.binding(ViewBinder.BF_ButtonClickUp)
	def OnStartGameBtnClick(self, args):
		self.GetParentPart().ClickStart()
		return ViewRequest.Refresh | ViewRequest.Exit

	def UpdateUI(self, args):
		playerAlive = args["playerAlive"]
		playerEnsure = args["playerEnsure"]
		state = args["state"]
		countDownTime = args["countDownTime"]
		startNum = args["startNum"]
		self.SetVisible(self.waitNotifyPanal, False)
		self.SetVisible(self.startGameBtn, False)
		self.SetVisible(self.countDownLabel, False)
		if state == 3:  # 游戏已开始
			if self.mPlayerId in playerEnsure:
				return
			else:
				self.WaitNextGame()
		if state == 0:  # 等待
			self.UpdateWaitUI(playerAlive)
		if state == 1:  # 确认中
			self.UpdateEnsureUI(playerEnsure, startNum)
		if state == 2:  # 倒计时
			if self.mPlayerId in playerEnsure:
				self.SetVisible(self.countDownLabel, True)
				self.SetText(self.countDownLabel, str(countDownTime // 30))
			else:
				self.UpdateEnsureUI(playerEnsure, startNum)
