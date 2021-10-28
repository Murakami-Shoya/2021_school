#coding:utf-8

#---------------------
#Run on Python2 Only
#need to conect Leap Motion
#
#Leap Motion SDKから手の位置、向き、関節位置の27つの三次元ベクトルを取得するクラス
#
#保存されるデータは
#[palm, normal, direction, 24 bone_joints]　
#1フレームの手モデルは3×27の配列で保持
#---------------------


import sys

my_path = ".."     #親ディレクトリの相対パス
#my_path = "c:\\Users\\tadachi\\Desktop\\SOTUKEN"　#親ディレクトリの絶対パス（研究室）
#my_path = "c:\\Users\\Owner\\Desktop\\SOTUKEN2020\\deep-learning-2-my-file" #親ディレクトリの絶対パス（ノートパソコン）
sys.path.append(my_path)  # 親ディレクトリのファイルをインポートするための設定
sys.path.append(my_path + "\\Leap_Motion_python\\lib")  # Leapをインポートするための設定

import Leap
import copy, thread, time


class Leap2Data(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    all_data = []
    new_data = []

    def on_init(self, controller):
        print ("Initialized" )

    def on_connect(self, controller):
        print ("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print ("Disconnected")

    def on_exit(self, controller):
        hand_index = ["palm_position", "normal", "direction", "T0","T1","T2","T3", "I0","I1","I2","I3","I4",
                           "M0","M1","M2","M3","M4", "R0","R1","R2","R3","R4", "P0","P1","P2","P3","P4"]
       

        print ("Exited")


    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        iBox = frame.interaction_box

        # Get hands
        for hand in frame.hands:
            hand_data = []

            handType = "Left hand" if hand.is_left else "Right hand"
            palm_position = iBox.normalize_point(hand.palm_position, False)
            
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            #手の位置と向きを追加
            hand_data.append([palm_position.x, palm_position.y, palm_position.z])
            hand_data.append([normal.x, normal.y, normal.z])
            hand_data.append([direction.x, direction.y, direction.z])

            #必要な指の関節24箇所の位置ベクトルを追加
            for finger in hand.fingers:
                #Get joint Vector
                bone_data = []
                for b in range(0, 4):
                    if(finger.type == 0 and b==0):
                        continue
                    
                    bone = finger.bone(b)
                    prev_joint = iBox.normalize_point(bone.prev_joint, False)
                    next_joint = iBox.normalize_point(bone.next_joint, False)

                    bone_data.append([prev_joint.x, prev_joint.y, prev_joint.z])

                    if(b==3):
                        bone_data.append([next_joint.x, next_joint.y, next_joint.z])
                    

                hand_data.extend(bone_data)

            #右手だけ保存
            if(handType == "Right hand" and len(hand_data) == 27):
                #self.all_data.extend(hand_data)
                self.new_data = copy.deepcopy(hand_data)
                #print ("  updata (position: %s)" % (palm_position) )
              
                
            else:
                if(handType == "Right hand"):
                    print("---------erore-----%d"%(len(hand_data)))

            
            
            
            
            


def main():
    # Create a sample listener and controller
    listener = Leap2Data()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print ("Press Enter to quit..." )
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
