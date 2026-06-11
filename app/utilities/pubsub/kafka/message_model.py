from dataclasses import dataclass


@dataclass
class KafkaMessage:
    body: str
    topic: str
    partition: int
    offset: int
