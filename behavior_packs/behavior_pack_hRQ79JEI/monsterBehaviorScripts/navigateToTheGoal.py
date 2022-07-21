# -*- coding: utf-8 -*-
#

import mod.server.extraServerApi as serverApi

CustomGoalCls = serverApi.GetCustomGoalCls()


class NavigateToTheGoal(CustomGoalCls):
    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)

    def _GetPos(self, entityId):
        comp = serverApi.GetEngineCompFactory().CreatePos(entityId)
        return comp.GetPos()

    # 寻找带摧毁目标
    def _MoveToTarget(self, myCalllback=None):
        # 获取目标的位置：有待更改
        # targetPos = (7.00, -61, 20.00)
        # targetPos = (142.00, 70, -24.00)
        targetPos = (133.00, 73, -61.00)
        # 向目标点移动
        comp = serverApi.GetEngineCompFactory().CreateMoveTo(self.GetEntityId())
        comp.SetMoveSetting(targetPos, 1.0, 7000)

    def CanUse(self):
        return True

    def CanContinueToUse(self):
        return True

    def CanBeInterrupted(self):
        return True

    def Start(self):
        print "NavigateToTheGoal Start", self.GetEntityId()
        # 向目标移动
        self._MoveToTarget()

    def Stop(self):
        print "NavigateToTheGoal Stop", self.GetEntityId()

    def Tick(self):
        pass
