# ai_deck_streaming.py

import socket
import struct
import argparse
import cv2
import numpy as np
import time

class AIDeckStreaming:
    def __init__(self, ip="192.168.4.1", port=5000, save=False):
        self.ip = ip
        self.port = port
        self.save = save
        self.client_socket = self.connect_to_deck()

    def connect_to_deck(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        print("Socket connected")
        return client_socket

    def receive_image_data(self):
        packet_info_raw = self.rx_bytes(4)
        [length, routing, function] = struct.unpack('<HBB', packet_info_raw)

        img_header = self.rx_bytes(length - 2)
        [magic, width, height, depth, format, size] = struct.unpack('<BHHBBI', img_header)

        if magic == 0xBC:
            img_stream = bytearray()

            while len(img_stream) < size:
                packet_info_raw = self.rx_bytes(4)
                [chunk_length, dst, src] = struct.unpack('<HBB', packet_info_raw)
                chunk = self.rx_bytes(chunk_length - 2)
                img_stream.extend(chunk)

            return img_stream

    def process_image_data(self, img_stream, count):
        format = struct.unpack('<B', img_stream[0:1])[0]

        if format == 0:
            bayer_img = np.frombuffer(img_stream, dtype=np.uint8)
            bayer_img.shape = (244, 324)
            color_img = cv2.cvtColor(bayer_img, cv2.COLOR_BayerBG2BGRA)
            cv2.imshow('Raw', bayer_img)
            cv2.imshow('Color', color_img)
            if self.save:
                cv2.imwrite(f"stream_out/raw/img_{count:06d}.png", bayer_img)
                cv2.imwrite(f"stream_out/debayer/img_{count:06d}.png", color_img)
            cv2.waitKey(1)
        else:
            with open("img.jpeg", "wb") as f:
                f.write(img_stream)
            nparr = np.frombuffer(img_stream, np.uint8)
            decoded = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            cv2.imshow('JPEG', decoded)
            cv2.waitKey(1)

    def run(self):
        start = time.time()
        count = 0

        while True:
            imgStream = self.receive_image_data()
            self.process_image_data(imgStream, count)
            count += 1
            meanTimePerImage = (time.time()-start) / count
            print("{}".format(meanTimePerImage))
            print("{}".format(1/meanTimePerImage))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to AI-deck JPEG streamer example')
    parser.add_argument("-n", default="192.168.4.1", metavar="ip", help="AI-deck IP")
    parser.add_argument("-p", type=int, default='5000', metavar="port", help="AI-deck port")
    parser.add_argument('--save', action='store_true', help="Save streamed images")
    args = parser.parse_args()

    ai_deck_streaming = AIDeckStreaming(ip=args.n, port=args.p, save=args.save)
    ai_deck_streaming.run()
