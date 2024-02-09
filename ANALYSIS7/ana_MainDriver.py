import os
from os import path
import pickle
import shutil
import pandas as pd
# CUSTOM IMPORTS
from ana_Community_Detection_Algorithms import *
from ana_FileProcessing import *
from ana_constants import *
from ana_log_file_generation import *
from ana_parser_class import *
import time

"""
    Creates the name for the Hash table.
    
    :param username: The username of the user.
    :param ana_configfilename: The name of the configuration file.
    :param ext: The extension of the Hash table.
    :return: The name of the Hash table.
"""
def ana_hash_table_file_name(username, ana_configfilename,ext):
    if username == '' or username == None:
        config_file = ana_configfilename + ext
    else:
        config_file = username + '_' + ana_configfilename + ext
    return config_file


"""
    Creates the name for the log file.

    :param username: The username of the user.
    :param ana_configfilename: The name of the configuration file.
    :param config_file_ext: The extension of the configuration file.
    :param log_file_ext: The extension of the log file.
    :return: The name of the log file.
"""
def ana_log_file_naming(username, ana_configfilename, config_file_ext, log_file_ext):
    # if username == '' or username == None:
    log_file = ana_configfilename + config_file_ext + log_file_ext
    # else:
    #     log_file = username + '_' + ana_configfilename + config_file_ext + log_file_ext
    return log_file


