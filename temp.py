import cv2
import numpy as np

img = cv2.imread('image.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
inverse = cv2.bitwise_not(gray)
blur = cv2.GaussianBlur(inverse, (21, 21), 0)
invertedblur = cv2.bitwise_not(blur)
sketch = cv2.divide(gray, invertedblur, scale=256.0)

gamma = 3

adjusted = np.power(sketch/255.0, gamma)
adjusted = np.uint8(adjusted*255)

cv2.imwrite('2.png', adjusted)

