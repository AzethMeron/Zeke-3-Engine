
import traceback
from datetime import datetime

class Log:
    def __init__(self, filepath):
        self.__filepath = filepath
    def __make_log(mess):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return f"=================================================\n" + \
        f"{now} {mess}\n" + \
        f"{traceback.format_exc()}\n"
    def Write(self, e): # e - exception
        try:
            with open(self.__filepath, 'a') as file:
                message = Log.__make_log(str(e))
                file.write(message)
                print(message) 
        except Exception as E:
            print(f"ERROR DURING WRITTING TO FILE {self.__filepath}: {E}")
            print(traceback.format_exc())

Fatal = Log(".fatal.txt")
Regular = Log(".regular.txt")
Expected = Log(".expected.txt")
WIP = Log(".wip.txt")