"""
    Deletes all files from the tmp directory.

    :param tmp_folder: The path to the tmp directory.
    :return: None
"""
def ana_del_file_tmp_dir(tmp_folder):
    # delete files from the tmp directory
    for filename in os.listdir(tmp_folder):
        file_path = os.path.join(tmp_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            pass


"""
    Gets the path to the input graph file from the dictionary.

    :param path_to_pickle_dict: The path to the dictionary.
    :param matching_key: The key to match.
"""
def ana_get_INPUT_layer_path(path_to_pickle_dict, matching_key):
    # reading the pickle file
    loaded_pickel_hash_table = pickle.load(open(path_to_pickle_dict, "rb"))
    # looping through the pickle file
    for key, value in loaded_pickel_hash_table.items():
        # key is the layer name and value is the binary object. 
        # To convert the binary object to actual one, we need to load the value using pickle 
        keytype = key.split(".")
        # read the intralayer keys in the following way
        if keytype[1] == "net":
            if matching_key in key:
                print("--------------------------------")
                print("KEY: ", key)
                path_to_layer_file = pickle.loads(value)._LAYER_NAME
                print("PATH TO LAYER FILE: ", path_to_layer_file)
                print("--------------------------------")
                return path_to_layer_file
    # if caught in the loop, then the layer is found else no PATH found
    return None

"""
    Detects communities in the input graph using the specified community detection algorithm.

    :param community_type_algo: The community detection algorithm to use.
    :param INPUT_layer_path_from_dict: The path to the input graph file.
    :param output_directory: The directory to write the output files to.
    :param analysis_name: The name of the analysis.
    :param ana_log_file_object: The log file object.
    :param log_file: The path to the log file.
    :return: The number of nodes, edges, and communities in the input graph.
"""
def community_detection(COMMUNITY_TYPE_ALGO, INPUT_layer_path_from_dict, outputDirectory, analysisNAME, ana_log_file_object, log_file, userName_from_ana_config_file, gen_configFile_name):

    numNodes = 0
    numEdges = 0
    numCommunities = 0

    validAlgorithms = ["louvain", "infomap", "walktrap", "fastgreedy", "leadingeigenvector", "multilevel"]
    if COMMUNITY_TYPE_ALGO.lower() not in validAlgorithms:
        raise ValueError(f"Incorrect algorithm mentioned: {COMMUNITY_TYPE_ALGO}. Valid options are: {', '.join(validAlgorithms)}")

    try:
        # the msg indicates that analysis is initialized.
        ana_log_file_object.ana_msg_log_file(log_file,"Analysis on layer " +  analysisNAME + " is Initiated.")

        if COMMUNITY_TYPE_ALGO.lower() == "louvain":
            # Read and process input file to create Graph
            Graph, edges = create_nx_Graph(INPUT_layer_path_from_dict)

            # Louvain function
            result, time, numNodes, numEdges, numCommunities = louvain(Graph)

            # Write Louvain results
            writeResultsLouvain(result, outputDirectory, Graph.edges(), analysisNAME, numNodes, userName_from_ana_config_file, gen_configFile_name)
            print("--- LOUVAIN COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")

        elif COMMUNITY_TYPE_ALGO.lower() == "infomap":
            # Read and process input file to infomap
            im_result, edges, time = infomapAlgo(INPUT_layer_path_from_dict)
            numNodes = im_result.num_nodes
            numEdges =  len(edges)
            numCommunities = im_result.num_top_modules
            # Write Infomap results to .vcom and .ecom files
            writeResultsInfomap(im_result, outputDirectory, edges, analysisNAME, userName_from_ana_config_file, gen_configFile_name)
            print("--- INFOMAP COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")

        elif COMMUNITY_TYPE_ALGO.lower() == "fastgreedy":
            # Send graph location to function and returns ig graph
            Graph, edges, edgeWeights = create_ig_Graph(INPUT_layer_path_from_dict)
            numNodes = Graph.vcount()
            numEdges = len(edges)
            # FASTGREEDY function
            result, time, numCommunities = fastgreedy(Graph, edgeWeights)
            writeResults(result, outputDirectory, edges, analysisNAME, "FastGreedy", time, numNodes, userName_from_ana_config_file, gen_configFile_name)
            print("--- FASTGREEDY COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")

        elif COMMUNITY_TYPE_ALGO.lower() == "walktrap":
            # Send graph location to function and returns ig graph
            Graph, edges, edgeWeights = create_ig_Graph(INPUT_layer_path_from_dict)
            numNodes = Graph.vcount()
            numEdges = len(edges)
            # WALKTRAP function
            result, time, numCommunities = walktrap(Graph, edgeWeights)
            writeResults(result, outputDirectory, edges, analysisNAME, "Walktrap", time, numNodes, userName_from_ana_config_file, gen_configFile_name)
            print("--- WALKTRAP COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")

        elif COMMUNITY_TYPE_ALGO.lower() == "leadingeigenvector":
            # Send graph location to function and returns ig graph
            Graph, edges, edgeWeights = create_ig_Graph(INPUT_layer_path_from_dict)
            numNodes = Graph.vcount()
            # LEADING EIGEN VECTOR function
            result, time = leadingeigenvector(Graph, edgeWeights)
            # calculating edges and no. of comms
            numEdges = len(edges)
            numCommunities = len(result)
            # writing results to file
            writeResults(result, outputDirectory, edges, analysisNAME, "LeadingEigenVector", time, numNodes, userName_from_ana_config_file, gen_configFile_name)
            print("--- LEADING EIGEN VECTOR COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")

        elif COMMUNITY_TYPE_ALGO.lower() == "multilevel":
            # Send graph location to function and returns ig graph
            Graph, edges, edgeWeights = create_ig_Graph(INPUT_layer_path_from_dict)
            numNodes = Graph.vcount()
            # MULTILEVEL function
            result, time = multilevel(Graph, edgeWeights)
            # calculating edges and no. of comms
            numEdges = len(edges)
            numCommunities = len(result)
            writeResults(result, outputDirectory, edges, analysisNAME, "Multilevel", time, numNodes, userName_from_ana_config_file, gen_configFile_name)
            # append the result of louvain algorithm to the resultsList for comparision function later
            # resultsList.append([result, time])
            print("--- MULTILEVEL COMPLETED ---\n")
            ana_log_file_object.ana_msg_log_file(log_file, "Done.")
        else:
            print("Incorrect algorithm mentioned") 
    except Exception as e:  # Replace with actual exception type if you have one
        print(f"An error occurred during {COMMUNITY_TYPE_ALGO} analysis: {str(e)} \n")
        # ana_log_file_object.ana_msg_log_file(log_file, f"An ERROR occurred during {COMMUNITY_TYPE_ALGO} analysis!")
        ana_log_file_object.ana_msg_log_file(log_file, f"An ERROR occurred during {COMMUNITY_TYPE_ALGO} analysis: {str(e)}")

    
    return numNodes, numEdges, numCommunities


"""
    Runs the analysis pipeline using the specified configuration file.

    :param MLN_USR: The path to the user directory.
    :param ana_configfilename: The path to the configuration file.
"""
################################################################ MAIN ################################################################
# Sent the Path to the MLN_USR, where you can output the files, as well as the ana_configfilename.
def main(MLN_USR, ana_configfilename):

    try:
        # relpath finds the path room the given directory
        configFile_to_open = path.relpath(ana_configfilename)

        # separates the ana_configfilename from the absolute path
        # change the config file name each time the user wants to use a new config file
        ana_config_file = os.path.basename(ana_configfilename)
        # config _file first portion :
        # IF southwest.ana THEN southwest is returned
        config_file_first_portion = ana_config_file.split(".")
        
        # creating a log file object
        ana_log_file_object = ana_LogObject()

        # join the system folder to the user directory
        system_folder = os.path.join(MLN_USR, ana_directory_name.system_files.value)
        #if the path for hash table does not exist, a system folder is created
        system_path_exist = os.path.isdir(system_folder)
        if system_path_exist==False:
            os.mkdir(system_folder)

        #join the log folder to the user directory
        ana_log_folder = os.path.join(MLN_USR,ana_directory_name.log_files.value )
        log_path_exist = os.path.isdir(ana_log_folder)
        #if the path for log files does not exist, a log folder is created
        if log_path_exist == False:
            os.mkdir(ana_log_folder)   

        tmp_folder = os.path.join(MLN_USR, ana_directory_name.tmp_files.value)
        tmp_path_exist = os.path.isdir(tmp_folder)
        #if the path for tmp files does not exist, a tmp folder is created
        if tmp_path_exist == False:
            os.mkdir(tmp_folder)

        with open(configFile_to_open, mode='r', encoding="utf8") as ana_config_file:
            #lines contain all the lines of config file in a list, each line is an element of the list
            lines = ana_config_file.readlines()

            INPUT_LAYER_PATH_FROM_DICT = ""

            OUTPUT_DIRECTORY = lines[0].split("=")[1]
            OUTPUT_DIRECTORY = MLN_USR + OUTPUT_DIRECTORY.replace("$MLN_USR", "")
            OUTPUT_DIRECTORY = OUTPUT_DIRECTORY.rstrip("\n")
            # if the path for output directory does not exist, a folder is created
            OUTPUT_DIRECTORY_path_exist = os.path.isdir(OUTPUT_DIRECTORY)
            if OUTPUT_DIRECTORY_path_exist==False:
                os.mkdir(os.path.join(MLN_USR, OUTPUT_DIRECTORY))
            if not os.path.isdir(OUTPUT_DIRECTORY):
                raise FileNotFoundError("==> Output directory not found.\n")

            USERNAME = lines[1].split("=")[1]
            USERNAME = USERNAME.rstrip("\n")

            if lines[2].startswith("INPUT_DIRECTORY"):
                INPUT_LAYER_PATH_FROM_DICT = lines[2].split("=")[1]
                INPUT_LAYER_PATH_FROM_DICT = MLN_USR + INPUT_LAYER_PATH_FROM_DICT.replace("$MLN_USR", "")
                INPUT_LAYER_PATH_FROM_DICT = INPUT_LAYER_PATH_FROM_DICT.rstrip("\n")  
                INPUT_LAYER_PATH_FROM_DICT = INPUT_LAYER_PATH_FROM_DICT + "/" + config_file_first_portion[0] + ".net"      

            # printing all the file headers
            print("OUTPUT_DIRECTORY : ", OUTPUT_DIRECTORY)
            print("USERNAME : ", USERNAME)
            print("INPUT_LAYER_PATH_FROM_DICT : ", INPUT_LAYER_PATH_FROM_DICT)

            ana_log_file_name = ana_log_file_naming(
                USERNAME,
                config_file_first_portion[0],
                ana_extension_layer_name.config_file.value,
                ana_extension_layer_name.log_file.value
            )
            # join log file with complete path
            ana_log_file = os.path.join(ana_log_folder, ana_log_file_name)
            # open a log file for the configuration file
            ana_log_file_object.ana_open_log_file_for_each_layer(ana_log_file)     
            
            # Keep track of the number of layers analyzed
            total_no_of_layer_to_analyze = 0
            layername = ""
            # initialize an empty dictionary to store the layers.
            layers = {}
            pathhh = {}

            for index, line in enumerate(lines):
                if line.startswith('IMPORT'):
                    layer = line.split()[1]
                    layer = layer.rstrip("\n")  # PRINTS "small-64Movies.gen" that is the name from IMPORT line in CONFIG file
                    # currently the path is something like $MLN_USR/system/ira_accident_gen.bin
                    layername = layer[:-len('.gen')]
                    ana_binary_pathname = '$MLN_USR/system/' + USERNAME + '_' + layername + '_gen' + '.bin'
                    # This replaces the string $MLN_USR with the given path
                    pathhh[layer] = MLN_USR + ana_binary_pathname.replace("$MLN_USR", "")
                    layers[layer] = layer[:-len('.gen')]
                    if os.path.exists(pathhh[layer]):
                        try:
                            os.rename('ana_parser_class.py', 'parser_class.py')
                            INPUT_LAYER_PATH_FROM_DICT = ana_get_INPUT_layer_path(pathhh[layer], config_file_first_portion[0])
                            os.rename('parser_class.py', 'ana_parser_class.py')
                        except Exception as e:
                            print(f"An error occurred while reading pickle file: {str(e)} \n")
                        # Error handling
                        if not os.path.isfile(INPUT_LAYER_PATH_FROM_DICT):
                            print("==> Input graph file (.net or .ilf) not found.")
                            ana_log_file_object.ana_msg_log_file(ana_log_file, f"Imported generated layers do not exist. Please execute the {layer} to generate the layers before performing analysis.")
                            ana_log_file_object.ana_ending_msg_log_file_fail(ana_log_file)
                            return 2
                    else:
                        print("Dictionary File not found!")
                
                # check if there's no IMPORT found before the ANALYSIS_NAME, 
                # if INPUT_LAYER_PATH_FROM_DICT is empty then return numerical value 1
                # if pathhh is empty then return numerical value 1
                if line.startswith("ANALYSIS_NAME") and (INPUT_LAYER_PATH_FROM_DICT == "" or pathhh == {}):
                    ana_log_file_object.ana_msg_log_file(ana_log_file, f"No dictinary found. Please execute the {config_file_first_portion[0]}.gen to generate the layers before performing analysis.")
                    ana_log_file_object.ana_ending_msg_log_file_fail(ana_log_file)
                    ana_del_file_tmp_dir(tmp_folder)
                    return 1

                if line.startswith("ANALYSIS_NAME"):    
                    analysisNAME = line.split("=")[1].strip()
                if line.startswith("ANALYSIS_EXPRESSION"):
                    analysisEXPRESSION = line.split("=")[1].strip()
                    COMMUNITY_TYPE_ALGO = analysisEXPRESSION.split("(")[0]
                    layer_name = analysisEXPRESSION.split("(")[1]
                    LAYER_NAME = layer_name.split(")")[0]
                    

                    # printing the details of variables
                    print("ANALYSIS_NAME : ", analysisNAME)
                    print("ANALYSIS_EXPRESSION : ", analysisEXPRESSION)
                    print("COMMUNITY_TYPE_ALGO : ", COMMUNITY_TYPE_ALGO)
                    print("LAYER_NAME : ", LAYER_NAME)

                    log_StartTime = time.time()
                    numNodes, numEdges, numCommunities = community_detection(COMMUNITY_TYPE_ALGO, INPUT_LAYER_PATH_FROM_DICT, OUTPUT_DIRECTORY, analysisNAME, ana_log_file_object, ana_log_file, USERNAME, layername)
                    log_EndTime = time.time()
                    ana_log_file_object.ana_log_for_each_layer((
                        MLN_USR,                                    # z[0]
                        ana_log_file,                               # z[1]
                        OUTPUT_DIRECTORY,                           # z[2]
                        round(log_EndTime-log_StartTime, 4),        # z[3]
                        numNodes,                                   # z[4]
                        numEdges,                                   # z[5]
                        numCommunities                              # z[6]
                    ))


        # FIXME: This is a temporary fix. This is to get the number of layers analyzed
        # check if the all the layers are correctly analyzed in the tmp file. If yes, then move all the files in the output directory and delete from tmp folder. Otherwise just delete all files from tmp durectory 
        list_of_files_in_tmp = os.listdir(tmp_folder) # dir is your directory path
        number_files_in_temp = len(list_of_files_in_tmp)
        file_names = os.listdir(tmp_folder)

        # check if all the layers are generated without any error
        if number_files_in_temp == total_no_of_layer_to_analyze:  
            # move files from tmp to output directory
            for file_name in file_names:
                # Specify path
                file_exist_in_output_directory = os.path.join(OUTPUT_DIRECTORY, file_name)
                isExist = os.path.exists(file_exist_in_output_directory )
                if isExist == False:
                    shutil.move(os.path.join(tmp_folder, file_name), OUTPUT_DIRECTORY)
                else:
                    #if the file with the same name already exists in the directory then the file is removed from the output directory first, then the newly generated file with thesame name is moved from the temp to output directory
                    os.unlink(file_exist_in_output_directory)
                    shutil.move(os.path.join(tmp_folder, file_name), OUTPUT_DIRECTORY)
            # add the success message to the log file
            ana_log_file_object.ana_ending_msg_log_file_success(ana_log_file)
            return 0
        else:
            ana_log_file_object.ana_ending_msg_log_file_fail(ana_log_file)
        ana_del_file_tmp_dir(tmp_folder)
    except Exception as e:
        print(f"An ERROR occurred during analysis: {str(e)} \n")
