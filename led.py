import socket
import pyautogui as pag
import cv2 as cv
import numpy as np
import os
import sys

def verif_args():
    if len(sys.argv) != 2:
        print("Wrong usage: python3 led.py <Local_IP> <Port>")
        return False
    else:
        return True

def main():
    while True:
        screen = pag.screenshot()
        screencv = cv.cvtColor(np.array(screen), cv.COLOR_RGB2BGR)

        couleur_dom = {}

        y = -20
        for i in range (50):
            x = 10
            y = y + 32
            for j in range (10):
                (b, g, r) = screencv[y,x]
                if (b, g, r) in couleur_dom:
                    couleur_dom[(b, g, r)] += 1
                else:
                    couleur_dom[(b, g, r)] = 1
                x = x + 57

        maxi = max(couleur_dom, key=couleur_dom.get)

        color_fin = []
        for k in range(3):
            val = list(hex(maxi[k]))
            val.pop(0)
            val.pop(0)
            val = ''.join(val)
            color_fin.append(val)

        red = int(color_fin[2], 16)
        green = int(color_fin[1], 16)
        blue = int(color_fin[0], 16)
        print (red, green, blue)

        data_hex = bytes([0x41, red, green, blue, 0, 0, 0, 0])
        co.sendall(data_hex)

if __name__ == "__main__":
    DEST_IP, DEST_PORT = sys.argv[1], int(sys.argv[2])
    if verif_args():
        co = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        co.connect((DEST_IP, DEST_PORT))
        main()
        co.close()