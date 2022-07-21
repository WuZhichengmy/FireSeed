# -*- coding: utf-8 -*-
from Meta.ClassMetaManager import sunshine_class_meta
from Meta.TypeMeta import PCoordinate, PDict, PArray, PEnum, PVector3, PGameObjectArea, PBool, PInt, PCustom
from Preset.Model import PartBaseMeta
from Meta.EnumMeta import DefEnum


def getTeamName(currentPart):
	try:
		preset = currentPart.GetParent()
		if preset is None:
			return {}
		part = preset.GetPartByType("TeamPart")
		if not (part is None):
			return part.GetALLQueueName()
		else:
			return {}
	except Exception:
		import traceback
		traceback.print_exc()
		return {}


@sunshine_class_meta
class StartLogicPartMeta(PartBaseMeta):
	CLASS_NAME = "StartLogicPart"
	PROPERTIES = {
		'gameMinPlayerNum': PInt(sort=11, text='最低人数', group="零件设置", min=1, tip='达到最低人数后才能开始游戏。'),
		'autoStartFlag': PBool(sort=12, text='是否自动开始', group="零件设置", tip='若勾选，则达到最低人数后会自动开始游戏。'),
		'countDownTime': PInt(sort=13, text='倒计时长（秒）', group="零件设置", min=3, max=120, tip='所有人点击“开始游戏”按钮后，会经过倒计时后真正开始游戏。'),
		'clearDropsFlag': PBool(sort=14, text='是否清除掉落物', group="零件设置", tip='若勾选，则在开始游戏时会清除掉所有的掉落物。'),
		"area": PGameObjectArea(
			sort=15,
			text="等待区域", tip='游戏开始前，会将玩家传送到等待区域内的随机坐标。',
			children={
				'min': PVector3(sort=0, text="顶点1"),
				'max': PVector3(sort=1, text="顶点2")
			},
		),
		'posOption': PEnum(
			sort=16, text='开始游戏坐标', group="传送方式", enumType='startPosOption',
			tip='开始游戏时，会将玩家传送到指定的坐标。\n按队伍区分：不同的队伍会传送到不同的坐标。\n随机坐标：所有人分别传送到随机的坐标。\n'
		),
		"teamPosList":
			PArray(
				text="队伍坐标", visible=False,
				sort=20,
				func=lambda x: {'visible': x.posOption == 1},
				childAttribute=PDict(children={"teamName": PCustom(text='队伍', editAttribute='MCEnum', extend=getTeamName), "pos": PCoordinate(text='世界坐标')})
			),
		"randomPointList":
			PArray(
				text="随机坐标列表",
				sort=20,
				func=lambda x: {'visible': x.posOption == 0},
				childAttribute=PDict(children={"pos": PCoordinate(text='世界坐标')})
			),
	}

	@staticmethod
	def registerEnum():
		DefEnum("startPosOption", {0: '随机坐标', 1: '按队伍区分'})
