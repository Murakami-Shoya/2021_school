#coding:utf-8

#---------------------
#Run on Python2 Only
#
#Leap2Dataから手モデルの座標データを取得するクラス
#---------------------

import sys

my_path = ".."     #親ディレクトリの相対パス
#my_path = "c:\\Users\\tadachi\\Desktop\\SOTUKEN"　#親ディレクトリの絶対パス（研究室）
#my_path = "c:\\Users\\Owner\\Desktop\\SOTUKEN2020\\deep-learning-2-my-file" #親ディレクトリの絶対パス（ノートパソコン）
sys.path.append(my_path)  # 親ディレクトリのファイルをインポートするための設定
sys.path.append(my_path + "\\Leap_Motion_python\\lib")  # Leapをインポートするための設定

import thread, time
import Leap
from Leap2Data import Leap2Data


class MyLeap():
    # Create a sample listener and controller
    listener = Leap2Data()
    controller = Leap.Controller()


    def __init__(self):
        

        # Have the sample listener receive events from the controller
        self.controller.add_listener(self.listener)

        # Keep this process running until Enter is pressed
        print ("Press Enter to quit..." )
        #try:
        #    sys.stdin.readline()
        #except KeyboardInterrupt:
        #    sys.exit()
        #finally:
            # Remove the sample listener when done
        #    self.controller.remove_listener(self.listener)

    
    def getData(self):
        data = self.listener.new_data
        return data

    def getColumns(self):
        hand_columns_list = ["palm_position", "normal", "direction", "T0","T1","T2","T3", "I0","I1","I2","I3","I4", "M0","M1","M2","M3","M4", "R0","R1","R2","R3","R4", "P0","P1","P2","P3","P4"]
        columns = []
        xyz_columns_list = ['x', 'y', 'z']
        for hand_columns in hand_columns_list:
            for xyz_columns in xyz_columns_list:
                columns.append(hand_columns + "_" + xyz_columns)

        return columns

if __name__ == "__main__":
    L = MyLeap()
#     while True:
#         data = L.getData()
#         print("get_data")
#         if not data == []:
#             print(data[0])
#         time.sleep(1.0/10.0)
