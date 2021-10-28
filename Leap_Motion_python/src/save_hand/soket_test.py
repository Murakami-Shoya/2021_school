#coding: utf-8

import socket
import time

class Soket2Processing:

    def __init__(self):
        host = "127.0.0.1" #Processingで立ち上げたサーバのIPアドレス
        port = 10001       #Processingで設定したポート番号

        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #オブジェクトの作成
        self.socket_client.connect((host, port))
        
    def sendArray(self, array):
        text = "cut\n"
        for i in array:
            for j in i:
                text = text + str(j) + ","

            text = text + "\n"

        self.socket_client.send(text) 
        


def main():

    mySoket = Soket2Processing()

    for i in range(100):
        time.sleep(0.01)
        mySoket.sendArray([[i,i,i]])
    
    time.sleep(1)

    

if __name__ == '__main__':
    main()


