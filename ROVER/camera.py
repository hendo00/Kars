import cv2
import socket
import pickle

class VideoSender:
    def __init__(self, group_number, station_number):
        self.group_number = group_number
        self.server_ip = f"192.168.0.20{station_number}"
        self.server_port = 6666

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000 * group_number)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)
        self.cap.set(4, 240)

    def send_video(self):
        while self.cap.isOpened():
            ret, img = self.cap.read()
            if not ret:
                break
            ret, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            x_as_bytes = pickle.dumps(buffer)
            self.s.sendto((x_as_bytes), (self.server_ip, self.server_port))

        self.cap.release()

# if __name__ == "__main__":
#     group_number = int(input("Enter the group number: "))
#     station_number = input("Enter the station number: ")
#     sender = VideoSender(group_number, station_number)
#     sender.send_video()
