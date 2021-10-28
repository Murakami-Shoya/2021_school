#coding:utf-8

import sys
my_path = "c:\\Users\\tadachi\\Desktop\\\x91\xb2\x8b\xc6\x8c\xa4\x8b\x86\\LeapMotion"
sys.path.append(my_path + '\\leap_python\\lib')  # 親ディレクトリのファイルをインポートするための設定
print(sys.path)
import Leap, thread, time
import pandas as pd
from soket_test import Soket2Processing
mySoket = Soket2Processing()

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    all_data = []

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
        df = pd.DataFrame(data = self.all_data)
            
        df.to_csv(my_path + "\\leap_python\\src\\save_hand\\data\\hand_data.txt", header=False, index = False)
        df.to_csv(my_path + "\\leap_processing\\handData2draw\\data\\hand_data.txt", header=False, index = False)
        print("save hand_data.txt , len : %d , frame : %f" %(len(self.all_data), len(self.all_data)/27.0) )

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
            #print ("  %s, position: %s" % (handType, palm_position)  )
            
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            hand_data.append([palm_position.x, palm_position.y, palm_position.z])
            hand_data.append([normal.x, normal.y, normal.z])
            hand_data.append([direction.x, direction.y, direction.z])

            #print ("  normal: %s, direction: %s" % (normal, direction)  )


            for finger in hand.fingers:

                #print( "    %s finger" % (self.finger_names[finger.type]))

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
                    
                    #print( "      %s, start: %s, end: %s" % (self.bone_names[bone.type], prev_joint, next_joint,))
                
                #for i ,v in enumerate(bone_data):
                    #print( "      %s : %s" %(i, v) )

                hand_data.extend(bone_data)

            #for i ,v in enumerate(hand_data):
                    #print( "      %s : %s" %(i, v) )
            
            if(handType == "Right hand" and len(hand_data) == 27):
                self.all_data.extend(hand_data)
                print ("  append data (position: %s)" % (palm_position)  )

                mySoket.sendArray(hand_data)
                print("----send to Processing------ len:" + str(len(hand_data)))


            else:
                if(handType == "Right hand"):
                    print("---------erore-----%d"%(len(hand_data)))

            
            
            
            
            


def main():
    # Create a sample listener and controller
    listener = SampleListener()
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
