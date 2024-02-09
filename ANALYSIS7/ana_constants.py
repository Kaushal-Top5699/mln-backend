from enum import Enum

class ana_directory_name(Enum):
    log_files="log-files"
    system_files="system"
    tmp_files="tmp"

class ana_DateEnum(Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

class ana_GeneratedAnalysisType(Enum):
    User_Generated = "User_Generated"
    System_Generated = "System_Generated"

class ana_extension_layer_name(Enum):
    layer_file=".net"
    hash_table_file="_gen.bin"
    config_file=".ana"
    log_file=".log"