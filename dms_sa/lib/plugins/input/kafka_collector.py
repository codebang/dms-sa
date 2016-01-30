from lib.base.inputbase import InputBase
from lib.services.servicecontext import ServiceContext
import avro.io
import avro.schema
import io
from lib.events import EventFactory
import json
from lib.utils import Logger
from lib.exceptions import *
from kafka import KafkaConsumer
from lib.utils.constants import avro_schema
class KafkaCollector(InputBase,Logger):

    def getPluginName(self):
        return "kafka_collector"

    def run(self):
        ctx = ServiceContext()
        queue = ctx.getQueueService()
        self._initializeschema()
        self._initializeconsumer()
        for msg in self.consumer:
            value = bytearray(msg.value)
            topic = msg.topic
            bytes_reader = io.BytesIO(value[5:])
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(self.schema)
            kafkamsg = reader.read(decoder)
            try:
                jsondata = json.loads(kafkamsg['rawdata'])
                eventType = jsondata["eventName"]
                jsondata['topic'] = topic
                queue.put(EventFactory.getEvent(eventType,jsondata))
            except InputError,e:
                self.error(str(e))
            except:
                self.error("message format is invalid(%s)" % jsondata)


    def _initializeschema(self):
        self.schema = avro.schema.parse(avro_schema)

    def _initializeconsumer(self):
        constructor="KafkaConsumer(%s,group_id=%s,bootstrap_servers=%s)"
        topics = self.kafka_topics
        group_id = self.kafka_groupid
        bootstrap_server = self.kafka_broker
        str = constructor % (topics,group_id,bootstrap_server)
        self.consumer = eval(str)

    def _decodemsg(self,msg):
        value = bytearray(msg.value)
        bytes_reader = io.BytesIO(value[5:])
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.schema)
        message = reader.read(decoder)
        return message

