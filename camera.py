import cv2

# Cambia el número 0 por el índice de tu cámara o la dirección IP
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()

    # Aquí puedes realizar operaciones en cada frame si lo deseas

    cv2.imshow('Moticam 2300', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
