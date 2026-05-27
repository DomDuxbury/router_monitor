from dataclasses import dataclass, fields
from datetime import datetime

type MacAddress = str
type DNSGroup = str
type connectionTime = str


@dataclass
class Data:
    downloaded_bytes: int
    uploaded_bytes: int

    def __str__(self):
        data_str = ""
        for field in fields(self):
            field_value = self.__dict__[field.name]
            is_byte_field = field.name in ["downloaded_bytes", "uploaded_bytes"]
            match field_value:
                case _ if is_byte_field and field_value > 1000000000:
                    data_str += f"{field.name}={str(round(field_value / 100000000) / 10) + 'Gb'}"
                case _ if is_byte_field and field_value > 1000000:
                    data_str += (
                        f"{field.name}={str(round(field_value / 100000) / 10) + 'Mb'}"
                    )
                case _ if is_byte_field and field_value > 1000:
                    data_str += (
                        f"{field.name}={str(round(field_value / 100) / 10) + 'Kb'}"
                    )
                case _:
                    data_str += f"{field.name}={field_value}"
            data_str += ", "

        return "{" + data_str[0 : len(data_str) - 2] + "}"


@dataclass
class DeviceData(Data):
    mac_address: MacAddress

    def __repr__(self):
        return self.__str__() + "\n"


@dataclass
class AppData(Data):
    dns_group: DNSGroup

    def __repr__(self):
        return self.__str__() + "\n"


@dataclass
class HourlyData(Data):
    hour_beginning: int
    device: MacAddress | str

    def __repr__(self):
        return self.__str__() + "\n"


@dataclass
class DataDelta(Data):
    delta_start: datetime
    delta_end: datetime
    length_secs: float

    def __post_init__(self):
        self.length_secs = (self.delta_end - self.delta_start).total_seconds()

    def __repr__(self):
        return self.__str__() + "\n"
