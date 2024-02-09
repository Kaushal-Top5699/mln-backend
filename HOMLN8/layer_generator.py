import csv
from itertools import combinations
from similarityMetric import *
import datetime
from inputValidation import *
import time
from pathlib import Path
from parser_class import *
import os
from rules_class_for_mln import *
from layer_generation import * 
import csv
from collections import defaultdict
import platform
from pandas import *
import shutil
import sys
import re
from enum import Enum, auto
from dataclasses import dataclass
import pickle
from os.path import exists
from mapping_primary_column import *
import os.path
from log_file_generation import *
import time
from os import path
from constants import *
from tabulate import tabulate
from multiprocessing import Pool
import networkx as nx
import sys
import gc

#create the name for the layer
def layer_file_name(username, configfilename,buffer,layer_ext):
    for ele in buffer:
         val=ele.split("=")
         if val[0]=="LAYER_NAME":
              LAYER_NAME=val[1]

         if val[0]=="INTER_LAYER_NAME":
              LAYER_NAME=val[1]
              
    if username == '' or username == None:
        layer_file = configfilename + '_' + LAYER_NAME + layer_ext
    else:
        layer_file = username + '_' + configfilename + '_' + LAYER_NAME + layer_ext
   
    return layer_file

#create the name for the hash table
def hash_table_file_name(username, configfilename,ext):
    if username == '' or username == None:
        config_file = configfilename + ext
    else:
        config_file = username + '_' + configfilename + ext
    return config_file

#function to return the column index number
def column_no_of_a_feature(input_folder,input_filename,feature_name):
        filename = os.path.join(input_folder, input_filename)
        f = csv.DictReader(open(filename), delimiter = ",")
        fi = f.fieldnames
        index_num = fi.index(feature_name)
        return index_num 

#create the name for the primary key converted file
def primary_key_converted_input_file_name(username,configfilename,path_converted_file,inputfilename,buffer):
    for ele in buffer:
         val=ele.split("=")
         if val[0]=="LAYER_NAME":
              LAYER_NAME=val[1]
              break
         
    primary_key_converted_file=username+"_"+configfilename+"_"+LAYER_NAME+".map"
    converted_file = os.path.join(path_converted_file, primary_key_converted_file)
    return converted_file

#create the name for the hash table
def primary_key_converted_input_file_name_for_inter_layer_generation(username,configfilename,path_converted_file,inputfilename,buffer,layer_name):
   # x=configfilename.split(".")
    for ele in buffer:
            val=ele.split("=")
            if layer_name=="LAYER_1_NAME":
                if val[0]==layer_name:
                            LAYER_NAME=val[1]
                            break

            elif layer_name=="LAYER_2_NAME":
                if val[0]==layer_name:
                    LAYER_NAME=val[1]
                    break
            
    primary_key_converted_file=username+"_"+configfilename+"_"+LAYER_NAME+".map"
    
    #converted_file=path_converted_file/primary_key_converted_file
    converted_file = os.path.join(path_converted_file, primary_key_converted_file)
    return converted_file

#the function puts the edges of the generated layer in list of tuple format for finding the number of connected component. The python package for finding connected component no requires this format for edgelist
def edge_list_con_com(edge_list):
     edgelist_con_com_val=[]
     for ele in edge_list:
          ele=ele.split(",")
          edgelist_con_com_val.append((ele[0],ele[1]))   
     return edgelist_con_com_val
 

