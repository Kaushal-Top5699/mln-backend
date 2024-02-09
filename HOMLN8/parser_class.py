import re
from inputValidation import *
from typing import List, Tuple, ChainMap
import pandas as pd
from pathlib import Path

class Parser:
    #constructor method
    def __init__(self,
                 INPUT_FILE_NAME: str = None,
                 LAYER_NAME: str = None,
                 LAYER_GENERATION_TYPE:str=None,
                 PRIMARY_KEY_COLUMN: str = None,
                 primary_key_converted_filename:str=None,
                 FEATURE_COLUMN: str = None,
                 FEATURE_TYPE: str = None,
                 SIMILARITY_METRIC: str = None,
                 THRESHOLD: float = None,
                 RANGE: str = None,
                 MULTI_RANGE: str = None,
                 NUMBER_OF_EQUI_SIZED_SEGMENTS: int = None,
                 LONGITUDE_FEATURE_COLUMN: str = None,
                 LATITUDE_FEATURE_COLUMN: str = None,
                 DATE_METRIC: str = None,
                 DATE_FORMAT: str = None,
                 TIME_FORMAT: str = None,
                 NODE_NUMBER: str = None,
                 EDGE_NUMBER: str = None,
                 CON_COM_NO:str = None,
                 

                 #attribute for interlayer
                 INTER_LAYER_NAME: str = None,
                 INTER_LAYER_GENERATION_TYPE:str=None,
                 #INPUT_FILE_NAME: str = None,this one is already in intra-layer
                 LAYER_1_NAME: str = None,
                 LAYER_1_INPUT_FILE_NAME: str = None,
                 LAYER_2_NAME: str = None,
                 LAYER_2_INPUT_FILE_NAME: str = None
        ):
        self.__INPUT_FILE_NAME = INPUT_FILE_NAME
        self.__LAYER_NAME = LAYER_NAME
        self.__LAYER_GENERATION_TYPE=LAYER_GENERATION_TYPE
        self.__PRIMARY_KEY_COLUMN = PRIMARY_KEY_COLUMN
        self.__primary_key_converted_filename=primary_key_converted_filename
        self.__FEATURE_COLUMN = FEATURE_COLUMN
        self.__FEATURE_TYPE = FEATURE_TYPE
        self.__SIMILARITY_METRIC = SIMILARITY_METRIC
        self.__THRESHOLD = THRESHOLD
        self.__RANGE = RANGE
        self.__MULTI_RANGE = MULTI_RANGE
        self.__NUMBER_OF_EQUI_SIZED_SEGMENTS = NUMBER_OF_EQUI_SIZED_SEGMENTS
        self.__LONGITUDE_FEATURE_COLUMN = LONGITUDE_FEATURE_COLUMN
        self.__LATITUDE_FEATURE_COLUMN = LATITUDE_FEATURE_COLUMN
        self.__DATE_METRIC = DATE_METRIC
        self.__DATE_FORMAT = DATE_FORMAT
        self.__TIME_FORMAT = TIME_FORMAT
        self.__NODE_NUMBER= NODE_NUMBER
        self.__EDGE_NUMBER= EDGE_NUMBER
        self.__CON_COM_NO = CON_COM_NO

        #for interlayer

        self.__INTER_LAYER_NAME = INTER_LAYER_NAME,
        self.__INTER_LAYER_GENERATION_TYPE=INTER_LAYER_GENERATION_TYPE,
        # self.__INPUT_FILE_NAME= INPUT_FILE_NAME, this one is already in intralayer edge
        self.__LAYER_1_NAME=LAYER_1_NAME ,
        self.__LAYER_1_INPUT_FILE_NAME = LAYER_1_INPUT_FILE_NAME,
        self.__LAYER_2_NAME = LAYER_2_NAME,
        self.__LAYER_2_INPUT_FILE_NAME = LAYER_2_INPUT_FILE_NAME

    #getter method for INPUT_FILE_NAME
    def get_INPUT_FILE_NAME(self) -> str:
        return self._INPUT_FILE_NAME

    #setter method for INPUT_FILE_NAME
    def set_INPUT_FILE_NAME(self, layerinfo, INPUT_DIRECTORY) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "INPUT_FILE_NAME":
                #if INPUT_FILE_NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._INPUT_FILE_NAME = os.path.join(INPUT_DIRECTORY,val[1].strip()) 
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._INPUT_FILE_NAME = None

    #getter method for LAYER_NAME
    def get_LAYER_NAME(self) -> str:
        return self._LAYER_NAME

    #setter method for LAYER_NAME
    def set_LAYER_NAME(self, layerinfo, OUTPUT_DIRECTORY, USERNAME,configfilename,layer_ext) -> str:
        exist = False
        configfilename=os.path.basename(configfilename)
        configfilename= configfilename.split(".")
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_NAME":
                LAYER_NAME_val=val[1]
                if  USERNAME== '' or  USERNAME == None:
                    layer_file = configfilename[0] + '_' + LAYER_NAME_val
                else:
                    layer_file =  USERNAME + '_' + configfilename[0] + '_' + LAYER_NAME_val

    #adding the extension for interlayer edges
                layer_file = layer_file + layer_ext
                #if LAYER_NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LAYER_NAME = os.path.join(OUTPUT_DIRECTORY,layer_file)
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_NAME = None

    #getter method for LAYER_GENERATION_TYPE
    def get_LAYER_GENERATION_TYPE(self) -> str:
        return self._LAYER_GENERATION_TYPE

    #setter method for LAYER_GENERATION_TYPE
    def set_LAYER_GENERATION_TYPE(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_GENERATION_TYPE":
                #if LAYER_GENERATION_TYPE exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LAYER_GENERATION_TYPE = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_GENERATION_TYPE = None

    #getter method for PRIMARY_KEY_COLUMN
    def get_PRIMARY_KEY_COLUMN(self) -> str:
        return self._PRIMARY_KEY_COLUMN

    #setter method for PRIMARY_KEY_COLUMN
    def set_PRIMARY_KEY_COLUMN(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "PRIMARY_KEY_COLUMN":
                #if PRIMARY_KEY_COLUMN exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._PRIMARY_KEY_COLUMN = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._PRIMARY_KEY_COLUMN = None

    #getter method for PRIMARY_KEY_COLUMN
    def get_primary_key_converter_for_input_file(self) -> str:
        return self._primary_key_converted_filename

    #the method converts the primary keys ids of the input file to unique ids starting from 1 and incrementing upto n and store the converted id information in a csv file in the directory primary_key_converter 
    def set_primary_key_converter_for_input_file(self,input_directory,converter_primary_key_input_filename,INPUT_FILE_NAME,PRIMARY_KEY_COLUMN) -> str:
        primary_key_column_list=  PRIMARY_KEY_COLUMN.split(",") 
        #put the primary key column name in a list required by pandas to a a specific column information
        #primary_key_column_list.append(PRIMARY_KEY_COLUMN)    
        #input_file = inputfile_folder  / INPUT_FILE_NAME
        input_file = os.path.join(input_directory, INPUT_FILE_NAME)
        # reading CSV file
        df = pd.read_csv(input_file, usecols=primary_key_column_list,index_col=False)
        #convert all column value to str
        df = df.astype(str)
        #this is the initial empty list used to merge multiple column values into one for the csv
        com_list=[]
        first_iter=0
        for col in primary_key_column_list:
            first_iter=first_iter+1
            if first_iter==1:
                com_list=df[col]
            else:
                com_list=com_list+","
                com_list=com_list+df[col]
        
       # print(list(com_list))
        size_of_column=len(df)
        converted_primary_key_column= list(range(1, size_of_column+1))
        df["Node_id"] =   converted_primary_key_column
        df["Primary_key_id"] = list(com_list)
        #print(df)
        usecol=["Node_id","Primary_key_id"]
        df[usecol].to_csv(converter_primary_key_input_filename, index=None)
        self._primary_key_converted_filename=converter_primary_key_input_filename
 
    #getter method for PRIMARY_KEY_COLUMN for interlayer
    def get_primary_key_converter_for_input_file_inter_layer(self) -> str:
        return self._primary_key_converted_filename

    #for interlayer the method converts the primary keys ids of the input file to unique ids starting from 1 and incrementing upto n and store the converted id information in a csv file in the directory primary_key_converter 
    def set_primary_key_converter_for_input_file_inter_layer(self,input_directory,converter_primary_key_input_filename,INPUT_FILE_NAME,PRIMARY_KEY_COLUMN) -> str:
        primary_key_column_list=  PRIMARY_KEY_COLUMN.split(",") 
        #put the primary key column name in a list required by pandas to a a specific column information
        #primary_key_column_list.append(PRIMARY_KEY_COLUMN)    
        #input_file = inputfile_folder  / INPUT_FILE_NAME
        input_file = os.path.join(input_directory, INPUT_FILE_NAME)
        # reading CSV file
        df = pd.read_csv(input_file, usecols=primary_key_column_list,index_col=False)
        #convert all column value to str
        df = df.astype(str)
        #this is the initial empty list used to merge multiple column values into one for the csv
        com_list=[]
        first_iter=0
        for col in primary_key_column_list:
            first_iter=first_iter+1
            if first_iter==1:
                com_list=df[col]
            else:
                com_list=com_list+","
                com_list=com_list+df[col]
        
       # print(list(com_list))
        size_of_column=len(df)
        converted_primary_key_column= list(range(1, size_of_column+1))
        df["Node_id"] =   converted_primary_key_column
        df["Primary_key_id"] = list(com_list)
        #print(df)
        usecol=["Node_id","Primary_key_id"]
        df[usecol].to_csv(converter_primary_key_input_filename, index=None)
        self._primary_key_converted_filename=converter_primary_key_input_filename

    #getter method for FEATURE_COLUMN
    def get_FEATURE_COLUMN(self) -> str:
        return self._FEATURE_COLUMN

    #setter method for FEATURE_COLUMN
    def set_FEATURE_COLUMN(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "FEATURE_COLUMN":
                #if FEATURE_COLUMN exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._FEATURE_COLUMN = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._FEATURE_COLUMN = None

    #getter method for FEATURE_TYPE
    def get_FEATURE_TYPE(self) -> str:
        return self._FEATURE_TYPE

    #setter method for FEATURE_TYPE
    def set_FEATURE_TYPE(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "FEATURE_TYPE":
                #if FEATURE_TYPE exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._FEATURE_TYPE = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._FEATURE_TYPE = None

    #getter method for SIMILARITY_METRIC
    def get_SIMILARITY_METRIC(self) -> str:
        return self._SIMILARITY_METRIC

    #setter method for SIMILARITY_METRIC
    def set_SIMILARITY_METRIC(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "SIMILARITY_METRIC":
                #if SIMILARITY_METRIC exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._SIMILARITY_METRIC = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._SIMILARITY_METRIC = None

    #getter method for THRESHOLD
    def get_THRESHOLD(self) -> float:
        return self._THRESHOLD

    #setter method for THRESHOLD
    def set_THRESHOLD(self, layerinfo) -> float:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "THRESHOLD":
                #if THRESHOLD exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._THRESHOLD = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._THRESHOLD = None

    #getter method for RANGE
    def get_RANGE(self) -> str:
        return self._RANGE

    #setter method for RANGE
    def set_RANGE(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "RANGE":
                #if RANGE exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._RANGE = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._RANGE = None

    #getter method for MULTI_RANGE
    def get_MULTI_RANGE(self) -> str:
        return self._MULTI_RANGE

    #setter method for MULTI_RANGE
    def set_MULTI_RANGE(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "MULTI_RANGE":
                #if MULTI_RANGE exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._MULTI_RANGE = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._MULTI_RANGE = None

    #getter method for NUMBER_OF_EQUI_SIZED_SEGMENTS
    def get_NUMBER_OF_EQUI_SIZED_SEGMENTS(self) -> int:
        return self._NUMBER_OF_EQUI_SIZED_SEGMENTS

    #setter method for NUMBER_OF_EQUI_SIZED_SEGMENTS
    def set_NUMBER_OF_EQUI_SIZED_SEGMENTS(self, layerinfo) -> int:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "NUMBER_OF_EQUI_SIZED_SEGMENTS":
                #if NUMBER_OF_EQUI_SIZED_SEGMENTS exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._NUMBER_OF_EQUI_SIZED_SEGMENTS = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._NUMBER_OF_EQUI_SIZED_SEGMENTS = None

    #getter method for LONGITUDE_FEATURE_COLUMN
    def get_LONGITUDE_FEATURE_COLUMN(self) -> str:
        return self._LONGITUDE_FEATURE_COLUMN

    #setter method for LONGITUDE_FEATURE_COLUMN
    def set_LONGITUDE_FEATURE_COLUMN(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LONGITUDE_FEATURE_COLUMN":
                #if LONGITUDE_FEATURE_COLUMN exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LONGITUDE_FEATURE_COLUMN = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LONGITUDE_FEATURE_COLUMN = None

    #getter method for LATITUDE_FEATURE_COLUMN
    def get_LATITUDE_FEATURE_COLUMN(self) -> str:
        return self._LATITUDE_FEATURE_COLUMN

    #setter method for LATITUDE_FEATURE_COLUMN
    def set_LATITUDE_FEATURE_COLUMN(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LATITUDE_FEATURE_COLUMN":
                #if LATITUDE_FEATURE_COLUMN exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LATITUDE_FEATURE_COLUMN = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LATITUDE_FEATURE_COLUMN = None

    #getter method for DATE_METRIC
    def get_DATE_METRIC(self) -> str:
        return self._DATE_METRIC

    #setter method for DATE_METRIC
    def set_DATE_METRIC(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "DATE_METRIC":
                #if DATE_METRIC exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._DATE_METRIC = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._DATE_METRIC = None

    #getter method for DATE_FORMAT
    def get_DATE_FORMAT(self) -> str:
        return self._DATE_FORMAT

    #setter method for DATE_FORMAT
    def set_DATE_FORMAT(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "DATE_FORMAT":
                #if DATE_FORMAT exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._DATE_FORMAT = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._DATE_FORMAT = None

    #getter method for TIME_FORMAT
    def get_TIME_FORMAT(self) -> str:
        return self._TIME_FORMAT

    #setter method for TIME_FORMAT
    def set_TIME_FORMAT(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "TIME_FORMAT":
                #if TIME_FORMAT exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._TIME_FORMAT = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._TIME_FORMAT = None

    #getter method for Node_Number
    def get_NODE_NUMBER(self) -> str:
        return self._NODE_NUMBER

    #setter method for TIME_FORMAT
    def set_NODE_NUMBER(self, nodelist) -> str:
                #strip is used to remove leading and ending spaces
                self._NODE_NUMBER = nodelist
    
    #getter method for Node_Number
    def get_EDGE_NUMBER(self) -> str:
        return self._EDGE_NUMBER

    #setter method for TIME_FORMAT
    def set_EDGE_NUMBER(self,edgelist) -> str:
                #strip is used to remove leading and ending spaces
                self._EDGE_NUMBER = edgelist

    #getter method for Node_Number
    def get_CON_COM_NO(self) -> str:
        return self._CON_COM_NO

    #setter method for TIME_FORMAT
    def set_CON_COM_NO(self,con_com) -> str:
                #strip is used to remove leading and ending spaces
                self._CON_COM_NO = con_com

    #getter method for INTER_LAYER_NAME
    def get_INTER_LAYER_NAME(self) -> str:
        return self._INTER_LAYER_NAME
    
    #setter method for INTER_LAYER_NAME
    def set_INTER_LAYER_NAME(self, layerinfo, OUTPUT_DIRECTORY, USERNAME,configfilename,layer_ext) -> str:
                            exist = False
                            configfilename= os.path.basename(configfilename)
                            configfilename=configfilename.split(".")
                            for val in layerinfo:
                                val = val.split("=")
                                if val[0] == "INTER_LAYER_NAME":
                                    LAYER_NAME_val=val[1]
                                    if  USERNAME== '' or  USERNAME == None:
                                        layer_file =  configfilename[0] + '_' + LAYER_NAME_val
                                    else:
                                        layer_file =  USERNAME + '_' + configfilename[0] + '_' + LAYER_NAME_val

                            #adding the extension for interlayer edges
                                    inter_layer_file = layer_file + layer_ext
                                    #if LAYER_NAME exists in buffer, then exit is set to True
                                    exist = True
                                    #strip is used to remove leading and ending spaces
                                    self._INTER_LAYER_NAME = os.path.join(OUTPUT_DIRECTORY,inter_layer_file)
                                    break

                              #if the attribute does not exist, set the value to None
                            if exist == False:
                                self._INTER_LAYER_NAME = None

    #getter method for INTER_LAYER_GENERATION_TYPE
    def get_INTER_LAYER_GENERATION_TYPE(self) -> str:
        return self._INTER_LAYER_GENERATION_TYPE

    #setter method for INTER_LAYER_GENERATION_TYPE
    def set_INTER_LAYER_GENERATION_TYPE(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "INTER_LAYER_GENERATION_TYPE":
                #if INTER_LAYER_GENERATION_TYPE exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._INTER_LAYER_GENERATION_TYPE = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._INTER_LAYER_GENERATION_TYPE = None

    #getter method for LAYER 1 NAME
    def get_LAYER_1_NAME(self) -> str:
        return self._LAYER_1_NAME

    #setter method for LAYER 1 NAME
    def set_LAYER_1_NAME(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_1_NAME":
                #if LAYER 1 NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LAYER_1_NAME = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_1_NAME = None

    #getter method for   LAYER_1_INPUT_FILE_NAME
    def get_LAYER_1_INPUT_FILE_NAME(self) -> str:
        return self._LAYER_1_INPUT_FILE_NAME

    #setter method for   LAYER_1_INPUT_FILE_NAME
    def set_LAYER_1_INPUT_FILE_NAME(self, layerinfo,INPUT_DIRECTORY) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_1_INPUT_FILE_NAME":
                #if LAYER_1_INPUT_FILE_NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LAYER_1_INPUT_FILE_NAME = os.path.join(INPUT_DIRECTORY,val[1].strip())
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_1_INPUT_FILE_NAME = None

    #getter method for LAYER 2 NAME
    def get_LAYER_2_NAME(self) -> str:
        return self._LAYER_2_NAME

    #setter method for LAYER 1 NAME
    def set_LAYER_2_NAME(self, layerinfo) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_2_NAME":
                #if LAYER 1 NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading and ending spaces
                self._LAYER_2_NAME = val[1].strip()
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_2_NAME = None

    #getter method for   LAYER_2_INPUT_FILE_NAME
    def get_LAYER_2_INPUT_FILE_NAME(self) -> str:
        return self._LAYER_2_INPUT_FILE_NAME

    #setter method for LAYER_2_INPUT_FILE_NAME
    def set_LAYER_2_INPUT_FILE_NAME(self, layerinfo,INPUT_DIRECTORY) -> str:
        exist = False
        for val in layerinfo:
            val = val.split("=")
            if val[0] == "LAYER_2_INPUT_FILE_NAME":
                #if LAYER_2_INPUT_FILE_NAME exists in buffer, then exit is set to True
                exist = True
                #strip is used to remove leading( and ending spaces
                self._LAYER_2_INPUT_FILE_NAME = os.path.join(INPUT_DIRECTORY, val[1].strip())
                break
        #if the attribute does not exist, set the value to None
        if exist == False:
            self._LAYER_2_INPUT_FILE_NAME = None
