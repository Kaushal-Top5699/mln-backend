#maps the primary key column of input csv file to unique ids staring from 1 and increaming the value until all the IDs are converted
class Mapper:
    #constructor method
    def __init__(self,
                 INPUT_FILE_NAME: str = None):
        self.__INPUT_FILE_NAME = INPUT_FILE_NAME
    #convert the primary key column values to ids starting from 1 and incrementing the values and store the mapped values in a csv file in the folder mapped_csv_files
    def map_primary_key_column_id(self) -> str:
        return self._INPUT_FILE_NAME
