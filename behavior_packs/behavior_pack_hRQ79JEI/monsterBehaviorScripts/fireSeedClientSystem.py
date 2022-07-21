# -*- coding: utf-8 -*-
#
import mod.client.extraClientApi as clientApi

compFactory = clientApi.GetEngineCompFactory()

class FireSeedClientSystem(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(FireSeedClientSystem, self).__init__(namespace, name)
        print "==== FireSeedClientSystem Init ===="

        # 函数名为Destroy才会被调用，在这个System被引擎回收的时候会调这个函数来销毁一些内容
        def Destroy(self):
            pass