def del_file_tmp_dir(tmp_folder):
    #delete files from the tmp directory
    for filename in os.listdir(tmp_folder):
                file_path = os.path.join(tmp_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    pass


def main(MLN_USR,configfilename):
    #relpath finds the path rom the given directory
    configfiletoopen= path.relpath(configfilename)
    os_name = platform.system()
    #count the no of centralt processing units for the machine the code runs
    cpu_no=os.cpu_count()
    #separates the configfilename from the absolute path
    config_file = os.path.basename(configfilename)
    #separates the username from the absolute path
    MLN_USR_basename=os.path.basename(MLN_USR)
    config_file_first_portion = config_file.split(".")
    node_column = 0
    nodeList = []
    edgeList = []
    similarityObj = SimilarityObject()
    inputValidationObj = InputValidationObj()
    log_file_object=LogObject()
    generate_layer_obj=LAYER_GENERATION()
    #join the system folder to the user directory
    system_folder=os.path.join(MLN_USR, directory_name.system_files.value)
    #if the path for hash table does not exist, a system folder is created
    system_path_exist = os.path.isdir(system_folder)
    if system_path_exist==False:
         os.mkdir(system_folder)
    #join the log folder to the user directory
    log_folder=os.path.join(MLN_USR,directory_name.log_files.value )
    log_path_exist = os.path.isdir(log_folder)
    #if the path for log files does not exist, a log folder is created
    if log_path_exist==False:
         os.mkdir(log_folder)   
    
    tmp_folder=os.path.join(MLN_USR, directory_name.tmp_files.value)
    tmp_path_exist = os.path.isdir(tmp_folder)
    #if the path for tmp files does not exist, a tmp folder is created
    if tmp_path_exist==False:
         os.mkdir(tmp_folder)
    
    #generate log file name from layer file
    log_file_name=config_file+".log"

    #join log file with complete path
    log_file = os.path.join(log_folder, log_file_name)
    #open a log file for the configuration file
    log_file_object.open_log_file_for_each_layer(log_file)

    #join primary key converted folder with complete path
    primary_key_converted_folder_for_input_file=os.path.join(MLN_USR, directory_name.primary_key_converter_for_inputfiles.value)
    primary_key_converted_folder_for_input_file_path_exist = os.path.isdir(primary_key_converted_folder_for_input_file)
    #if the path for primary key converted_folder does not exist, a folder is created
    if primary_key_converted_folder_for_input_file_path_exist==False:
        os.mkdir(primary_key_converted_folder_for_input_file)
    
    #open the configuration file for reading
    with open(configfiletoopen, mode='r',encoding="utf8") as  config_file:
        #lines contain all the lines of config file in a list, each line is an element of the list
        lines = config_file.readlines()
        INPUT_DIRECTORY = lines[0].split("=")[1]
        INPUT_DIRECTORY = MLN_USR +  INPUT_DIRECTORY.replace("$MLN_USR","")
        #rstrip removes the last \n at the end
        INPUT_DIRECTORY = INPUT_DIRECTORY.rstrip("\n")
        OUTPUT_DIRECTORY = lines[1].split("=")[1]
        OUTPUT_DIRECTORY = MLN_USR + OUTPUT_DIRECTORY.replace("$MLN_USR","")
        OUTPUT_DIRECTORY = OUTPUT_DIRECTORY.rstrip("\n")
          
        OUTPUT_DIRECTORY_path_exist = os.path.isdir(OUTPUT_DIRECTORY)
        #if the path for output directory does not exist, a folder is created
        if OUTPUT_DIRECTORY_path_exist==False:
          os.mkdir(os.path.join(MLN_USR, OUTPUT_DIRECTORY))

        USERNAME = lines[2].split("=")[1]
        USERNAME = USERNAME.rstrip("\n")
       
        #a dict that is written in the .bin file in the system folder in the following way. For each config file, we have one hash_table where key is the layer name, and value is the object
        hash_table = {}
        hashtable_file_name_for_config_file = hash_table_file_name(
            USERNAME, config_file_first_portion[0],extension_layer_name.hash_table_file.value)
        #join hash table folder with hash table file to get the complete path
        hash_table_for_config = os.path.join(system_folder, hashtable_file_name_for_config_file)        
        total_no_of_layer_to_generated=0
        line_number_dict={}
                
        #contains the line number for each parameter to generate layer. This is mainly needed to show the user where the error occurs from the configuration file    
        for line in lines:
            # for intra-layer edge
            if line.startswith("BEGIN_LAYER"):
                buffer = []
               
            elif line.startswith("END_LAYER"):
                total_no_of_layer_to_generated=total_no_of_layer_to_generated+1
       
                #list that contains all the non null input attributes
                attribute_comb=[]

                #create an object of the class Parser
                ParserObject = Parser()
                
                # set INPUT_FILE_NAME
                ParserObject.set_INPUT_FILE_NAME(buffer,INPUT_DIRECTORY)
                # get INPUT_FILE_NAME
                INPUT_FILE_NAME = ParserObject.get_INPUT_FILE_NAME()
                if INPUT_FILE_NAME!="NULL":
                    attribute_comb.append("INPUT_FILE_NAME")
                
                layer_file_ext=extension_layer_name.layer_file.value
                #set LAYER_NAME
                ParserObject.set_LAYER_NAME(buffer,OUTPUT_DIRECTORY, USERNAME,configfilename,layer_file_ext)
                #get LAYER_NAME
                LAYER_NAME = ParserObject.get_LAYER_NAME()
              
                if LAYER_NAME!="NULL":
                    attribute_comb.append("LAYER_NAME")
                #set LAYER_GENERATION_TYPE
                ParserObject.set_LAYER_GENERATION_TYPE(buffer)
                #get LAYER_GENERATION_TYPE
                LAYER_GENERATION_TYPE = ParserObject.get_LAYER_GENERATION_TYPE()
                if LAYER_GENERATION_TYPE!="NULL":
                    attribute_comb.append("LAYER_GENERATION_TYPE")

                #set PRIMARY_KEY_COLUMN
                ParserObject.set_PRIMARY_KEY_COLUMN(buffer)
                #get PRIMARY_KEY_COLUMN
                PRIMARY_KEY_COLUMN = ParserObject.get_PRIMARY_KEY_COLUMN()

                if PRIMARY_KEY_COLUMN!="NULL":
                    attribute_comb.append("PRIMARY_KEY_COLUMN")
                
                base_layer_name=os.path.basename(LAYER_NAME)

                #the msg indicates that layer generation is initialized.
                log_file_object.msg_log_file(log_file,"Layer " +  base_layer_name + " Generation is Initiated.")
                #primary key converted filename for input file
                converter_primary_key_input_filename=primary_key_converted_input_file_name(USERNAME, config_file_first_portion[0],primary_key_converted_folder_for_input_file,INPUT_FILE_NAME, buffer)
                
                #set FEATURE_COLUMN
                ParserObject.set_FEATURE_COLUMN(buffer)     
                #get FEATURE_COLUMN              
                FEATURE_COLUMN = ParserObject.get_FEATURE_COLUMN()
                if FEATURE_COLUMN!="NULL":
                    attribute_comb.append("FEATURE_COLUMN")

                #set LONGITUDE_FEATURE_COLUMN
                ParserObject.set_LONGITUDE_FEATURE_COLUMN(buffer)     
                #get LONGITUDE_FEATURE_COLUMN         
                LONGITUDE_FEATURE_COLUMN = ParserObject.get_LONGITUDE_FEATURE_COLUMN(
                )
                if LONGITUDE_FEATURE_COLUMN!="NULL":
                    attribute_comb.append("LONGITUDE_FEATURE_COLUMN")
                
                #set LATITUDE_FEATURE_COLUMN
                ParserObject.set_LATITUDE_FEATURE_COLUMN(buffer)
                #get LATITUDE_FEATURE_COLUMN
                LATITUDE_FEATURE_COLUMN = ParserObject.get_LATITUDE_FEATURE_COLUMN(
                )
                if LATITUDE_FEATURE_COLUMN!="NULL":
                    attribute_comb.append("LATITUDE_FEATURE_COLUMN")
                
                #set FEATURE_TYPE
                ParserObject.set_FEATURE_TYPE(buffer)
                #get FEATURE_TYPE
                FEATURE_TYPE = ParserObject.get_FEATURE_TYPE()
                if FEATURE_TYPE!="NULL":
                    attribute_comb.append("FEATURE_TYPE")
                
                #set SIMILARITY_METRIC
                ParserObject.set_SIMILARITY_METRIC(buffer)
                #get SIMILARITY_METRIC
                SIMILARITY_METRIC = ParserObject.get_SIMILARITY_METRIC()
                if SIMILARITY_METRIC!="NULL":
                    attribute_comb.append("SIMILARITY_METRIC")
                
                #set THRESHOLD
                ParserObject.set_THRESHOLD(buffer)
                #get THRESHOLD
                THRESHOLD = ParserObject.get_THRESHOLD()
                if THRESHOLD!="NULL":
                    attribute_comb.append("THRESHOLD")
                    try:
                        THRESHOLD = float(THRESHOLD)
                    except:
                        log_file_object.msg_log_file(log_file,"Error in line number " + str(line_number_dict["THRESHOLD"])+".")
                        log_file_object.msg_log_file(log_file,"Failed")
                        log_file_object.ending_msg_log_file_fail(log_file)
                        buffer = [] 
                        del_file_tmp_dir(tmp_folder)
                        sys.exit() 
                            
                #set RANGE
                ParserObject.set_RANGE(buffer)
                #get RANGE
                RANGE = ParserObject.get_RANGE()
                if RANGE!="NULL":
                    attribute_comb.append("RANGE")
                
                #set MULTI_RANGE
                ParserObject.set_MULTI_RANGE(buffer)
                #get MULTI_RANGE
                MULTI_RANGE = ParserObject.get_MULTI_RANGE()
                if MULTI_RANGE!="NULL":
                    attribute_comb.append("MULTI_RANGE")
                
                #set NUMBER_OF_EQUI_SIZED_SEGMENTS
                ParserObject.set_NUMBER_OF_EQUI_SIZED_SEGMENTS(buffer)
                #get NUMBER_OF_EQUI_SIZED_SEGMENTS
                NUMBER_OF_EQUI_SIZED_SEGMENTS = ParserObject.get_NUMBER_OF_EQUI_SIZED_SEGMENTS(
                )
                if  NUMBER_OF_EQUI_SIZED_SEGMENTS !="NULL":
                    attribute_comb.append("NUMBER_OF_EQUI_SIZED_SEGMENTS")
                    try:
                        NUMBER_OF_EQUI_SIZED_SEGMENTS = float(NUMBER_OF_EQUI_SIZED_SEGMENTS)
                    except:
                        log_file_object.msg_log_file(log_file,"Error in line number " + str(line_number_dict["NUMBER_OF_EQUI_SIZED_SEGMENTS"])+".")
                        log_file_object.msg_log_file(log_file,"Failed")
                        log_file_object.ending_msg_log_file_fail(log_file)
                        buffer = []  
                        del_file_tmp_dir(tmp_folder)
                        sys.exit() 

                #set DATE_FORMAT
                ParserObject.set_DATE_FORMAT(buffer)
                #get DATE_FORMAT
                DATE_FORMAT = ParserObject.get_DATE_FORMAT()
                if DATE_FORMAT !="NULL":
                    attribute_comb.append("DATE_FORMAT")

                #set DATE_METRIC
                ParserObject.set_DATE_METRIC(buffer)
                #get DATE_METRIC
                DATE_METRIC = ParserObject.get_DATE_METRIC()
                if  DATE_METRIC!="NULL":
                    attribute_comb.append("DATE_METRIC")
                
                #set TIME_FORMAT
                ParserObject.set_TIME_FORMAT(buffer)
                #get TIME_FORMAT
                TIME_FORMAT = ParserObject.get_TIME_FORMAT()
                if TIME_FORMAT!="NULL":
                    attribute_comb.append("TIME_FORMAT")
                
                #input type value is the attribute combination for instance: INPUT_FILE_NAME_AND_LAYER_NAME_AND_LAYER_GENERATION_TYPE_AND_PRIMARY_KEY_COLUMN_AND_FEATURE_COLUMN_AND_FEATURE_TYPE_AND_SIMILARITY_METRIC
                input_type_value='_AND_'.join(attribute_comb)
               
                #check if the rule is present in the existing rule set
                input_type_exist=input_type_value in  InputType._member_names_

                if input_type_exist==True:
                    #input type number is the input number. For instance: 1
                    input_number=InputType[input_type_value].value
                    #call function to validate input type
                    input_valid=inputValidationObj.layer_specification_validation(INPUT_DIRECTORY,OUTPUT_DIRECTORY, input_type_value, input_number, ParserObject,line_number_dict,log_file_object,log_file)                 
                    #generate naming for the output layer
                    if input_valid==True:
                    #check if input type exist for system_generated_file. If the file is user generated, then the user can put any input attribute combination. But Layer_name and Layer_generation-type field is mandatory
                        if ParserObject.get_LAYER_GENERATION_TYPE()=="System_Generated": 
                                            #set PRIMARY_KEY_COLUMN
                                            ParserObject.set_primary_key_converter_for_input_file(INPUT_DIRECTORY,converter_primary_key_input_filename,INPUT_FILE_NAME,PRIMARY_KEY_COLUMN)
                                            #returns the name of the file that stores the file that stores the primary key(the first column) and the converted primary key(sec column) for an input file
                                            primary_key_converted_filename=ParserObject.get_primary_key_converter_for_input_file()
                                        
                                            input_file=os.path.join(INPUT_DIRECTORY,ParserObject.get_INPUT_FILE_NAME())
                                            #open input file for reading
                                            with open(input_file, mode='r',encoding="utf8") as data_file:
                                                    file_name_array=ParserObject.get_INPUT_FILE_NAME().split('.')
                                                    if(file_name_array[1]=="csv"):
                                                        csv_reader = csv.reader(data_file, delimiter=',')
                                                    next(csv_reader, None)
                                                    id_val=0
                                                    modified_csv_reader=[]
                                                    node_list=[]
                                                    #add node id value (1,2,3, ..) at the beginning of each row. The reason is the primary key id can be anything but we need integer node ids for community detection
                                                    for i in csv_reader:
                                                        id_val=id_val+1
                                                        i.insert(0, id_val)
                                                        node_list.append(id_val)                      
                                                        modified_csv_reader.append(i)
                                                    combi = list(combinations(list(modified_csv_reader), 2))
                                                    
                                            
                                            #if the layer is system genenerated, then create a unique layer name, else keep the original layer name provided by the user
                                            layer_file_ext=extension_layer_name.layer_file.value        
                                            layer_name = layer_file_name(USERNAME,
                                                                                config_file_first_portion[0],
                                                                                buffer,   layer_file_ext)
                                            
                                            #find the feature column no
                                            if ParserObject.get_FEATURE_COLUMN()!="NULL":
                                                feature_col_no=column_no_of_a_feature(INPUT_DIRECTORY, INPUT_FILE_NAME,FEATURE_COLUMN)
                                            else:
                                                feature_col_no=ParserObject.get_FEATURE_COLUMN()
                                            #find the lat col index if the value provided for lat col is not null
                                            if ParserObject.get_LATITUDE_FEATURE_COLUMN()!="NULL":
                                                lat_col=column_no_of_a_feature(INPUT_DIRECTORY, INPUT_FILE_NAME,ParserObject.get_LATITUDE_FEATURE_COLUMN())
                                            else:
                                                lat_col=ParserObject.get_LATITUDE_FEATURE_COLUMN()
                                            
                                            #find the lon col index if the value provided for lat col is not null
                                            if ParserObject.get_LONGITUDE_FEATURE_COLUMN()!="NULL":
                                                lon_col=column_no_of_a_feature(INPUT_DIRECTORY, INPUT_FILE_NAME,ParserObject.get_LONGITUDE_FEATURE_COLUMN())
                                            else:
                                                lon_col=ParserObject.get_LONGITUDE_FEATURE_COLUMN()
                
                                            
                                            #starting time
                                            start = time.time()
                                            edge_list=list(set(generate_layer_obj.generate_layer(INPUT_DIRECTORY, input_type_value, input_number, ParserObject, combi,similarityObj,node_column,feature_col_no,lat_col,lon_col,THRESHOLD, NUMBER_OF_EQUI_SIZED_SEGMENTS)))
                                                        
                                            # using naive method
                                            # to remove None values in list since the generated edgelist for layer files return some None values. The None values are returned for the edges which do not forms a connection between them based on the similarity metric or range information provided by the user
                                            non_none_edgelist = []
                                            for val in  edge_list:
                                                if val != None :
                                                    non_none_edgelist.append(val)
                                            edge_list= non_none_edgelist
                            
                                            end = time.time()
                                            layer_gen_time=round(end-start,2)
                                                
                                            #add node and edge info to parser object
                                            ParserObject.set_NODE_NUMBER(len(node_list))
                                            Node_Number = ParserObject.get_NODE_NUMBER()

                                            ParserObject.set_EDGE_NUMBER(len(edge_list))
                                            Edge_Number= ParserObject.get_EDGE_NUMBER()
                                                        
                                            #find connected com no in the layer                   
                                            G= nx.Graph()
                                            edge_list_con_com_val=edge_list_con_com(edge_list)
                                            G.add_edges_from(edge_list_con_com_val)
                                                        
                                            #python networkx is used to find the no. of connected component
                                            con_com_no=nx.number_connected_components(G)
                                                    
                                            #set connected component no
                                            ParserObject.set_CON_COM_NO(con_com_no)
                                                
                                            #write layer file info to output directory
                                            generate_layer_obj.write_layer_file(layer_name, OUTPUT_DIRECTORY,tmp_folder, node_list,edge_list,buffer,layer_file_ext)
                                            log_file_object.msg_log_file(log_file,"Done.")
                                            log_file_object.log_for_each_layer((MLN_USR_basename,log_file,layer_name,layer_gen_time,OUTPUT_DIRECTORY,Node_Number,Edge_Number,con_com_no))
                                            #log_for_each_layer_list.append()
                                            del combi
                                            del edge_list
                                            del line_number_dict
                                            del edge_list_con_com_val
                                            gc.collect()
                                                
                                            #create a hash table file and load the layer info in hash table(The hash table contains a dict where key is the layer name and value is the object that contains layer attributes)
                                            hash_table[layer_name] =pickle.dumps(ParserObject)

                                            #write the layer info in the hash table(pickle file in python written in the system directory)
                                            pickle.dump(hash_table, open(hash_table_for_config, "wb"))
                                                                                        #empty buffer
                                            buffer = []  
                                            line_number_dict={}    
                                            
                                                        
                        elif ParserObject.get_LAYER_GENERATION_TYPE()=="User_Generated":
                                                user_gene_layer_file = os.path.join(OUTPUT_DIRECTORY,ParserObject.get_LAYER_NAME())
                                                with open(user_gene_layer_file, mode='r') as user_layer_file: 
                                                        lines = user_layer_file.readlines()
                                                        node_no=lines[1].strip()
                                                        edge_no=lines[2].strip()

                                                con_com_no="NA"
                                                log_file_object.log_for_each_layer((MLN_USR_basename,log_file,ParserObject.get_LAYER_NAME(),"NA",OUTPUT_DIRECTORY,node_no,edge_no,con_com_no))
                                                buffer = [] 
                                                line_number_dict={} 
                                                del line_number_dict
                                                gc.collect() 
                                                    
                    else:
                        log_file_object.msg_log_file(log_file,"Failed")
                        log_file_object.ending_msg_log_file_fail(log_file)
                        buffer = [] 
                        del_file_tmp_dir(tmp_folder) 
                        sys.exit() 
                            
                else:
                    log_file_object.msg_log_file(log_file,"Inappropriate input attribute.")  
                    log_file_object.msg_log_file(log_file,"Failed")
                    log_file_object.ending_msg_log_file_fail(log_file)
                    buffer = []  
                    del_file_tmp_dir(tmp_folder)
                    sys.exit() 
            
            elif line.startswith("BEGIN_INTERLAYER"):
                    buffer = []

            elif line.startswith("END_INTERLAYER"):
                    ParserObject = Parser()
                    total_no_of_layer_to_generated=total_no_of_layer_to_generated+1
                 
                    #list that contains all the non null input attributes
                    attribute_comb_inter_layer=[]
              
                    #set INPUT_FILE_NAME
                    ParserObject.set_INPUT_FILE_NAME(buffer, INPUT_DIRECTORY)
                    #get INPUT_FILE_NAME
                    INPUT_FILE_NAME =  ParserObject.get_INPUT_FILE_NAME()
                    if INPUT_FILE_NAME!="NULL":
                        attribute_comb_inter_layer.append("INPUT_FILE_NAME")
                    
                    #set LAYER 1 NAME
                    ParserObject.set_LAYER_1_NAME(buffer)
                    #get LAYER 1 NAME
                    LAYER_1_NAME =  ParserObject.get_LAYER_1_NAME()
                    if LAYER_1_NAME!="NULL":
                        attribute_comb_inter_layer.append("LAYER_1_NAME")

                    #set LAYER_1_INPUT_FILE_NAME
                    ParserObject.set_LAYER_1_INPUT_FILE_NAME(buffer,INPUT_DIRECTORY)
                    #get LAYER_1_INPUT_FILE_NAME
                    LAYER_1_INPUT_FILE_NAME =  ParserObject.get_LAYER_1_INPUT_FILE_NAME()
                    if LAYER_1_INPUT_FILE_NAME!="NULL":
                        attribute_comb_inter_layer.append("LAYER_1_INPUT_FILE_NAME")

                    #set LAYER 2 NAME
                    ParserObject.set_LAYER_2_NAME(buffer)
                    #get LAYER 2 NAME
                    LAYER_2_NAME =  ParserObject.get_LAYER_2_NAME()
                    if LAYER_2_NAME!="NULL":
                        attribute_comb_inter_layer.append("LAYER_2_NAME")

                    #set LAYER_2_INPUT_FILE_NAME
                    ParserObject.set_LAYER_2_INPUT_FILE_NAME(buffer,INPUT_DIRECTORY)
                    #get LAYER_2_INPUT_FILE_NAME
                    LAYER_2_INPUT_FILE_NAME =  ParserObject.get_LAYER_2_INPUT_FILE_NAME()
                    if LAYER_2_INPUT_FILE_NAME!="NULL":
                        attribute_comb_inter_layer.append("LAYER_2_INPUT_FILE_NAME")
                    
                    inter_layer_file_ext=extension_layer_name.inter_layer_file.value
                    # set INTER_LAYER_NAME
                    ParserObject.set_INTER_LAYER_NAME(buffer,OUTPUT_DIRECTORY, USERNAME,configfilename, inter_layer_file_ext)
                    #get INTER_LAYER_NAME
                    INTER_LAYER_NAME =  ParserObject.get_INTER_LAYER_NAME()
                    if INTER_LAYER_NAME!="NULL":
                        attribute_comb_inter_layer.append("INTER_LAYER_NAME")
                    
                    base_layer_name=os.path.basename(INTER_LAYER_NAME)
                    #the msg indicates that layer generation is initialized.
                    log_file_object.msg_log_file(log_file,"Layer " +  base_layer_name + " Generation is Initiated.")
                    #set INTER_LAYER_GENERATION_TYPE
                    ParserObject.set_INTER_LAYER_GENERATION_TYPE(buffer)
                    #get LAYER_GENERATION_TYPE
                    LAYER_GENERATION_TYPE =  ParserObject.get_INTER_LAYER_GENERATION_TYPE()
                    if LAYER_GENERATION_TYPE!="NULL":
                        attribute_comb_inter_layer.append("LAYER_GENERATION_TYPE")

                    #input type value is the attribute combination for instance: INPUT_FILE_NAME_AND_LAYER_NAME_AND_LAYER_GENERATION_TYPE_AND_PRIMARY_KEY_COLUMN_AND_FEATURE_COLUMN_AND_FEATURE_TYPE_AND_SIMILARITY_METRIC
                    input_type_value='_AND_'.join(attribute_comb_inter_layer)
                
                    #check if the input type is valid or not
                    #check if the rule is present in the existing rule set
                    input_type_exist=input_type_value in  InputType._member_names_
                    #check if input type exist for system_generated_file. If the file is user generated, then the user can put any input attribute combination. But Layer_name and Layer_generation-type field is mandatory
                    if input_type_exist==True:
                            #input type number is the input number. For instance: 1
                            input_number=InputType[input_type_value].value
                            #primary key converted filename for two files from which inter-layer file is generated
                            Layer_1_primary_key_converted_file=primary_key_converted_input_file_name_for_inter_layer_generation(USERNAME, config_file_first_portion[0],primary_key_converted_folder_for_input_file,LAYER_1_INPUT_FILE_NAME,buffer,"LAYER_1_NAME")
                            Layer_2_primary_key_converted_file=primary_key_converted_input_file_name_for_inter_layer_generation(USERNAME,config_file_first_portion[0],primary_key_converted_folder_for_input_file,LAYER_2_INPUT_FILE_NAME,buffer,"LAYER_2_NAME")


                            first_converted_file={}
                            sec_converted_file={}

                            #convert the first primary key converted file into a dict
                            with open(Layer_1_primary_key_converted_file, mode='r') as user_layer_file: 
                                csv_reader = csv.reader(user_layer_file)
                                header=next(csv_reader)
                                for rows in user_layer_file:  
                                    rows = rows.rstrip("\n")
                                    rows=rows.split(",")
                                    first_converted_file[rows[1]]=rows[0]
                            
                            #convert the sec primary key converted file into a dict
                            with open(Layer_2_primary_key_converted_file, mode='r') as user_layer_file: 
                                csv_reader = csv.reader(user_layer_file)
                                header=next(csv_reader)
                                for rows in user_layer_file:
                                    rows = rows.rstrip("\n")
                                    rows=rows.split(",")
                                    sec_converted_file[rows[1]]=rows[0]

                            #call function to validate input type
                            input_valid=inputValidationObj.inter_layer_specification_validation(INPUT_DIRECTORY,OUTPUT_DIRECTORY,primary_key_converted_folder_for_input_file, Layer_1_primary_key_converted_file,Layer_2_primary_key_converted_file,input_type_value, input_number,  ParserObject,line_number_dict,log_file_object,log_file)

                            #generate naming for the output layer
                            if input_valid==True:
                                    input_file=os.path.join(INPUT_DIRECTORY, ParserObject.get_INPUT_FILE_NAME())
                                    all_entry_of_inter_layer=[]
                                   
                                    #reading the input file for inter-layer
                                    with open(input_file, mode='r', encoding="UTF-8") as input_file:
                                            csvreader = csv.reader(input_file)
                                            header = next(csvreader)
                                            INPUT_FILE_1_PRIMARY_KEY_COLUMN=header[0]
                                            INPUT_FILE_2_PRIMARY_KEY_COLUMN=header[1]

                                            #convert the row values to ids
                                            for rows in csvreader:
                                                ind_entry_of_inter_layer=[]
                                                first_id=first_converted_file[rows[0]]
                                                sec_id=sec_converted_file[rows[1]]
                                                relation=rows[2]
                                                ind_entry_of_inter_layer.append(first_id)
                                                ind_entry_of_inter_layer.append(sec_id)
                                                ind_entry_of_inter_layer.append(relation)

                                                all_entry_of_inter_layer.append(ind_entry_of_inter_layer)

                                            input_file.close()
                                                    
                                    layer_name = layer_file_name(USERNAME,
                                                                       config_file_first_portion[0],
                                                                       buffer, inter_layer_file_ext)
                                    
                                    line_count=len(all_entry_of_inter_layer)
                                    
                                    inter_layer_nodelist_1st_file=[]
                                    inter_layer_nodelist_2nd_file=[]
                                    
                                    #total no of nodes (nodes in the 1st and 2nd csv file)
                                    node_list_size=len(first_converted_file)+len(sec_converted_file)

                                    #add the nodes in the first layer file for inter-layer generation to list
                                    for keys in first_converted_file:
                                        inter_layer_nodelist_1st_file.append(first_converted_file[keys])

                                    #add the nodes in the sec layer file for inter-layer generation to list
                                    for keys in sec_converted_file:
                                        inter_layer_nodelist_2nd_file.append(sec_converted_file[keys])
                                  
                                    if  ParserObject.get_INTER_LAYER_GENERATION_TYPE()==GeneratedLayerType.System_Generated.value:
                                                # starting time
                                                start = time.time()
                                                #create layer
                                                edge_list=all_entry_of_inter_layer                            
                                                #end time
                                                end = time.time()
                                                layer_gen_time=round(end-start,2)
                                                
                                                #add node and edge info to parserobject 
                                                ParserObject.set_NODE_NUMBER(node_list_size)
                                                Node_Number = ParserObject.get_NODE_NUMBER()

                                                ParserObject.set_EDGE_NUMBER(len(edge_list))
                                                #get DATE_FORMAT
                                                Edge_Number= ParserObject.get_EDGE_NUMBER()

                                                con_com_no="NA"
                                                                                                
                                                ParserObject.set_CON_COM_NO("NA")
                                                generate_layer_obj.write_inter_layer_file(layer_name,OUTPUT_DIRECTORY,tmp_folder, line_count, inter_layer_nodelist_1st_file,inter_layer_nodelist_2nd_file,INPUT_FILE_1_PRIMARY_KEY_COLUMN,INPUT_FILE_2_PRIMARY_KEY_COLUMN,edge_list,buffer,relation, inter_layer_file_ext)
                                                log_file_object.msg_log_file(log_file,"Done.")
                                                log_file_object.log_for_each_layer((MLN_USR_basename,log_file,layer_name,layer_gen_time,OUTPUT_DIRECTORY,Node_Number,Edge_Number,con_com_no))

                                            
                                                #create a hash table(a dictionary) and load the layer info in the hash table(The hash table contains a dict where key is the layer name and value is the object that contains layer attributes)
                                                hash_table[layer_name] =pickle.dumps(ParserObject)
                                                #write the layer info in the hash table(pickle file in python written in the system directory)
                                                pickle.dump(hash_table, open(hash_table_for_config, "wb"))

                                                buffer=[]
                                                line_number_dict={}
                                    
                                    elif ParserObject.get_INTER_LAYER_GENERATION_TYPE()=="User_Generated":
                                        user_gene_layer_file = os.path.join(OUTPUT_DIRECTORY,ParserObject.get_LAYER_NAME())
                                        with open(user_gene_layer_file, mode='r') as user_layer_file: 
                                                lines = user_layer_file.readlines()
                                                node_no="NA" 
                                                edge_no=len(lines)-1   
                                                con_com_no="NA"                   
                                            
                                        log_file_object.msg_log_file(log_file,"Done.")
                                        log_file_object.log_for_each_layer((MLN_USR_basename,log_file,ParserObject.get_LAYER_NAME(),"NA",OUTPUT_DIRECTORY,node_no,edge_no,con_com_no))
                                        buffer=[]
                                        line_number_dict={}
                            else:
                                log_file_object.msg_log_file(log_file,"Failed")
                                log_file_object.ending_msg_log_file_fail(log_file)
                                buffer = []  
                                del_file_tmp_dir(tmp_folder)
                                sys.exit()              
        
                            
                    else:                              
                                log_file_object.msg_log_file(log_file,"Inappropriate input attribute.")  
                                log_file_object.msg_log_file(log_file,"Failed")
                                log_file_object.ending_msg_log_file_fail(log_file)
                                buffer = [] 
                                del_file_tmp_dir(tmp_folder) 
                                sys.exit()              
        
            else:
                #store line number of layer parameters in a dict(line_number_dict) and lines in a list(buffer)
                line_index=lines.index(line)
                line = line.rstrip("\n")
                line_content=line.split("=")
                if line_content[0]=="INPUT_FILE_NAME" or line_content[0]=="LAYER_NAME" or line_content[0]=="LAYER_GENERATION_TYPE" or line_content[0]=="PRIMARY_KEY_COLUMN" or line_content[0]=="FEATURE_COLUMN" or line_content[0]=="FEATURE_TYPE" or line_content[0]=="SIMILARITY_METRIC" or line_content[0]=="THRESHOLD" or line_content[0]=="RANGE" or line_content[0]=="MULTI_RANGE" or line_content[0]=="NUMBER_OF_EQUI_SIZED_SEGMENTS" or line_content[0]=="LONGITUDE_FEATURE_COLUMN" or line_content[0]=="LATITUDE_FEATURE_COLUMN" or line_content[0]=="DATE_METRIC" or line_content[0]=="DATE_FORMAT" or line_content[0]=="TIME_FORMAT" or line_content[0]=="LAYER_1_NAME" or line_content[0]=="LAYER_1_INPUT_FILE_NAME" or line_content[0]=="LAYER_2_NAME" or line_content[0]=="LAYER_2_INPUT_FILE_NAME" or line_content[0]=="INTER_LAYER_NAME" or line_content[0]=="INTER_LAYER_GENERATION_TYPE":
                    line_number_dict[line_content[0]]=line_index+1
                    buffer.append(line)

    #check if the all the layers are correctly generated in the tmp file. If yes, then move all the files in the output directory and delete from tmp folder. Otherwise just delete all files from tmp durectory 
    list_of_files_in_tmp = os.listdir(tmp_folder) # dir is your directory path
    number_files_in_temp = len(list_of_files_in_tmp)
    file_names = os.listdir(tmp_folder)

    #check if all the layers are generated without any error
    if number_files_in_temp==total_no_of_layer_to_generated:  
        #move files from tmp to output directory
        for file_name in file_names:
            # Specify path
            file_exist_in_output_directory = os.path.join(OUTPUT_DIRECTORY, file_name)
            isExist = os.path.exists(file_exist_in_output_directory )
            if isExist==False:
                shutil.move(os.path.join(tmp_folder, file_name), OUTPUT_DIRECTORY)

            else:
                #if the file with the same name already exists in the directory then the file is removed from the output directory first, then the newly generated file with thesame name is moved from the temp to output directory
                os.unlink(file_exist_in_output_directory)
                shutil.move(os.path.join(tmp_folder, file_name), OUTPUT_DIRECTORY)
                # print("Layer " + file_name + " is Already Present in the " + OUTPUT_DIRECTORY  + ". The Newly Generated Layer" +  file_name )
       
        log_file_object.ending_msg_log_file_success(log_file)

    else:
         log_file_object.ending_msg_log_file_fail(log_file)

    
    del_file_tmp_dir(tmp_folder)
