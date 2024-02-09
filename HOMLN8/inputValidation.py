from enum import Enum 
import os 
import pandas as pd
from constants import *
from log_file_generation import *
import colorama
from colorama import Fore

def check_if_string(input):
    if type(input) == str:
        return True
    else:
        return False

def check_if_int(int_input):
    if isinstance(int_input, int):
        return True
    else:
        return False

def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

#function to check if a column exists in the csv file
def column_in_csv_exist(filename, cloumn_name,INPUT_DIRECTORY):
    filename=os.path.join(INPUT_DIRECTORY,filename)
    column_exists=False
    # reading csv file
    df=pd.read_csv(filename)
    if cloumn_name in df:
        column_exists=True
        return column_exists
    return column_exists

#function to check if the input file exists in the directory
def file_exists(path, filename):
    filename=os.path.join(path,filename)
    exist=os.path.exists(filename)
    return exist

class InputValidationObj:
    def __init__(self):
       #print("input validation initialized")
       pass

    def NONE(self):
        print("Invalid input.")
    
    def convert_input_value_to_comma_separated_format(self,input_type_value,layer_input):
        if input_type_value==1:
            #this contains the user input in the comma separated format
            comma_sep_input=layer_input.INPUT_FILE_NAME + "," + layer_input.LAYER_NAME + "," + layer_input.LAYER_GENERATION_TYPE + ","+ layer_input.PRIMARY_KEY_COLUMN + "," +layer_input.FEATURE_COLUMN + "," + layer_input.FEATURE_TYPE + "," + layer_input.SIMILARITY_METRIC        
        return comma_sep_input 

    def layer_specification_validation(self, INPUT_DIRECTORY, OUTPUT_DIRECTORY,input_type_value, input_number, ParserObject,line_number_dict,log_file_object,log_file_name):
        if ParserObject.get_LAYER_GENERATION_TYPE()==GeneratedLayerType.System_Generated.value:     
            base_inputfile_name=os.path.basename(ParserObject.get_INPUT_FILE_NAME())       
            input_file_exist=file_exists(INPUT_DIRECTORY, ParserObject.get_INPUT_FILE_NAME())
            if input_file_exist==True:
                primary_key_column_exist=True
                primary_key_column=ParserObject.get_PRIMARY_KEY_COLUMN().split(",")            
                for keys in primary_key_column:
                    primary_key_column_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), keys,INPUT_DIRECTORY)
                    if primary_key_column_exist==False:
                        break
                if primary_key_column_exist==True:
                    #validation for input number 1
                    if input_number==1:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if ParserObject.get_SIMILARITY_METRIC()==Metric.EQUALITY.value:
                                    input_valid=True
                                    
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+ ".")  
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".") 
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False                 
               
                    #validation for input number 2
                    elif input_number==2:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if ParserObject.get_SIMILARITY_METRIC()==Metric.EUCLIDEAN.value or ParserObject.get_SIMILARITY_METRIC()==Metric.JACCARD.value or ParserObject.get_SIMILARITY_METRIC()==Metric.COSINE.value:
                                    if is_float(ParserObject.get_THRESHOLD())==True:
                                        input_valid=True
                                        
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["THRESHOLD"])+".")   
                                        input_valid=False       
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+".")   
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False                 

                 #validation for input number 3
                    elif input_number==3:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if check_if_string(ParserObject.get_RANGE())==True:        
                                        input_valid=True
                                        
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["RANGE"])+".")   
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False   

                    #validation for input number 4
                    elif input_number==4:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if check_if_string(ParserObject.get_RANGE())==True:   
                                    if is_float(ParserObject.get_NUMBER_OF_EQUI_SIZED_SEGMENTS())==True:  
                                            input_valid=True
                                           
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["NUMBER_OF_EQUI_SIZED_SEGMENTS"])+".")   
                                        input_valid=False             
      
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["RANGE"])+".")   
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False   

                    #validation for input number 5
                    elif input_number==5:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if check_if_string(ParserObject.get_MULTI_RANGE())==True:   
                                    input_valid=True
                                                                          
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["MULTI_RANGE"])+".")   
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False               


                    #validation for input number 6
                    elif input_number==6:
                        Lat_FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_LATITUDE_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        Long_FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_LONGITUDE_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if Lat_FEATURE_COLUMN_exist==True: 
                            if Long_FEATURE_COLUMN_exist==True:
                                feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                                if feature_type_valid==True:                                                            
                                    if ParserObject.get_SIMILARITY_METRIC()==Metric.HAVERSINE.value:   
                                        if is_float(ParserObject.get_THRESHOLD())==True:
                                            input_valid=True
                                        
                                        else:
                                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["THRESHOLD"])+".")   
                                            input_valid=False                                           
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+".")   
                                        input_valid=False               
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                    input_valid=False 
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["LONGITUDE_FEATURE_COLUMN"])+".")     
                                input_valid=False               
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["LATITUDE_FEATURE_COLUMN"])+".")     
                            input_valid=False                   
                    
                    
                    #validation for input number 7
                    elif input_number==7:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:    
                                if ParserObject.get_DATE_FORMAT()=="dd-mm-yyyy" or ParserObject.get_DATE_FORMAT()=="mm-dd-yyyy":
                                    date_metric_valid=ParserObject.get_DATE_METRIC() in DateEnum._member_names_
                                    if date_metric_valid==True:
                                        
                                        if ParserObject.get_SIMILARITY_METRIC()==Metric.EQUALITY.value:
                                            input_valid=True
                                            
                                        else:
                                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+".")   
                                            input_valid=False      
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["DATE_METRIC"])+".")   
                                        input_valid=False       
                                    
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["DATE_FORMAT"])+".")   
                                    input_valid=False                                                               
                                   
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False                 
                      
                                        
                    #validation for input number 8
                    elif input_number==8:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                    
                            if feature_type_valid==True:    
                                if ParserObject.get_DATE_FORMAT()=="dd-mm-yyyy" or ParserObject.get_DATE_FORMAT()=="mm-dd-yyyy":
                                    date_metric_valid=ParserObject.get_DATE_METRIC() in DateEnum._member_names_
                                    if date_metric_valid==True:
                                       
                                        if ParserObject.get_SIMILARITY_METRIC()==Metric.EUCLIDEAN.value:
                                            if is_float(ParserObject.get_THRESHOLD())==True:
                                                input_valid=True
                                                
                                            else:
                                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["THRESHOLD"])+".")
                                                input_valid=False  

                                        else:
                                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+".")   
                                            input_valid=False               
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["DATE_METRIC"])+".")   
                                        input_valid=False       
                                    
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["DATE_FORMAT"])+".")   
                                    input_valid=False                                                               
                                   
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False   


                    #validation for input number 9
                    elif input_number==9:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:    
                                if ParserObject.get_TIME_FORMAT()=="hh:mm":
                                     
                                        if ParserObject.get_SIMILARITY_METRIC()==Metric.EUCLIDEAN.value:
                                            if is_float(ParserObject.get_THRESHOLD())==True:
                                                input_valid=True
                                                
                                            else:
                                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["THRESHOLD"])+".")
                                                input_valid=False  
                                        else:
                                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["SIMILARITY_METRIC"])+".")   
                                                input_valid=False               
                                    
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["TIME_FORMAT"])+".")   
                                    input_valid=False                                                               
                                   
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False   


                    #validation for input number 10
                    elif input_number==10:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if check_if_string(ParserObject.get_RANGE())==True: 
                                    if ParserObject.get_TIME_FORMAT()=="hh:mm":   
                                             
                                            input_valid=True
                                            
                                    else:
                                        log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["TIME_FORMAT"])+".")   
                                        input_valid=False               
                                else:
                                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["RANGE"])+".")   
                                    input_valid=False               
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False             
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False   


                    #validation for input number 11
                    elif input_number==11:
                        FEATURE_COLUMN_exist=column_in_csv_exist(ParserObject.get_INPUT_FILE_NAME(), ParserObject.get_FEATURE_COLUMN(),INPUT_DIRECTORY)
                        if FEATURE_COLUMN_exist==True:
                            feature_type_valid=ParserObject.get_FEATURE_TYPE() in FeatureType._member_names_
                            if feature_type_valid==True:                                                            
                                if check_if_string(ParserObject.get_MULTI_RANGE())==True:  
                                    if feature_type_valid==True:                                                            
                                        if ParserObject.get_TIME_FORMAT()=="hh:mm":   
                                             input_valid=True
                                        else:
                                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["TIME_FORMAT"])+".")   
                                            input_valid=False                       
                            else:
                                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_TYPE"])+".")  
                                input_valid=False              
                                    
                        else:
                            log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["FEATURE_COLUMN"])+".")     
                            input_valid=False                    
                        
                else:
                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["PRIMARY_KEY_COLUMN"])+".")
                    input_valid=False
            else:
                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["INPUT_FILE_NAME"])+".")
                input_valid=False
              
        #for user generated layer file, no need for validation, just put the layer information in the hash table
        elif ParserObject.get_LAYER_GENERATION_TYPE()==GeneratedLayerType.User_Generated.value:  
                user_generated_file_exist=file_exists(OUTPUT_DIRECTORY, ParserObject.get_LAYER_NAME())
                if user_generated_file_exist==True:
                    input_valid=True
                else:
                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["INPUT_FILE_NAME"])+".")
                    input_valid=False 

        else:
                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["LAYER_GENERATION_TYPE"])+".")
                input_valid=False
        
        return input_valid 

    #inter-layer file mapping validation
    def inter_layer_specification_validation(self, INPUT_DIRECTORY, OUTPUT_DIRECTORY,primary_key_converted_folder_for_input_file,Layer_1_primary_key_converted_file,Layer_2_primary_key_converted_file,input_type_value, input_number, ParserObject,line_number_dict,log_file_object,log_file_name):
        if ParserObject.get_INTER_LAYER_GENERATION_TYPE()==GeneratedLayerType.System_Generated.value:            
            LAYER_1_NAME_exist=file_exists(primary_key_converted_folder_for_input_file, Layer_1_primary_key_converted_file)
            LAYER_2_NAME_exist=file_exists(primary_key_converted_folder_for_input_file, Layer_2_primary_key_converted_file)
            if LAYER_1_NAME_exist==True and LAYER_2_NAME_exist==True:
                INPUT_FILE_NAME=True
                INPUT_FILE_NAME=ParserObject.get_INPUT_FILE_NAME().split(",")  
                INPUT_FILE_NAME_exist=file_exists(INPUT_DIRECTORY, ParserObject.get_INPUT_FILE_NAME())
                if INPUT_FILE_NAME_exist==True:
                    input_valid=True
                
                else:
                    input_valid=False
                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["INPUT_FILE_NAME"])+".")

            else:
                input_valid=False
                log_file_object.msg_log_file(log_file_name,"Primary key converted file is missing.")
             
        #for user generated layer file, no need for validation, just put the layer information in the hash table
        elif ParserObject.get_LAYER_GENERATION_TYPE()==GeneratedLayerType.User_Generated.value:  
                user_generated_file_exist=file_exists(OUTPUT_DIRECTORY, ParserObject.get_LAYER_NAME())
                if user_generated_file_exist==True:
                    input_valid=True
                else:
                    log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["INPUT_FILE_NAME"])+".")
                    input_valid=False
        
        else:
                log_file_object.msg_log_file(log_file_name,"Error in line number " + str(line_number_dict["INTER_LAYER_GENERATION_TYPE"])+".")
                input_valid=False
 
        return input_valid 
