import cv2
import pandas as pd
from tkinter import Tk, filedialog, Button, Label, PhotoImage
from PIL import Image, ImageTk

def get_color_info(R, G, B):
    minimum = float('inf')
    color_info = {"name": "Unknown Color", "general_name": "Unknown", "hex": "#000000", "r": R, "g": G, "b": B}
    for i in range(len(color_data)):
        try:
            r_val = int(color_data.loc[i, "R"])
            g_val = int(color_data.loc[i, "G"])
            b_val = int(color_data.loc[i, "B"])
            d = abs(R - r_val) + abs(G - g_val) + abs(B - b_val)
            if d < minimum:
                minimum = d
                color_info["name"] = str(color_data.loc[i, "Color ID"])
                color_info["general_name"] = str(color_data.loc[i, "Color Name"])
                color_info["hex"] = str(color_data.loc[i, "Hex"])
        except (ValueError, KeyError):
            continue  # Skip invalid rows
    return color_info

def mouse_click(event, x, y, flags, param):
    global clicked, r, g, b, xpos, ypos
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = True
        xpos, ypos = x, y
        b, g, r = map(int, frame[y, x])  # Ensure values are integers

def open_image():
    global frame, clicked, r, g, b, xpos, ypos  # Declare as global
    Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    
    if file_path:
        frame = cv2.imread(file_path)
        clicked = False  # Ensure clicked starts as False
        cv2.imshow("Image Color Detection", frame)
        cv2.setMouseCallback("Image Color Detection", mouse_click)
        
        while True:
            if clicked:
                color_info = get_color_info(r, g, b)
                cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (int(b), int(g), int(r)), -1)
                text = f"{color_info['name']} ({color_info['general_name']}) - HEX: {color_info['hex']} - RGB({color_info['r']},{color_info['g']},{color_info['b']})"
                text_color = (255 - r, 255 - g, 255 - b)
                cv2.putText(frame, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
                cv2.imshow("Image Color Detection", frame)
                clicked = False  # Reset after each click
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or cv2.getWindowProperty("Image Color Detection", cv2.WND_PROP_VISIBLE) < 1:
                break
        
        cv2.destroyAllWindows()

def start_camera():
    global frame, clicked, r, g, b
    clicked = False
    r = g = b = xpos = ypos = 0
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Live Color Detection")
    cv2.setMouseCallback("Live Color Detection", mouse_click)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if clicked:
            color_info = get_color_info(r, g, b)
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (int(b), int(g), int(r)), -1)
            text = f"{color_info['name']} ({color_info['general_name']}) - HEX: {color_info['hex']} - RGB({color_info['r']},{color_info['g']},{color_info['b']})"
            text_color = (255 - r, 255 - g, 255 - b)
            cv2.putText(frame, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
        cv2.imshow("Live Color Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty("Live Color Detection", cv2.WND_PROP_VISIBLE) < 1:
            break
    cap.release()
    cv2.destroyAllWindows()

# Load and clean the color CSV file
csv_file = "colors.csv"  # Update this if needed
color_data = pd.read_csv(csv_file, delimiter=',', names=["Color ID", "Color Name", "Hex", "R", "G", "B"], keep_default_na=False)

color_data["R"] = pd.to_numeric(color_data["R"], errors="coerce").fillna(0).astype(int)
color_data["G"] = pd.to_numeric(color_data["G"], errors="coerce").fillna(0).astype(int)
color_data["B"] = pd.to_numeric(color_data["B"], errors="coerce").fillna(0).astype(int)

print(color_data.head())

# Create Tkinter GUI
root = Tk()
root.title("Color Detection")
root.geometry("600x400")

# Load background image
bg_image = Image.open("background.jpg")
bg_image = ImageTk.PhotoImage(bg_image)
bg_label = Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Create buttons
btn_live_camera = Button(root, text="Live Camera", command=start_camera, font=("Arial", 14), bg="white", fg="black")
btn_live_camera.place(relx=0.35, rely=0.6, relwidth=0.3, relheight=0.1)

btn_select_photo = Button(root, text="Select Photo", command=open_image, font=("Arial", 14), bg="white", fg="black")
btn_select_photo.place(relx=0.35, rely=0.75, relwidth=0.3, relheight=0.1)

root.mainloop()
