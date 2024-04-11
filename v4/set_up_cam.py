from funcV4 import *


# # Params
center_cords = (360, 280)

# def onclick(event):
#     print('You clicked on point ({:.2f}, {:.2f})'.format(event.xdata, event.ydata))

# fig, ax = plt.subplots()
# ax.plot([1, 2, 3], [4, 5, 6])
# fig.canvas.mpl_connect('button_press_event', onclick)
# plt.show()
## APP
if __name__ == "__main__":

    # Application
    print(f"TEST CAM")
    # Live Feed
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("Error: Could not open video") if not cap.isOpened() else None
    ret, frame = cap.read(0) # Remove first frame

    frame_num = 0
    data_dict = {}
    start_time = time.time()

    frame_num += 1


    # Read a frame from the video
    ret, frame = cap.read(0)


    # Crop the frame
    FRAME_SIZE = 400
    cropped_frame = crop(FRAME_SIZE, center_cords, frame)


    def onclick(event):
        if event.inaxes is not None:
            print('You clicked on point ({:.2f}, {:.2f})'.format(event.xdata, event.ydata))

    # Assuming you have already defined cropped_frame, frame, FRAME_SIZE, and center_cords
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
    plt.scatter(FRAME_SIZE//2, FRAME_SIZE//2, c='r')
    plt.title('Cropped Frame')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cmap='gray')
    plt.scatter(center_cords[0], center_cords[1], c='r')
    plt.title('Original Frame')

    plt.gcf().canvas.mpl_connect('button_press_event', onclick)
    plt.show()
        