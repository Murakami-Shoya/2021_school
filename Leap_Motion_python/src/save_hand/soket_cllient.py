#coding: utf-8
# クライアントを作成

import socket
text = ""
for i in range(10):
    text = text + "aaaaaaiiiiiiiii945879824756\\n"

print(text)
print("-------------------------------")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # サーバを指定
    s.connect(('127.0.0.1', 50007))
    # サーバにメッセージを送る
    s.sendall(text.encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    data = s.recv(1024)
    #
    print(repr(data))