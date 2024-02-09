from math import radians, cos, sin, asin, sqrt
from numpy import dot
from numpy.linalg import norm 
import string
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import math
import numpy as np
from haversine import haversine, Unit
from nltk.tokenize import word_tokenize 
from sklearn.feature_extraction.text import TfidfVectorizer
from math import radians, cos, sin, asin, sqrt
import cmath
nltk.download('stopwords')
stopwords=stopwords.words('english')

#check if a value can be converted to float
def isFloat(s):
   try:
      float(s)
      return True
   except:
      return False

# find common elements between two lists
def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

"""
#remove stopwords and punctuations from text
def clean_string(text):        
    text=''.join([word for word in text if word not in string.punctuation])
    text=text.lower()
    text=' '.join([word for word in text.split() if word not in stopwords])
    return text
"""
class SimilarityObject:
    def __init__(self):
        pass
       
    #similarity metric computation for rule 1, x=(i[0][feature_col_no],i[1][feature_col_no], str_val)
    def nominal_metric(self, x):
        if x[0]==x[1]:
            return x[2]

    #similarity metric for rule 2,x=i[0][feature_col_no],i[1][feature_col_no], THRESHOLD,str_val
    #calculate the jaccard distance between two lists
    #list accepts integer, float and string types and similarity ranges from 0.0 - 1.0
    def num_metric_jaccard_similarity(self,x):
        try:
            list1=x[0].split(",")
            list2=x[1].split(",")
            common = intersection(list1, list2)
            similarity=len(common) / (len(list1) + len(list2) - len(common))
            if (similarity<x[2]):
                return x[3]
        except:
            pass
    
    #similarity metric for rule 2,x=i[0][feature_col_no],i[1][feature_col_no], THRESHOLD,str_val
    #calculate the eucliden distance between two lists
    def num_metric_euclidean(self,x):
        try:
            list1=x[0].split(",")
            list2=x[1].split(",")

            list1=list(np.float_(list1))
            list2=list(np.float_(list2))

            distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(list1, list2)]))
            if(distance<x[2]):
                return x[3]    
            
        except:
            pass
   
#similarity metric for rule 2,x=i[0][feature_col_no],i[1][feature_col_no], THRESHOLD,str_val        
#calculation of the cosine similarity between two numeric list or string list            
    def cosine_similarity_value(self,x):
        try:  
            cleaned=[]
            
            #clean first string
            text1=''.join([word for word in x[0] if word not in string.punctuation])
            text1=text1.lower()
            text1=' '.join([word for word in text1.split() if word not in stopwords])
            cleaned.append(text1)
            
            #clean sec string
            text2=''.join([word for word in x[1] if word not in string.punctuation])
            text2=text2.lower()
            text2=' '.join([word for word in text2.split() if word not in stopwords])
            cleaned.append(text2)

            #cleaned=list(map(clean_string,list_vec))
            if cleaned[0]!='' or cleaned[1]!='':
                    vectorizer=CountVectorizer().fit_transform(cleaned)
                    vectors=vectorizer.toarray()
                    csim=cosine_similarity(vectors)
                    vec1=vectors[0].reshape(1,-1)
                    vec2=vectors[1].reshape(1,-1)
                    similarity_val=cosine_similarity(vec1,vec2)[0][0]
                    if similarity_val<x[2]:
                            return x[3]
        except:
            pass
                
#for rule 3,x=i[0][feature_col_no],i[1][feature_col_no], ParserObject.RANGE(),str_val)
    def numeric_metric_range(self,x):
        try:
            input1=float(x[0])
            input2=float(x[1])
            range=x[2]
            first_interval= range[0]
            last_interval= range[len(range)-1]
            string = range[1:-1]
            string=string.split(",")
            string[0]=float(string[0])
            string[1]=float(string[1])
            
            if first_interval=="[" and last_interval=="]" and string[0] <= input1 <= string[1] and string[0] <= input2 <= string[1]:
                        return x[3]          
                
            elif first_interval=="(" and last_interval==")" and string[0] < input1 < string[1] and string[0] < input2 < string[1]:
                            return x[3]         
                    
            elif first_interval=="(" and last_interval=="]" and string[0] < input1 <= string[1] and string[0] < input2 <= string[1]:
                            return x[3]           
                    
            elif first_interval=="[" and last_interval==")" and string[0] <= input1 < string[1] and string[0] <= input2 < string[1]:
                            return x[3] 
        except:
            pass      

