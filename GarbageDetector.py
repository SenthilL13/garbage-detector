import cv2
import math
import cvzone
from ultralytics import YOLO
import os
import smtplib
import ssl
from email.message import EmailMessage
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


# Load YOLO model
def detect_garbage(image_path, model_path="Weights/best.pt", output_path="output.jpg"):
    """Detects garbage in an image and saves processed output."""

    if not os.path.exists(model_path):
        messagebox.showerror("Error", "Model file not found!")
        return None

    if not os.path.exists(image_path):
        messagebox.showerror("Error", "Image file not found!")
        return None

    yolo_model = YOLO(model_path)
    class_labels = ['0', 'c', 'garbage', 'garbage_bag', 'sampah-detection', 'trash']

    img = cv2.imread(image_path)
    results = yolo_model(img)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w, h = x2 - x1, y2 - y1
            conf = round(box.conf[0].item(), 2)
            cls = int(box.cls[0]) if box.cls[0] < len(class_labels) else -1

            if cls != -1 and conf > 0.3:
                cvzone.cornerRect(img, (x1, y1, w, h), t=2)
                cvzone.putTextRect(img, f'{class_labels[cls]} {conf}', (x1, y1 - 10),
                                   scale=0.8, thickness=1, colorR=(255, 0, 0))

    cv2.imwrite(output_path, img)
    print(f"Processed image saved: {output_path}")
    return output_path


def send_email(location, authority, email_id, image_path):
    """Sends an email with the processed garbage detection image."""

    sender_email = "nithyasreemuthuraj@gmail.com"
    sender_password = "nyryfsrlplidjjeo"  # Use environment variable for security
    subject = "Garbage Detection Alert"

    body = f"""
    Location: {location}
    Authority: {authority}
    Email ID: {email_id}

    This email contains the detected garbage image.
    """

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = email_id
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach image
    with open(image_path, "rb") as img_file:
        msg.add_attachment(img_file.read(), maintype="image", subtype="jpeg", filename="garbage_detected.jpg")

    # Send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        messagebox.showinfo("Success", f"Email sent to {email_id} successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")


# ----------------------- UI SETUP -----------------------
def browse_image():
    """Allow user to select an image and preview it."""
    global image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])

    if image_path:
        img = Image.open(image_path)
        img = img.resize((250, 250))  # Resize image for display
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk


def process_and_send():
    """Processes the image and sends an email with the detection result."""
    global image_path

    if not image_path:
        messagebox.showerror("Error", "Please select an image!")
        return

    location = location_entry.get()
    authority = authority_entry.get()
    email_id = email_entry.get()

    if not location or not authority or not email_id:
        messagebox.showerror("Error", "Please fill in all fields!")
        return

    # Process the image
    processed_image = detect_garbage(image_path)
    if processed_image:
        send_email(location, authority, email_id, processed_image)


# Create Tkinter window
root = tk.Tk()
root.title("Garbage Detection & Reporting")
root.geometry("500x600")

# Labels and Inputs
tk.Label(root, text="Garbage Detection System", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="Location:").pack()
location_entry = tk.Entry(root, width=50)
location_entry.pack()

tk.Label(root, text="Authority Name:").pack()
authority_entry = tk.Entry(root, width=50)
authority_entry.pack()

tk.Label(root, text="Email ID:").pack()
email_entry = tk.Entry(root, width=50)
email_entry.pack()

# Image Selection Button
tk.Button(root, text="Upload Image", command=browse_image).pack(pady=10)

# Image Preview
image_label = tk.Label(root)
image_label.pack()

# Submit Button
tk.Button(root, text="Process & Send", command=process_and_send, bg="green", fg="white").pack(pady=20)

# Run the UI
root.mainloop()
