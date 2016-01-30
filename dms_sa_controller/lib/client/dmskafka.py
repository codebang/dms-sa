from kafka import SimpleProducer, KafkaClient
from ..utils import singleton,logger
from .. services.servicecontext import ServiceContext
import avro.io
import avro.schema
import io
from ..utils.constants import avro_schema

@singleton
class DmsKafkaClient(object):
    def __init__(self):
        config = ServiceContext().getConfigService()
        broker_list = config.get("KafkaProducer","kafka_broker")
        self.producer = SimpleProducer(broker_list)
        self.zabbix_alert = config.get("KafkaProducer","zabbix_alert_topic")

    def sendPackageTimeout(self,accountId,severity,message):
        message = {
            "accountId":accountId,
            "severity": severity,
            "description": message
        }
        all = {
            "timestamp": 1L,
            "src": "rundeck",
            "host_ip": "10.74.113.101",
            "rawdata":message
        }
        schema = avro.schema.parse(avro_schema)
        writer = avro.io.DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(all,encoder)
        try:
            self.producer.send_messages(b"%s"%self.zabbix_alert,bytes_writer.getvalue())
        except:
            logger.error("occur error when send package timeout message to zabbix alert topic")