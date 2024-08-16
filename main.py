import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import cv2
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageTk
from google.auth.transport.requests import Request
import os
import shutil
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import PhotoImage
import threading
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import mimetypes
import io
import zipfile
import re

import customtkinter

SCOPES = ["https://www.googleapis.com/auth/drive"]

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")


class VideoBackground:
    def __init__(self, root, video_file):
        self.root = root
        self.video_file = video_file
        self.video_cap = cv2.VideoCapture(self.video_file)
        self.create_widgets()

    def create_widgets(self):
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(fill="both", expand=True)

    def play_video(self):
        ret, frame = self.video_cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.video_label.configure(image=photo)
            self.video_label.image = photo
            self.video_label.after(10, self.play_video)
        else:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_video()


class Backuproot:
    def __init__(self, root, drive_service):
        self.root = root
        self.root.title("Backup Application")
        self.root.geometry("1000x590")  # Set the window size (width x height)
        self.root.resizable(width=False, height=False)
        self.drive_service = drive_service  # Google Drive service
        self.background_image = PhotoImage(file="background.png")

        # Create a Label to display the background image
        self.background_label = ttk.Label(self.root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)  # Cover the entire window

        self.create_widgets()
        self.backup_interval = 45

    def schedule_backup(self):
        self.perform_backup()
        self.root.after(self.backup_interval * 1000, self.schedule_backup)  # Schedule the next backup

    def create_widgets(self):
        self.frame = customtkinter.CTkFrame(master=self.root, width=320, height=320, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.button1 = customtkinter.CTkButton(master=self.frame, width=220, text="Backup", command=self.perform_backup,
                                               corner_radius=6)
        self.button1.place(x=50, y=110)
        self.button1 = customtkinter.CTkButton(master=self.frame, width=220, text="Manual Backup",
                                               command=self.open_manual_backup_window, corner_radius=6)
        self.button1.place(x=50, y=200)

        # Create a label for login status
        # Create a label for login status
        self.status_label1 = ttk.Label(master=self.frame, text="", foreground="green", background="#2b2b2b")
        self.status_label1.place(x=50, y=265)

    def browse_source(self):
        source_dir = filedialog.askdirectory()
        self.source_entry.delete(0, tk.END)
        self.source_entry.insert(0, source_dir)

    def browse_destination(self):
        dest_dir = filedialog.askdirectory()
        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(0, dest_dir)

    # Set the background color to light blue
    def open_manual_backup_window(self):
        # Start the backup schedule in the background using a separate thread
        backup_thread = threading.Thread(target=self.schedule_backup)
        backup_thread.daemon = True  # Allow the thread to be killed when the main program exits
        backup_thread.start()

        # Create a new window for manual backup
        manual_backup_window = tk.Toplevel(self.root)
        manual_backup_window.title("Manual Backup")
        manual_backup_window.geometry("1000x590")
        manual_backup_window.resizable(width=False, height=False)

        self.frame = customtkinter.CTkFrame(manual_backup_window, width=550, height=550, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.l2 = customtkinter.CTkLabel(master=self.frame, text="Manual Backup", font=('Century Gothic', 20, "bold"))
        self.l2.place(x=50, y=45)

        self.button1 = customtkinter.CTkButton(master=self.frame, width=180, text="Select Source",
                                               command=self.browse_source, corner_radius=6)
        self.button1.place(x=50, y=110)

        self.source_entry = customtkinter.CTkEntry(master=self.frame, width=220)
        self.source_entry.place(x=250, y=110)

        self.button2 = customtkinter.CTkButton(master=self.frame, width=180, text="Select Destination",
                                               command=self.browse_destination, corner_radius=6)
        self.button2.place(x=50, y=200)

        self.destination_entry = customtkinter.CTkEntry(master=self.frame, width=220)
        self.destination_entry.place(x=250, y=200)

        self.button3 = customtkinter.CTkButton(master=self.frame, width=150, text="Start Backup",
                                               command=self.manual_backup, corner_radius=6)
        self.button3.place(x=180, y=280)

        self.status_label = ttk.Label(master=self.frame, text="", foreground="green", background="#2b2b2b")
        self.status_label.place(x=50, y=350)

    def manual_backup(self):
        source_dir = self.source_entry.get()  # Get the source directory from the entry widget
        local_backup_dir = self.destination_entry.get()  # Get the destination directory from the entry widget

        try:
            # Create the local backup directory if it doesn't exist
            if not os.path.exists(local_backup_dir):
                os.makedirs(local_backup_dir)

            # Store the current timestamp
            timestamp = datetime.datetime.now()

            # Iterate through files in the source directory, excluding directories
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_item = os.path.join(root, file)
                    dest_item = os.path.join(local_backup_dir, os.path.relpath(source_item, source_dir))

                    # Read the content of the source file
                    with open(source_item, 'rb') as f:
                        source_content = f.read()

                    # Check if the destination file already exists
                    if os.path.exists(dest_item):
                        # Read the content of the destination file
                        with open(dest_item, 'rb') as f:
                            dest_content = f.read()

                        # If the content is different, update the destination file
                        if source_content != dest_content:
                            with open(dest_item, 'wb') as f:
                                f.write(source_content)
                    else:
                        # Create directories if they don't exist
                        if not os.path.exists(os.path.dirname(dest_item)):
                            os.makedirs(os.path.dirname(dest_item))
                        # Copy the file from source to destination
                        with open(dest_item, 'wb') as f:
                            f.write(source_content)

                    # Update the access and modification times of the file to the current timestamp
                    os.utime(dest_item, (timestamp.timestamp(), timestamp.timestamp()))

            self.status_label.config(text="Manual backup completed.")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def perform_backup(self):
        source_dir = 'C:\\Users\\Kamil\\OneDrive\\Desktop\\BackupDAppNew\\BackupDApp\\source'  # Replace with your source directory
        local_backup_dir = 'C:\\Users\\Kamil\\OneDrive\\Desktop\\BackupDAppNew\\BackupDApp\\backup'  # Replace with your local backup directory

        try:
            # Define the timestamp here
            timestamp = datetime.datetime.now()

            # Iterate through files in the source directory, excluding directories
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_item = os.path.join(root, file)
                    dest_item = os.path.join(local_backup_dir, os.path.relpath(source_item, source_dir))

                    # Read the content of the source file
                    with open(source_item, 'rb') as f:
                        source_content = f.read()

                    # Check if the destination file already exists
                    if os.path.exists(dest_item):
                        # Read the content of the destination file
                        with open(dest_item, 'rb') as f:
                            dest_content = f.read()

                        # If the content is different, update the destination file
                        if source_content != dest_content:
                            with open(dest_item, 'wb') as f:
                                f.write(source_content)
                    else:
                        # Create directories if they don't exist
                        if not os.path.exists(os.path.dirname(dest_item)):
                            os.makedirs(os.path.dirname(dest_item))
                        # Copy the file from source to destination
                        with open(dest_item, 'wb') as f:
                            f.write(source_content)

                    # Update the access and modification times of the file to the current timestamp
                    os.utime(dest_item, (timestamp.timestamp(), timestamp.timestamp()))

            # Perform the Google Drive backup
            if self.drive_service is not None:

                # Create a single backup folder in Google Drive
                file_metadata = {
                    "name": "Backup",
                    "mimeType": "application/vnd.google-apps.folder"
                }
                file = self.drive_service.files().create(body=file_metadata, fields="id").execute()
                drive_backup_folder_id = file.get('id')

                # Upload individual files to Google Drive
                for root, dirs, files in os.walk(local_backup_dir):
                    for file in files:
                        local_file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(local_file_path, local_backup_dir)
                        file_metadata = {
                            "name": relative_path,
                            "parents": [drive_backup_folder_id]
                        }

                        # Read the content of the local file
                        with open(local_file_path, 'rb') as f:
                            file_content = f.read()

                        # Check if the file already exists in Google Drive
                        results = self.drive_service.files().list(q=f"name='{relative_path}' and '{drive_backup_folder_id}' in parents",
                                                                    fields="files(id)").execute()
                        items = results.get('files', [])

                        if not items:
                            # If the file does not exist, create a new one
                            media = MediaFileUpload(local_file_path, chunksize=1024 * 1024, resumable=True)
                            request = self.drive_service.files().create(body=file_metadata, media_body=media)
                            response = None
                            while response is None:
                                status, response = request.next_chunk()
                                if status:
                                    print(f"Uploaded {int(status.progress() * 100)}%")
                        else:
                            # If the file exists, update its content
                            file_id = items[0]['id']
                            media = MediaFileUpload(local_file_path, chunksize=1024 * 1024, resumable=True)
                            request = self.drive_service.files().update(fileId=file_id, body=file_metadata, media_body=media)
                            response = None
                            while response is None:
                                status, response = request.next_chunk()
                                if status:
                                    print(f"Updated {int(status.progress() * 100)}%")

                self.status_label1.config(text="Local and Google Drive backups completed.")

                # Send email notification about the backup status
                self.send_email_notification(timestamp.strftime("%I-%M-%S %p"))
            else:
                self.status_label1.config(text="Local backup completed. Google Drive not configured.")

        except Exception as e:
            self.status_label1.config(text=f"Error: {str(e)}")

    def send_email_notification(self, backup_dir):
        sender_email = "bagwankamil8@gmail.com"
        sender_password = "cell tghz mjjn kvqn"
        recipient_email = "bagwankamil8@gmail.com"
        email_subject = "Backup Completed Status"
        email_body = f"The system backup has completed successfully at {backup_dir}."

        email_message = MIMEMultipart()
        email_message['From'] = sender_email
        email_message['To'] = recipient_email
        email_message['Subject'] = email_subject
        email_message.attach(MIMEText(email_body, 'plain'))

        try:
            email_server = smtplib.SMTP('smtp.gmail.com', 587)
            email_server.starttls()
            email_server.login(sender_email, sender_password)
            email_server.sendmail(sender_email, recipient_email, email_message.as_string())
            email_server.quit()

        except Exception as e:
            self.status_label1.config(text=f"Email notification error: {str(e)}", foreground="red")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1000x590")
        self.root.resizable(width=False, height=False)
        self.drive_service = None

        # Create a VideoBackground instance with your video file
        self.video_bg = VideoBackground(self.root, 'bg_video.mp4')

        self.create_login_widgets()

    def create_login_widgets(self):
        self.frame = customtkinter.CTkFrame(master=self.root, width=320, height=320, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.l2 = customtkinter.CTkLabel(master=self.frame, text="Log into your Account",
                                          font=('Century Gothic', 20, "bold"))
        self.l2.place(x=50, y=45)

        self.username_entry = customtkinter.CTkEntry(master=self.frame, width=220, placeholder_text='Username')
        self.username_entry.place(x=50, y=110)

        self.password_entry = customtkinter.CTkEntry(master=self.frame, width=220, placeholder_text='Password',
                                                      show="*")
        self.password_entry.place(x=50, y=165)

        self.button1 = customtkinter.CTkButton(master=self.frame, width=220, text="Login", command=self.check_login,
                                               corner_radius=6)
        self.button1.place(x=50, y=220)

        # Create a label for login status
        # Create a label for login status
        self.login_status_label = ttk.Label(master=self.frame, text="", foreground="red", background="#2b2b2b")
        self.login_status_label.place(x=60, y=265)

    def check_login(self):

        username = self.username_entry.get()
        password = self.password_entry.get()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            self.login_status_label.config(text="Invalid username format", foreground="red")
            return

        # Validate password length
        if len(password) < 8:
            self.login_status_label.config(text="Password must be 8 characters or more", foreground="red")
            return

        # Add your authentication logic here (e.g., check username and password)
        if username == "demo@gmail.com" and password == "12345678":
            # If the login is successful, configure Google Drive
            creds = None

            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())  # Refresh the token
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    creds = flow.run_local_server(port=0)

                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                self.drive_service = build("drive", "v3", credentials=creds)
            except HttpError as e:
                print("Error: " + str(e))

            self.root.destroy()
            root = tk.Tk()
            root = Backuproot(root, self.drive_service)
            root.mainloop()
        else:
            self.login_status_label.config(text="Invalid username or password", foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    login_window = LoginWindow(root)

    # Start playing the video in the background
    login_window.video_bg.play_video()

    root.mainloop()
