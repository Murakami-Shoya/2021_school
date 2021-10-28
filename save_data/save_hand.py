#coding:utf-8

#---------------------
#Run on Python2 Only
#need to conect Leap Motion
#
#Leap Motionによって手モデルの座標データを保存するプログラム
#
#スペースキー : 座標データを保持するか
#rキー       : 保持したデータをリセット
#sキー       : 保持したデータの保存
#コマンドプロンプトに保存データのファイル名を入力
#my_dataseet\\hand_dataに保存される
#---------------------


import sys

my_path = ".."     #親ディレクトリの相対パス
#my_path = "c:\\Users\\tadachi\\Desktop\\SOTUKEN"　#親ディレクトリの絶対パス（研究室）
#my_path = "c:\\Users\\Owner\\Desktop\\SOTUKEN2020\\deep-learning-2-my-file" #親ディレクトリの絶対パス（ノートパソコン）
sys.path.append(my_path)  # 親ディレクトリのファイルをインポートするための設定

import random
import math, copy, time, glob
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pandas as pd
import numpy as np
from MyLeap import MyLeap


class OpenGL2Draw():

    #mouse move
    mx = 0.0
    my = 0.0
 
    #lattice size
    lsize = 1.0
 
    #init pos is .. 20 * 20 * 20
    th = math.pi * 0.5
    ph = math.pi * 0.5

    def __init__(self):
        self.gesture_name = raw_input("enter gesture name >> ").replace('\r', '')
        self.data_dir = '../my_dataset/hand_data/'
        self.data = []
        self.all_data = []
        self.append_flag = False
        self.L = MyLeap()
        self.columns = self.L.getColumns() # MyLeap参照


        pass
    
    #Leap Motionで取得した手モデルを描画する関数
    def draw(self):
        data = self.L.getData()
        #print("get_data")
        if not data == []:
            self.setdata(data)

        cx = cy = cz = self.lsize * 0.5
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        glLoadIdentity()
        #color
        glColor3f(0,0,1)
        #camera position
        gluLookAt( 5*math.sin(self.th)*math.cos(self.ph)+cx,  5*math.cos(self.th)+cy,  5*math.sin(self.th)*math.sin(self.ph)+cz,\
                cx,  cy,  cz, -math.cos(self.th)*math.cos(self.ph),math.sin(self.th),-math.cos(self.th)*math.sin(self.ph) )
 
        self.box([self.lsize/2.0, self.lsize/2.0, self.lsize/2.0], self.lsize)

        #手モデルの描画
        self.drawHand(self.data)

        #正規化した手モデルの描画
        self.drawHand(self.normalize(self.data))

        text = "save flame : " + str(len(self.all_data) / 27.0)
        self.printString(10, 20, text)
        
        glutSwapBuffers()

        #保存する感覚の設定
        #仮想立体裁断システムのフレームレートに近い方が良い（10fpsくらい?）-> 100fps
        time.sleep(0.01)

    #手モデルを描画する関数
    def drawHand(self, data):
        #data = self.data
        if not data == []:

            glColor3f(1,0,0)
            self.box(data[0], 0.05)

            glColor3f(0,0,1)
            for x in data[3:]:
                self.box(x, 0.05)
            
            glLineWidth(5.0)
            glColor3f(1,1,1)
            joint = [3,4,5,7,8,9,10,12,13,14,15,17,18,19,20,22,23,24,25]
            for i in joint:
                self.line(data[i], data[i+1])

            glColor3f(1,1,0)
            l = 0.2
            self.line(data[0], [data[0][0] + data[1][0]*l, data[0][1] + data[1][1]*l, data[0][2] + data[1][2]*l])
            self.line(data[0], [data[0][0] + data[2][0]*l, data[0][1] + data[2][1]*l, data[0][2] + data[2][2]*l])

            glLineWidth(1.0)

    #データをまとめる
    def setdata(self, data):
        self.data = copy.deepcopy(data)
        if self.append_flag == True:
            self.all_data.extend(self.data)

    
    def line(self, x, y):
        glBegin(GL_LINE_LOOP)
        glVertex3d(x[0], x[1], x[2])
        glVertex3d(y[0], y[1], y[2])
        glEnd()

    def box(self, x, s):
        x_min = x[0] - s/2.0
        y_min = x[1] - s/2.0
        z_min = x[2] -s/2.0

        glBegin(GL_LINE_LOOP)
        glVertex3d(x_min, y_min, z_min)
        glVertex3d(x_min,y_min + s, z_min)
        glVertex3d(x_min + s,y_min + s, z_min)
        glVertex3d(x_min + s, y_min, z_min)
        glEnd()

        glBegin(GL_LINE_LOOP)
        glVertex3d(x_min, y_min, z_min + s)
        glVertex3d(x_min,y_min + s, z_min + s)
        glVertex3d(x_min + s,y_min + s, z_min + s)
        glVertex3d(x_min + s, y_min, z_min + s)
        glEnd()

        self.line([x_min, y_min, z_min], [x_min, y_min, z_min + s])
        self.line([x_min, y_min + s, z_min], [x_min, y_min + s, z_min + s])
        self.line([x_min + s, y_min, z_min], [x_min + s, y_min, z_min + s])
        self.line([x_min + s, y_min + s, z_min], [x_min + s, y_min + s, z_min + s])

    #正規化する関数
    def normalize(self, X):
        if X==[]:
            return []
        
        hands = np.array(X).reshape([-1, 27, 3])
        joints = []

        for hand in hands:
            palm_position = hand[0]
            direction = hand[1]
            palm_y = hand[2]
        
            palm_x = np.cross(direction, palm_y,) #外積から三つ目のベクトル生成

            R = np.stack([palm_x, palm_y, direction]) #基底行列
            R = np.linalg.inv(R) #逆行列計算

            joint = hand[3:]
            joint = joint - palm_position

            joint = np.dot(joint, R) #正規化するアフィン変換

            joint = np.vstack([palm_position, direction, palm_y, joint])

            joints.append(joint)

        joints = np.array(joints).reshape([27, 3])
        joints = joints.tolist()

        return joints

    def printString(self, x, y, text):
        glColor3f(1, 1, 1)

        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 800, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glRasterPos2f(x, y)
        

        glutBitmapString(GLUT_BITMAP_9_BY_15, text)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
 
    def init(self):
        glClearColor(0, 0, 0, 0)
 
 
    def idle(self):
        glutPostRedisplay()
 
 
    def reshape(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30.0, w/h, 1.0, 100.0)
        glMatrixMode (GL_MODELVIEW)
 
 
    def motion(self, x, y):
 
        dltx = self.mx -x
        dlty = self.my -y

 
        #Invalid large motion
        if 10 < abs(dltx):
            dltx = 0
        if 10 < abs(dlty):
            dlty = 0
 
        self.ph = self.ph - 0.01*dltx
        self.th = self.th + 0.01*dlty
        glutPostRedisplay()
        glutSwapBuffers()
        self.mx = x
        self.my = y


    def mouse(self, button, state, x, y):
        
        if(button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
            pass

        if(button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN):
            pass
            

    def keyboard(self, key, x, y):
        if key == " ": #データを保持するかのフラグの変更
            self.append_flag = not self.append_flag
            print("sppend set : ", self.append_flag)

        elif key == "r": #初期化
            self.all_data = []
            print("reseted all_data")

        elif key == "s": #セーブする
            self.save_file()
            self.all_data = []
            print("reseted all_data")


    def keyboard_2(self, key, x, y):

        if key == GLUT_KEY_RIGHT:
            pass

        elif key == GLUT_KEY_LEFT:
            pass

    def save_file(self):
        # 取得したデータをDataFrameとして保存 
        data = np.array(self.all_data).reshape(-1, 27*3)
        df = pd.DataFrame(data=data, columns=self.columns)

        #既存のジェスチャーのファイルの数を取得
        data_files = glob.glob(self.data_dir + self.gesture_name + "*.csv")
        file_num = len(data_files)
        #"sample_000.csv"のフォーマットで保存する
        file_num = "{0:03d}".format(file_num+1)
        file_name = self.gesture_name + "_" + file_num + ".csv"

        df.to_csv(self.data_dir + file_name, header=True, index=False)
        print("%s has been saved. frame : %d" %(file_name, len(df)))
        print("")


    def start(self):
        glutInitWindowPosition(50, 50)
        glutInitWindowSize(800, 800)
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE )
        glutCreateWindow("pyOpenGL TEST")
        glutDisplayFunc(self.draw)
        glutReshapeFunc(self.reshape)
        glutMotionFunc(self.motion)
        glutMouseFunc(self.mouse)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.keyboard_2)
        self.init()
        glutIdleFunc(self.idle)
        glutMainLoop()

 
 
if __name__ == "__main__":
 
  OD = OpenGL2Draw()
  OD.start()