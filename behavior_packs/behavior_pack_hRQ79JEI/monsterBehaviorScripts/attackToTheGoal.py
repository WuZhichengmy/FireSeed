# -*- coding: utf-8 -*-
#

import mod.server.extraServerApi as serverApi
import math

CustomGoalCls = serverApi.GetCustomGoalCls()

class AttackToTheGoal(CustomGoalCls):
    def __init__(self, entityId, argsJson):
        CustomGoalCls.__init__(self, entityId, argsJson)

    # def _HasTarget(self):
    #     #是否有仇恨目标
    #     comp = serverApi.GetEngineCompFactory().CreateAction(self.GetEntityId())
    #     targetId = comp.GetAttackTarget()
    #     hasTarget = targetId != "-1"
    #     return hasTarget

    # 设置攻击目标
    def _SetAttackToGoal(self):
        comp = serverApi.GetEngineCompFactory().CreateAction(self.GetEntityId())
        identifier = 'monster:block'
        comp.SetAttackTarget(identifier)
        # comp.SetAttackTarget("monster_block")

    def CanUse(self):
        # return True or False
        return True

    def CanContinueToUse(self):
        # return True or False
        return True

    def CanBeInterrupted(self):
        # return True or False
        return True

    def Start(self):
        print "AttackToTheGoal Start", self.GetEntityId()
        # 攻击目标
        self._SetAttackToGoal()

    def Stop(self):
        print "AttackToTheGoal Stop", self.GetEntityId()

    def Tick(self):
        print "AttackToTheGoal Tick", self.GetEntityId()
        self._SetAttackToGoal()