from enum import Enum 

class DistanceUnit(Enum):
    MILES = "MILES"
    KILOMETERS = "KILOMETERS"

class DateEnum(Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

class Metric(Enum):
    EQUALITY = "EQUALITY"
    EUCLIDEAN = "EUCLIDEAN"
    JACCARD = "JACCARD"
    COSINE = "COSINE"
    HAVERSINE="HAVERSINE"
    MULTI_RANGE = "MULTI_RANGE"
    RANGE = "RANGE"

class FeatureType(Enum):
    NUMERIC = "NUMERIC"
    NOMINAL = "NOMINAL"
    GEOGRAPHIC = "GEOGRAPHIC"
    TIME = "TIME"
    DATE = "DATE"
    SET = "SET"
    TEXT = "TEXT"

class GeneratedLayerType(Enum):
    User_Generated = "User_Generated"
    System_Generated = "System_Generated"

class directory_name(Enum):
    log_files="log-files"
    system_files="system"
    tmp_files="tmp"
    primary_key_converter_for_inputfiles="primary_key_converter_for_inputfiles"

class extension_layer_name(Enum):
    layer_file=".net"
    inter_layer_file=".ilf"
    hash_table_file="_gen.bin"
