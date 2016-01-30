import IMultithreadChildPlugin
from yapsy.PluginManager import PluginManagerSingleton

class PluginBase(IMultithreadChildPlugin.IMultithreadChildPlugin):
    def getCategory(self):
        return None

    def getPluginName(self):
        return None

    def __getattr__(self, item):
        manager = PluginManagerSingleton.get()
        return manager.readOptionFromPlugin(self.getCategory(),self.getPluginName(),item)


