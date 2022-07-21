# -*- coding: utf-8 -*-
#
import mod.server.extraServerApi as serverApi
from mod.common.minecraftEnum import BiomeType, Change, EntityType

compFactory = serverApi.GetEngineCompFactory()


class FireSeedServerSystem(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(FireSeedServerSystem, self).__init__(namespace, name)
        print "==== FireSeedServerSystem Init ===="
    #     self.ListenEvent()
    #     self.playerId = None
    #     self.entityId = None
    #     # 如需隐藏饥饿度请使用extraClientApi的HideHungerGui
    #     # comp.SetDisableHunger(True)
    #     # 设置攻击对象
    #
    # def ListenEvent(self):
    #     self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "AddServerPlayerEvent",
    #                         self, self.OnAddServerPlayerEvent)
    #
    # def createEntity(self, playerId):
    #     comp = compFactory.CreatePos(playerId)
    #     pos = comp.GetPos()
    #     # 修改位置
    #     pos = (pos[0] + 10, pos[1], pos[2] + 1)
    #     comp = compFactory.CreateRot(playerId)
    #     rot = comp.GetRot()
    #     # 修改类型
    #     result = self.CreateEngineEntityByTypeStr('monster:zombie1', pos, rot)
    #
    # def OnAddServerPlayerEvent(self, args):
    #     # 玩家进入世界时创建自定义生物
    #     comp1 = serverApi.GetEngineCompFactory().CreateMobSpawn(serverApi.GetLevelId())
    #     comp1.SpawnCustomModule(BiomeType.plains, Change.Add, EntityType.Mob, 10, 1, 10, 2, 0, 7)
    #     # 设置自定义刷怪
    #     comp = compFactory.CreateGame(serverApi.GetLevelId())
    #     comp.AddTimer(3.0, self.createEntity, args['id'])
