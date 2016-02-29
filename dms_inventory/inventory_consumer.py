from kafka import KafkaConsumer
import avro.io
import avro.schema
import io
import json
from models import ObjectFactory
from connects import ConnectFactory
from util import logger
from dsoSynczoo.full_sync_redis import full_sync
import time
from util import ConfigurationHelper

avro_schema = """
    {"namespace": "com.dadycloud.sa",
    "type": "record",
    "name": "event",
    "fields": [
                 {"name": "timestamp", "type": "long"},
                 {"name": "src",       "type": "string"},
                 {"name": "host_ip",   "type": "string"},
                 {"name": "rawdata",   "type": "bytes"}
            ]
            }
         """



class KafkaCollector():
    def __init__(self):
#        self.app_home = os.path.dirname(os.path.abspath(__file__))
#        os.chdir(self.app_home)
        config = ConfigurationHelper().config
        self.kafka_host = config.get("Kafka","kafka_broker")
        self.kafka_topic = config.get("Kafka","kafka_topic")
        self.kafka_group = config.get("Kafka","kafka_group")
        self.consumer = KafkaConsumer(self.kafka_topic,self.kafka_group,bootstrap_servers=[self.kafka_host])
        self.schema = avro.schema.parse(avro_schema)

    def run(self):
        client = ConnectFactory().getConnect("redis")
        self.fullsync(client)
        for msg in self.consumer:
            kafkamsg = self._decodemsg(msg)
            try:
                logger.info("message handling(%s)" % kafkamsg)
                if kafkamsg["timestamp"] < self.snap_shot:
                    logger.warning("message is oudate. %s" % kafkamsg)
                    continue
                jsondata = json.loads(kafkamsg['rawdata'])
                ObjectFactory.fromjson(jsondata["message"]).execute(client)
            except:
                logger.error("message execute error(%s)" % jsondata)


    def fullsync(self,client):
        logger.info("start to full sync from dso...")
        client.flushall()
        logger.info("start to clear the db...")
        event_sourcing = full_sync()
        logger.info("finish to get data from dso.")
        self.snap_shot = time.time()
        for event in event_sourcing:
            ObjectFactory.fromjson(event).execute(client)
        logger.info("finsih to full sync. the event amount is: %s" %  len(event_sourcing))


    def _decodemsg(self,msg):
        value = bytearray(msg.value)
        bytes_reader = io.BytesIO(value[5:])
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(self.schema)
        message = reader.read(decoder)
        return message

if __name__ == '__main__':
    from util import Logger
    Logger.basicConfig()
    kafka_runner = KafkaCollector()
    kafka_runner.run()
