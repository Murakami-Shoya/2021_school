import Leap, sys, thread, time, glob
import pandas as pd
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class LeapListener(Leap.Listener):

    def on_init(self, controller):
        print "Initialized"

        self.file_dir = 'leap_dataset'
        self.finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        # self.bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
        # self.state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
        self.dynamic_hand_df = pd.DataFrame()
        self.get_data_flag = False
        self.gesture_name = None

    def on_connect(self, controller):
        print "Connected"
        print "***Make 'leap_dataset' directory***"
        print "Press ctrl+c to exit."

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited                                 "

    def on_frame(self, controller):
        frame = controller.frame()
        iBox = frame.interaction_box

        # ジェスチャー名を入力するまで何もしない
        if self.gesture_name is None:
            return None
        # データ記録前で手の準備ができていない状態
        if (not self.get_data_flag and self.dynamic_hand_df.empty):
            sys.stdout.write("Get your hand ready                 \r")
            sys.stdout.flush()

        for hand in frame.hands:
            # データ記録前で手の準備が完了した状態
            if (not self.get_data_flag and self.dynamic_hand_df.empty):
                sys.stdout.write("OK, press Enter to start.\r")
                sys.stdout.flush()
            
            #もしもデータを取得する入力があればデータを格納
            if hand.is_valid and self.get_data_flag:
                # データを格納するDataFrameの行数を取得
                dynamic_hand_df_len = len(self.dynamic_hand_df)
                # 手のひら正規化座標
                palm_position = iBox.normalize_point(hand.palm_position, False)
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_position_x"] = palm_position.x
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_position_y"] = palm_position.y
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_position_z"] = palm_position.z

                # 手のひら法線ベクトル
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_normal_x"] = hand.palm_normal.x
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_normal_y"] = hand.palm_normal.y
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_normal_z"] = hand.palm_normal.z

                # 指先方向ベクトル
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_finger_direction_x"] = hand.direction.x
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_finger_direction_y"] = hand.direction.y
                self.dynamic_hand_df.loc[dynamic_hand_df_len, "palm_finger_direction_z"] = hand.direction.z

                # show data frame number
                sys.stdout.write("Press Enter to exit. Frame number: %s\r" % (dynamic_hand_df_len+1))
                sys.stdout.flush()

                for finger in hand.fingers:

                    # Get bones
                    for b in range(0, 4):
                        # if finger is Thumb, Metacarpal and Proximame is same
                        if finger.type == 0 and b == 0:
                            continue

                        bone = finger.bone(b)
                        # 0:Metacarpal  1:Proximame   2:Intete    3:Distal
                        index_finger_name = self.finger_names[finger.type] + '_' + str(b)
                        # 正規化した関節座標
                        normalize_prev_joint = iBox.normalize_point(bone.prev_joint, False)
                        self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_x'] = normalize_prev_joint.x
                        self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_y'] = normalize_prev_joint.y
                        self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_z'] = normalize_prev_joint.z

                        # if bone is Distal, get next_joint data
                        if b == 3:
                            index_finger_name = self.finger_names[finger.type] + '_4'

                            normalize_next_joint = iBox.normalize_point(bone.next_joint, False)
                            self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_x'] = normalize_next_joint.x
                            self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_y'] = normalize_next_joint.y
                            self.dynamic_hand_df.loc[dynamic_hand_df_len, index_finger_name + '_z'] = normalize_next_joint.z

        if (frame.hands.is_empty):
            self.get_data_flag = False

    def save_file(self):
        #既存のジェスチャーのファイルの数を取得
        data_files = glob.glob("./leap_dataset/" + self.gesture_name + "*.csv")
        file_num = len(data_files)
        #"sample_000.csv"のフォーマットで保存する
        file_num = "{0:03d}".format(file_num+1)
        output_file_name = self.gesture_name + "_" + file_num + ".csv"
        self.dynamic_hand_df.to_csv(self.file_dir + "/" + output_file_name, index=False)
        sys.stdout.write("%s has been saved.\n" % (output_file_name))
        # print(self.dynamic_hand_df.head())
        # print(str(len(self.dynamic_hand_df)) + "rows")
    
    def ask_gesture_name(self):
        print "What is gesture name? >> ",
        self.gesture_name = sys.stdin.readline().replace("\n", "")

    def reset_data(self):
        self.dynamic_hand_df = pd.DataFrame()
        print "Data has been reset.\n"



def main():
    # Create a sample listener and controller
    listener = LeapListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Ctrl+c is pressed
    try:
        time.sleep(0.5)
        if listener.gesture_name is None:
            listener.ask_gesture_name()
        while True:
            key_input = sys.stdin.readline().replace("\n", "")
            if key_input == "":
                if listener.dynamic_hand_df.empty:
                    listener.get_data_flag = True
                    # print(listener.get_data_flag)
                else:
                    listener.get_data_flag = False
                    print "save:s or delete:d ? >> ",
                    key_input = sys.stdin.readline().replace("\n", "")
                    if key_input == "s":
                        listener.save_file()
                        listener.reset_data()
                    elif key_input == "d":
                        listener.reset_data()
            elif key_input == "q":
                break


    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()