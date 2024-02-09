from itertools import combinations
from similarityMetric import *
import csv
from collections import defaultdict
import os
from multiprocessing import Pool
from constants import *

class LAYER_GENERATION:
    def __init__(self):
        #print("Layer generation initialized")
        pass

    def NONE(self):
            pass
        #print("Invalid input")

    def generate_layer(self,INPUT_DIRECTORY, input_type_value, input_number, ParserObject, combi,similarityObj,node_column,feature_col_no,lat_col,lon_col,THRESHOLD, NUMBER_OF_EQUI_SIZED_SEGMENTS):      
        if input_number==1:
            feature_col_no=feature_col_no+1
            edgeList=[]
            combi_pair=[]
        
            for i in combi:
                    str_val=str(i[0][0]) + "," + str(i[1][0])
                    combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], str_val))
            with Pool(os.cpu_count()) as p:
                edgeList=p.map(similarityObj.nominal_metric,  combi_pair)


        elif input_number==2:
                    feature_col_no=feature_col_no+1
                    similarity_metric=ParserObject.get_SIMILARITY_METRIC()
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], THRESHOLD,str_val))

                    if similarity_metric=="JACCARD":
                            with Pool(os.cpu_count()) as p:
                                edgeList=p.map(similarityObj.num_metric_jaccard_similarity,  combi_pair)
                  
                    

                    elif similarity_metric=="EUCLIDEAN":
                            with Pool(os.cpu_count()) as p:
                                edgeList=p.map(similarityObj.num_metric_euclidean,  combi_pair)
                
                           
                    elif similarity_metric=="COSINE":        
                            with Pool(os.cpu_count()) as p:
                                edgeList=p.map(similarityObj.cosine_similarity_value,  combi_pair)
           
        elif input_number==3:
                    feature_col_no=feature_col_no+1
                    similarity_metric=ParserObject.get_SIMILARITY_METRIC()
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_RANGE(),str_val))
                    with Pool(os.cpu_count()) as p:
                                    edgeList=p.map(similarityObj.numeric_metric_range,  combi_pair)
            

        elif input_number==4:
                    feature_col_no=feature_col_no+1
                    similarity_metric=ParserObject.get_SIMILARITY_METRIC()
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_RANGE(),NUMBER_OF_EQUI_SIZED_SEGMENTS,str_val))
                    with Pool(os.cpu_count()) as p:
                                    edgeList=p.map(similarityObj.numeric_metric_range_with_segments,  combi_pair)
           

        elif input_number==5:
                    feature_col_no=feature_col_no+1
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_MULTI_RANGE(),str_val))
                    with Pool(os.cpu_count()) as p:
                                    edgeList=p.map(similarityObj.numeric_metric_multi_range,  combi_pair)
          
        
        elif input_number==6:
           
                    similarity_metric=ParserObject.get_SIMILARITY_METRIC()
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][lon_col],i[0][lat_col],i[1][lon_col],i[1][lat_col],DistanceUnit.KILOMETERS.value,THRESHOLD,str_val))
                    with Pool(os.cpu_count()) as p:
                                    edgeList=p.map(similarityObj.distance_cal_for_location_haversine,  combi_pair)
            

        elif input_number==7:
                    feature_col_no=feature_col_no+1
                    similarity_metric=ParserObject.get_SIMILARITY_METRIC()
                    edgeList=[]
                    combi_pair=[]
                    for i in combi:
                                str_val=str(i[0][0]) + "," + str(i[1][0])
                                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no],ParserObject.get_DATE_FORMAT(),ParserObject.get_DATE_METRIC(),str_val))
                    with Pool(os.cpu_count()) as p:
                                    edgeList=p.map(similarityObj.numeric_metric_date_equality,  combi_pair)
         
       
        elif input_number==8:
            feature_col_no=feature_col_no+1
            edgeList=[]
            combi_pair=[]
            for i in combi:
                str_val=str(i[0][0]) + "," + str(i[1][0])
                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no],ParserObject.get_DATE_FORMAT(),ParserObject.get_DATE_METRIC(), THRESHOLD,str_val))
               

            with Pool(os.cpu_count()) as p:
                edgeList=p.map(similarityObj.numeric_metric_date_euc,  combi_pair)


        elif input_number==9:
            feature_col_no=feature_col_no+1
            edgeList=[]
            combi_pair=[]
            for i in combi:
                str_val=str(i[0][0]) + "," + str(i[1][0])
                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(),THRESHOLD,str_val))

            with Pool(os.cpu_count()) as p:
                edgeList=p.map(similarityObj.numeric_metric_time_euc,  combi_pair)

        elif input_number==10:
            feature_col_no=feature_col_no+1
            similarity_metric=ParserObject.get_SIMILARITY_METRIC()
            edgeList=[]
            combi_pair=[]
            for i in combi:
                str_val=str(i[0][0]) + "," + str(i[1][0])
                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(),ParserObject.get_RANGE(),str_val))
              
            with Pool(os.cpu_count()) as p:
                edgeList=p.map(similarityObj.numeric_metric_time_range,  combi_pair)


        elif input_number==11:
            feature_col_no=feature_col_no+1
            similarity_metric=ParserObject.get_SIMILARITY_METRIC()
            edgeList=[]
            combi_pair=[]
            for i in combi:
                str_val=str(i[0][0]) + "," + str(i[1][0])
                combi_pair.append((i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(), ParserObject.get_MULTI_RANGE(),str_val))
            with Pool(os.cpu_count()) as p:
                edgeList=p.map(similarityObj.numeric_metric_time_multirange,  combi_pair)

    
        return edgeList
    
    def write_layer_file(self, layer_name_full,OUTPUT_DIRECTORY,tmp_folder,node_list,edge_list,buffer,layer_file_ext):
        for ele in buffer:
               val=ele.split("=")
               if val[0]=="LAYER_NAME":
                      layer_file_name=val[1]
                      break
        layer_file_name=layer_file_name+layer_file_ext
        file_name=os.path.join(tmp_folder,layer_name_full)
        with open(file_name, mode='w+') as layer_file:
            layer_name=layer_file_name.split(".")
            layer_file.write(layer_name[0] + '\n')
            layer_file.write(str(len(node_list)))
            layer_file.write('\n')
            layer_file.write(str(len(edge_list)))
            layer_file.write('\n')
            for i in node_list:
                layer_file.write(str(i) + "\n")
            for i in list(edge_list):
                layer_file.write(str(i))
                layer_file.write(',1.0000 \n')

    def write_inter_layer_file(self, layer_name_full,OUTPUT_DIRECTORY, tmp_folder,line_count,inter_layer_nodelist_1st_file,inter_layer_nodelist_2nd_file,INPUT_FILE_1_PRIMARY_KEY_COLUMN,INPUT_FILE_2_PRIMARY_KEY_COLUMN, edge_list,buffer,relation,layer_file_ext):
            for ele in buffer:
               val=ele.split("=")
               if val[0]=="INTER_LAYER_NAME":
                      layer_file_name=val[1]
                      break
            layer_file_name=layer_file_name+layer_file_ext
            file_name=os.path.join(tmp_folder,layer_name_full)
            with open(file_name, mode='w+') as layer_file:
                layer_name=layer_file_name.split(".")
                layer_file.write(layer_name[0] + '\n')
                strrel=","+relation+ "\n"
                for i in edge_list:
                    layer_file.write(str(i[0]))
                    layer_file.write(',')
                    layer_file.write(str(i[1]))
                    layer_file.write(strrel)