#for rule 4,z=i[0][feature_col_no],i[1][feature_col_no], ParserObject.RANGE(),NUMBER_OF_EQUI_SIZED_SEGMENTS,str_val
    def numeric_metric_range_with_segments(self,z):
        try:
            input1=float(z[0])
            input2=float(z[1])
            range_val=z[2]
            first_interval= range_val[0]
            last_interval= range_val[len(range_val)-1]
            string = range_val[1:-1]
            string=string.split(",")
            string[0]=float(string[0])
            string[1]=float(string[1])
            interval_value=int((string[1]-string[0])/z[3])
            #contains each splitted segment
            fixed_segment=[]
            #contains the whole segment list
            fixed_segment_list=[] 
            #each segment first value
            first_val=string[0]  
            for x in range(interval_value+1):
                fixed_segment.append(first_val)
                sec_val=first_val+interval_value
                fixed_segment.append(sec_val)
                fixed_segment_list.append(fixed_segment)
                first_val=sec_val
                fixed_segment=[]
            for string in fixed_segment_list:
                    if first_interval=="[" and last_interval=="]" and string[0] <= input1 <= string[1] and string[0] <= input2 <= string[1]:
                                    return z[4]
                    elif first_interval=="(" and last_interval==")" and string[0] < input1 < string[1] and string[0] < input2 < string[1]:

                                    return z[4]
                    elif first_interval=="(" and last_interval=="]" and string[0] < input1 <= string[1] and string[0] <input2 <= string[1]:
    
                                    return z[4]
                    elif first_interval=="[" and last_interval==")" and string[0] <= input1 < string[1] and string[0] <= input2 < string[1]:
                                    return z[4]
        except:
            pass
              
