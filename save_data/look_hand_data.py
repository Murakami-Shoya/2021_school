#coding:utf-8

#---------------------
#Run on Python2 Only
#
#hand_dataを見るプログラム
#一番最後のmain関数で見たいデータのパスを指定する
#スペースキー : 一時停止
#左右矢印キー : 戻り・送り
#rキー       : 最初から
#マウスドラッグ : 視点移動
#---------------------

import sys

my_path = ".."     #親ディレクトリの相対パス
#my_path = "c:\\Users\\tadachi\\Desktop\\SOTUKEN"　#親ディレクトリの絶対パス（研究室）
#my_path = "c:\\Users\\Owner\\Desktop\\SOTUKEN2020\\deep-learning-2-my-file" #親ディレクトリの絶対パス（ノートパソコン）
sys.path.append(my_path)  # 親ディレクトリのファイルをインポートするための設定

import random, time
import math, copy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd

class lookHandData():

    data = []
    count = 0
    count_flag = True

    #mouse move
    mx = 0.0
    my = 0.0
 
    #lattice size
    lsize = 1.0
 
    #init pos is .. 20 * 20 * 20
    th = math.pi * 0.5
    ph = math.pi * 0.5

    def __init__(self, file_name):
        #データのダウンロード
        data = pd.read_csv(file_name, sep=',', header=None)
        self.data = data.values.reshape([-1, 27, 3])

        self.n, _, _ = self.data.shape
        print("loaded    : " + file_name + "\nN of data : " + str(self.n))
        
    

    def draw(self):
        if self.count >= self.n or self.count < 0:
            self.count = 0

        cx = cy = cz = self.lsize * 0.5
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.9, 0.6, 0.1, 1.0) #(0, 0, 0, 1.0) ⇒ black

        glLoadIdentity()
        #color
        glColor3f(0,0,1)
        #camera position
        gluLookAt( 5*math.sin(self.th)*math.cos(self.ph)+cx,  5*math.cos(self.th)+cy,  5*math.sin(self.th)*math.sin(self.ph)+cz,\
                cx,  cy,  cz, -math.cos(self.th)*math.cos(self.ph),math.sin(self.th),-math.cos(self.th)*math.sin(self.ph) )
 
        self.box([self.lsize/2.0, self.lsize/2.0, self.lsize/2.0], self.lsize)

        #手モデル描画
        self.drawHand(self.data[self.count])

        #正規化した手モデル描画
        self.drawHand(self.normalize(self.data[self.count])[0])

        
        text = "frame number : " + str(self.count) + " / " + str(self.n)
        self.printString(10, 20, text)
 
        glutSwapBuffers()

        if self.count_flag:
            self.count += 1
        
        #フレームレートの設定
        time.sleep(0.1)


    #手モデルを描画する関数
    def drawHand(self, hand):
        if not hand == []:
            glColor3f(1,0,0)
            self.box(hand[0], 0.05)

            glColor3f(0,0,1)
            for x in hand[3:]:
                self.box(x, 0.05)
            
            #指の関節描画
            glLineWidth(5.0)
            glColor3f(1,1,1)
            joint = [3,4,5,7,8,9,10,12,13,14,15,17,18,19,20,22,23,24,25]
            for i in joint:
                self.line(hand[i], hand[i+1])

            glColor3f(1,0,0)
            l = 0.2
            self.line(hand[0], [hand[0][0] + hand[1][0]*l, hand[0][1] + hand[1][1]*l, hand[0][2] + hand[1][2]*l])
            glColor3f(0,1,0)
            self.line(hand[0], [hand[0][0] + hand[2][0]*l, hand[0][1] + hand[2][1]*l, hand[0][2] + hand[2][2]*l])

            glLineWidth(1.0)

    #ラインを描画する関数
    def line(self, x, y):
        glBegin(GL_LINE_LOOP)
        glVertex3d(x[0], x[1], x[2])
        glVertex3d(y[0], y[1], y[2])
        glEnd()

    #box描画関数
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


    #手モデルを正規化する関数
    def normalize(self, X):
        
        hands = X.reshape([-1, 27, 3])
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

            palm_position = np.dot(np.array([0.0, 0.0, 0.0]), R)
            direction = np.dot(direction, R)
            palm_y = np.dot(palm_y, R)

            joint = np.vstack([palm_position, direction, palm_y, joint])

            joints.append(joint)

        joints = np.array(joints).reshape([-1, 27, 3])

        return joints

 
 
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

    #文字を描画する関数
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
        
        if(button==GLUT_LEFT_BUTTON and state == GLUT_DOWN):
            pass

        
        if(button==GLUT_RIGHT_BUTTON and state == GLUT_DOWN):
            self.count = 0


    def keyboard(self, key, x, y):
        if key == " ":
            self.count_flag = not self.count_flag

        elif key == GLUT_KEY_RIGHT:
            self.count += 1

        elif key == GLUT_KEY_LEFT:
            self.count -= 1

        elif key == "r":
            self.count = 0


    def keyboard_2(self, key, x, y):

        if key == GLUT_KEY_RIGHT:
            self.count += 1

        elif key == GLUT_KEY_LEFT:
            self.count -= 1



    def start(self):
        glutInitWindowPosition(50, 50)
        glutInitWindowSize(800, 800)
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE )
        glutCreateWindow("hand data Visualizer")
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
 
  LHD = lookHandData(my_path + "\\my_dataset\\hand_data\\gu_hand.txt")
  LHD.start()