import cv2

def sketchify(path):

    image = cv2.imread(path)

    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    invert = cv2.bitwise_not(grey_img)
    blur = cv2.GaussianBlur(invert, (21,21), 0)
    inverted_blur = cv2.bitwise_not(blur)
    sketch = cv2.divide(grey_img, inverted_blur, scale=256.0)

    cv2.imwrite(path + ".png", sketch)