#For rule 5,z=i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_MULTI_RANGE(),str_val
    def numeric_metric_multi_range(self,z):  
        try:     
            input1=float(z[0])
            input2=float(z[1])
            mulri_range_list=[]
            multirange=z[2].split("-")

            for element in multirange:
                mulri_range_list.append(element)

            for string in mulri_range_list:
                    first_interval= string[0]
                    last_interval= string[len(string)-1]
                    string =string[1:-1]
                    string=string.split(",")
                    string[0]=float(string[0])
                    string[1]=float(string[1])
                    if first_interval=="[" and last_interval=="]" and string[0] <= input1 <= string[1] and string[0] <= input2 <= string[1]:
                                return z[3]
                    elif first_interval=="(" and last_interval==")" and string[0] < input1 < string[1] and string[0] < input2 < string[1]:
                                    return z[3]
                    elif first_interval=="(" and last_interval=="]" and string[0] <input1 <= string[1] and string[0] < input2 <= string[1]:
                                return z[3]
                    elif first_interval=="[" and last_interval==")" and string[0] <= input1 < string[1] and string[0] <= input2 < string[1]:
                                return z[3]  
        except:
            pass

    #for rule 6,x=i[0][lon_col],i[0][lat_col],i[1][lon_col],i[1][lat_col],"KILOMETERS",THRESHOLD,str_val
    def distance_cal_for_location_haversine(self, z):
        try:
            lon1=float(z[0])
            lat1=float(z[1])
            lon2=float(z[2])
            lat2=float(z[3])
            #print(z)

            # Calculate distance based on the provided units from user
            if z[4]==Unit.KILOMETERS.name:
                distance = haversine((lon1,lat1),(lon2,lat2),unit=Unit.KILOMETERS)
            elif z[4]==Unit.METERS.name:
                distance = haversine((lon1,lat1),(lon2,lat2),unit=Unit.METERS)
            elif z[4]==Unit.MILES.name:
                distance = haversine((lon1,lat1),(lon2,lat2),unit=Unit.MILES)
            elif z[4] == Unit.NAUTICAL_MILES.name:
                distance = haversine((lon1,lat1),(lon2,lat2),unit=Unit.NAUTICAL_MILES)
            
            #print(distance)
            # verify if the distance is in threshold or not
            if(distance < z[5]):
                return z[6]
        
        except:
            pass
            

    #for rule 7,x=i[0][feature_col_no],i[1][feature_col_no],ParserObject.get_DATE_FORMAT(),ParserObject.get_DATE_METRIC(),str_val
    #calculating the metric equality between two different date DAY/MONTH/YEAR
    def numeric_metric_date_equality(self, x): 
        try:
            #try different formats for date
            obj1=x[0].split("-")
            obj2=x[1].split("-")

            if x[2]=="dd-mm-yyyy":
                if x[3]=="DAY":
                    obj1=obj1[0] 
                    obj2=obj2[0]
                elif x[3]=="MONTH":
                    obj1=obj1[1]  
                    obj2=obj2[1]
                elif x[3]=="YEAR":
                    obj1=obj1[2] 
                    obj2=obj2[2]
            
            elif x[2]=="mm-dd-yyyy" : 
                if x[3]=="DAY":
                    obj1=obj1[1] 
                    obj2=obj2[1]
                elif x[3]=="MONTH":
                    obj1=obj1[0]  
                    obj2=obj2[0]
                elif x[3]=="YEAR":
                    obj1=obj1[2] 
                    obj2=obj2[2]
                
            if obj1==obj2:
                return x[4]
        
        except:
            pass

    #for rule 8,x=i[0][feature_col_no],i[1][feature_col_no],ParserObject.get_DATE_FORMAT(),ParserObject.get_DATE_METRIC(), THRESHOLD,str_val
    #calculating the euclidean distance between two different date DAY/MONTH/YEAR
    def numeric_metric_date_euc(self, z): 
        try:
        
            obj1=z[0].split("-")
            obj2=z[1].split("-")

            if z[2]=="dd-mm-yyyy":
                if z[3]=="DAY":
                    obj1=float(obj1[0])
                    obj2=float(obj2[0])
                elif z[3]=="MONTH":
                    obj1=float(obj1[1])  
                    obj2=float(obj2[1])
                elif z[3]=="YEAR":
                    obj1=float(obj1[2])
                    obj2=float(obj2[2])
            
            elif z[2]=="mm-dd-yyyy" : 
                if z[3]=="DAY":
                    obj1=float(obj1[1]) 
                    obj2=float(obj2[1])
                elif z[3]=="MONTH":
                    obj1=float(obj1[0])  
                    obj2=float(obj2[0])
                elif z[3]=="YEAR":
                    obj1=float(obj1[2])
                    obj2=float(obj2[2])

            list1=[]
            list2=[]

            list1.append(obj1)
            list2.append(obj2)
            distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(list1, list2)]))

            if(distance<z[4]):
             return z[5]
        
        except:
            pass
    #rule 9 euclidean,x=i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(),THRESHOLD,str_val 
    #for calculating the euclidean distance for time attribute
    def numeric_metric_time_euc(self, x):
            try:     
                obj1=x[0].split(':') 
                obj2=x[1].split(':')
                
                obj1= float(obj1[0])+ (float(obj1[1])/60)
                obj2= float(obj2[0])+(float(obj2[1])/60) 
                val=obj1 - obj2
                if val<0:
                       val=val*(-1)
                if val < x[3]:       
                    return x[4]
            except:
                pass


    #rule 10,x=i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(),ParserObject.get_RANGE(),str_val
    def numeric_metric_time_range(self, x): 
        try:
        #  if x[2]=="hh:mm":
            obj1=x[0].split(':') 
            obj2=x[1].split(':')

            obj1= float(obj1[0]) + (float(obj1[1])/60)
            obj2=float(obj2[0])+(float(obj2[1])/60)
            range=x[3]

            first_interval= range[0]
            last_interval= range[len(x[3])-1]
            string = range[1:-1]
            string=string.split(",")
            string[0]=float(string[0])
            string[1]=float(string[1])

            
            if first_interval=="[" and last_interval=="]" and string[0] <= obj1 <= string[1] and string[0] <= obj2 <= string[1]:
                            return x[4]        
            elif first_interval=="(" and last_interval==")" and string[0] < obj1 < string[1] and  string[0] < obj2 < string[1]:
                            return x[4]        
            elif first_interval=="(" and last_interval=="]" and string[0] < obj1 <= string[1] and string[0] < obj2 <= string[1]:
                            return x[4]        
            elif first_interval=="[" and last_interval==")" and string[0] <= obj1 < string[1] and string[0] <= obj2 < string[1]:
                            return x[4]  
        except:
            pass      
                  
    #rule 11,x=i[0][feature_col_no],i[1][feature_col_no], ParserObject.get_TIME_FORMAT(), ParserObject.get_MULTI_RANGE(),str_val
    def numeric_metric_time_multirange(self, x): 
        try:
            #if x[2]=="hh:mm":
            input1=x[0].split(':') 
            input2=x[1].split(':')

            input1= float(input1[0]) + (float(input1[1])/60)
            input2=float(input2[0])+(float(input2[1])/60)

            multi_range_list=[]
            multirange=x[3].split("-")
        # isSimilar=False 
            for element in multirange:
                multi_range_list.append(element)

            for string in multi_range_list:
                    first_interval= string[0]
                    last_interval= string[len(string)-1]
                    string =string[1:-1]
                    string=string.split(",")
                    string[0]=float(string[0])
                    string[1]=float(string[1])
                    if first_interval=="[" and last_interval=="]" and string[0] <= input1 <= string[1] and string[0] <= input2 <= string[1]:
                                    return x[4]
                    elif first_interval=="(" and last_interval==")" and string[0] < input1 < string[1] and string[0] < input2 < string[1]:
                                    return x[4]
                    elif first_interval=="(" and last_interval=="]" and string[0] < input1 <= string[1] and string[0] < input2 <= string[1]:
                                    return x[4]
                    elif first_interval=="[" and last_interval==")" and string[0] <= input1 < string[1] and string[0] <= input2 < string[1]:
                                    return x[4]   

        except:
            pass  
        