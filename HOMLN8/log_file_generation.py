from pathlib import Path
from tabulate import tabulate


class LogObject:
    def __init__(self):
        pass

    #open a log file for each configuration file
    def open_log_file_for_each_layer(self,log_file_name):
        with open(log_file_name, mode='w') as layer_file:
            pass

    #In this function, information regarding the generated layer is passed as tuple to print in the log file
    def log_for_each_layer(self,z):   
            val=".../"+ z[4] + "/"  
            with open(z[1], mode='a') as layer_file:
                layer_file.write("Information Regarding the Generated Layer File:" +  "\n")
                layer_file.write("\t"+"Destination Folder:" + val+ "\n")
                layer_file.write("\t"+"Generation Time(in second):" + str(z[3])+ "\n")
                layer_file.write("\t"+"Number of Node:" +str(z[5])+ "\n")
                layer_file.write("\t"+"Number of Edge:" + str(z[6])+ "\n")
                layer_file.write("\t"+"Number of Connected Component:" + str(z[7])+ "\n")
                layer_file.write("\n")
    
    #print msgs to log file
    def msg_log_file(self,log_file_name,msg):
        with open(log_file_name, mode='a') as layer_file:
            layer_file.write(msg)
            layer_file.write("\n")
    
    #print success msg to log file if all the layers are generated correctly
    def ending_msg_log_file_success(self,log_file_name):
        with open(log_file_name, mode='a') as layer_file:
            layer_file.write("Layer Generation is Successful.")
            
    
    #print failure msg to log file if there is error in any layer
    def ending_msg_log_file_fail(self,log_file_name):
            with open(log_file_name, mode='a') as layer_file:
                layer_file.write("\n")
                layer_file.write("Layer Generation is Unsuccessful.")
