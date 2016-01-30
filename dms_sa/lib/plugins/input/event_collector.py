from lib.base.inputbase import InputBase
from lib.services.servicecontext import ServiceContext
from lib.events import EventFactory
import json
from lib.utils import Logger
from lib.exceptions import *
from kafka import KafkaConsumer

class EventCollector(InputBase,Logger):

    def getPluginName(self):
        return "event_collector"

    def run(self):
        ctx = ServiceContext()
        queue = ctx.getQueueService()
        self._initializeconsumer()
        for msg in self.consumer:
            value = bytearray(msg.value)
            topic = msg.topic
            try:
                jsondata = json.loads(str(value))
                eventType = jsondata["eventName"]
                jsondata['topic'] = topic
                queue.put(EventFactory.getEvent(eventType,jsondata))
            except IndexError,e:
                self.error(e)




    def _initializeconsumer(self):
        constructor="KafkaConsumer(%s,group_id=%s,bootstrap_servers=%s)"
        topics = self.event_topic
        group_id = self.event_groupid
        bootstrap_server = self.kafka_broker
        str = constructor % (topics,group_id,bootstrap_server)
        self.consumer = eval(str)



