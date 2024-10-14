import customtkinter as ctk
from customtkinter import filedialog, CTkCanvas, CTkEntry, CTkLabel, CTkButton, CTkCheckBox, CTkScrollableFrame, CTkImage, CTkFrame
from tkinter import PhotoImage, messagebox
import yt_dlp
from youtubesearchpython import VideosSearch
from PIL import Image, ImageTk  
import requests
from io import BytesIO
import os
import threading




def main_function():
    global path_entry, url_entry, root, image_references, image_scroll, audio_only, anchor_default

    width = 1440
    height = 810
    anchor_default = 'center'
    label_color = 'transparent'
    image_references = []

    # Set up main window
    root = ctk.CTk()
    root.title('YouTube Video Installer')
    root.geometry(f'{width}x{height}')
    root.configure(fg_color='#252525')
    root.resizable(False, False)
    root._set_appearance_mode('dark')

    

    # Scaling based on screen width
    window_scaling_factor = 1.0
    widget_scaling_factor = 1.0

    if root.winfo_screenwidth() <= 1280:
        window_scaling_factor = 0.65
        widget_scaling_factor = 0.7
    elif root.winfo_screenwidth() <= 1440:
        window_scaling_factor = 0.75
        widget_scaling_factor = 0.8
    elif root.winfo_screenwidth() >= 1920:
        window_scaling_factor = 1
        widget_scaling_factor = 1

    ctk.set_window_scaling(window_scaling_factor)
    ctk.set_widget_scaling(widget_scaling_factor)

    
    gradient_canvas = ctk.CTkCanvas(root, width=width, height=height, highlightthickness=0)
    gradient_canvas.place(x=0, y=0)
    
    draw_gradient(gradient_canvas, width, height)

    image_scroll = CTkScrollableFrame(root, width=1000, height=height - 55, label_text='Video Results', label_font=ctk.CTkFont(size=15),
    corner_radius=8, bg_color= '#0F0F0F', fg_color='#0F0F0F', 
    scrollbar_fg_color='#000102', scrollbar_button_color='#7400ff', scrollbar_button_hover_color= '#3e0088')
    image_scroll.grid(row = 0, column = 0)




    # Split white line
    white_line = CTkCanvas(root, width=2, height=height,bg ='#252525', highlightthickness=0)
    white_line.place(anchor=anchor_default, x=width // 1.4, y=height // 2)
    white_line.create_line(width // 2, 0, width // 2, height, fill='#000102', width=3.2)


    # Welcome message
    welcome_text = CTkLabel(root, text='Welcome to YouTube Video Installer', bg_color = '#010407' ,
                            text_color='white', font=ctk.CTkFont(size=18, weight="bold"))
    welcome_text.place(anchor=anchor_default, x=1215, y=45)

    # Path entry and label
    path_entry = CTkEntry(root, width=300, font=('arial', 12), corner_radius=10,
                          bg_color= '#010508')
    path_entry.place(anchor=anchor_default, x=1203, y=145)
    check_default_path()

    path_text = CTkLabel(root, text='Enter or browse the Download location:',
                         text_color='white', font=ctk.CTkFont(size=15, weight="bold") , bg_color= '#02060b')
    path_text.place(anchor=anchor_default, x=1205, y=115)

    # Set up as default button
    set_as_default_button = CTkButton(root, text='Set path as default', width=180, command=set_as_default,
                                      corner_radius=10, font=ctk.CTkFont(size=15))
    set_as_default_button.place(anchor=anchor_default, x=1225, y=185)

    # Set up URL entry with label
    url_entry = CTkEntry(root, width=300, font=('arial', 12), corner_radius=10,
                         bg_color= '#02080d')
    url_entry.place(anchor=anchor_default, x=1203, y=255)
    url_entry.bind('<Return>', search_video)

    url_text = CTkLabel(root, text='Enter the search query:',
                        text_color='white', font=ctk.CTkFont(size=15, weight="bold"), bg_color= '#02080e')
    url_text.place(anchor=anchor_default, x=1145, y=225)

    # Set up Paste button
    search_button = CTkButton(root, text='Search video', width=180, command=search_threaded, corner_radius=10,
                             font=ctk.CTkFont(size=15))
    search_button.place(anchor=anchor_default, x=1225, y=295 )

    # Browse Button with icon import (keep reference to the icon)
    icon = PhotoImage(file=r'icons8-file-explorer-24.png')
    browse_button = CTkButton(root, image=icon, command=browse_button_clicked, text=None,
                              width=12, height=12, corner_radius=10)
    browse_button.place(anchor=anchor_default, x=1384, y=145)

    # Audio only download check box
    audio_only = ctk.BooleanVar(value=False)
    audio_only_checkbox = CTkCheckBox(root, text='Audio only', corner_radius=20, 
                                      bg_color= '#061422', variable=audio_only)
    audio_only_checkbox.place(anchor=anchor_default, x=1225, y=340)
    


    root.mainloop()


def draw_gradient(canvas, width, height):
    for i in range(height):
        # Calculate gradient color for a smoother transition
        r = int(0 + (10) * (i / height))
        g = int(0 + (30) * (i / height))
        b = int(0 + (50) * (i / height))
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Draw horizontal lines to create a gr adient effect
        canvas.create_line(0, i, width, i, fill=hex_color)


# All functions
def browse_button_clicked():
    file_chosen = filedialog.askdirectory(title='Choose folder')
    path_entry.delete(0, ctk.END)
    path_entry.insert(index=0, string=file_chosen)


def set_as_default():
    default_path = path_entry.get()
    if not default_path:
        messagebox.showwarning('Path error', 'You need to type a path to set it as default')
    else:
        if not default_path.endswith(os.sep):
            default_path += os.sep
        try:
            with open("download_path.txt", 'w') as file_path:
                file_path.write(default_path)
        except Exception as err:
            messagebox.showwarning('default_path error', message = err)


def check_default_path():
    with open('download_path.txt', 'r') as default_path:
        default_path_content = default_path.read()
    if default_path_content:
        path_entry.delete(0, ctk.END)
        path_entry.insert(0, default_path_content)


def search_threaded():
    search_threading = threading.Thread(target=search_video())
    search_threading.start

def search_video(*args):
    global results, Limit

    Title = url_entry.get()
    if not Title:
        messagebox.showerror('Search error', 'Enter a search query')
    else:
        Limit = 20

        youtube_search = VideosSearch(Title, Limit)
        results = youtube_search.result()['result']
        display_threading()


def display_threading():
    display_threaded = threading.Thread(target=display_videos)
    display_threaded.start()



def display_videos():
    global frame_video, all_video_link, download_button

    if not results:
        messagebox.showerror('Search error', 'Nothing found')
        return None
        

    icon = PhotoImage(file=r'Download_icon.png')
    video_count = 1
    all_video_links = {}
    for index, video in enumerate(results, start=1):
            
        video_Title = video['title']
        if len(video_Title) > 58:
            video_Title = video_Title[:58] + '...'
        video_Link = video['link']

        Duration = video['duration']
        publishedTime = video['publishedTime']
        viewCount = video['viewCount']
        short_views = viewCount['short']
        
        total_columns = Limit

        # Get thumbnail image
        image_url = video_Link.split('=')[-1]
        high_quality_thumbnail = f'https://img.youtube.com/vi/{image_url}/maxresdefault.jpg'
        try:
            image_response = requests.get(high_quality_thumbnail)
            image_response.raise_for_status()  
        except: Exception

        image_data = image_response.content
        
        image = Image.open(BytesIO(image_data))
        image = image.resize((1280, 720))
        ctk_image = CTkImage(light_image=image, size = (320, 180))



        image_references.append(ctk_image)

        frame_video = CTkFrame(image_scroll, width = 1000  , height = 225 , 
                    corner_radius = 15, border_width = 1, border_color = '#00d8ff', bg_color = '#252525')

        # Set up video frame
        
        frame_video.grid(stick = 'nw', row = index, column = 0, pady = (45, 15),
                            columnspan = total_columns)
        frame_video.grid_propagate(False)


        # Show Thumbnail

        image_label = CTkLabel(frame_video, image = ctk_image, text = None, width = 125,
                                corner_radius = 25)
        image_label.grid(row = 0, column = 0, padx = (30, 10), pady = (20, 25), sticky = 'w')
        image_label.lift()
        # Show video Title

        video_title_label = CTkLabel(frame_video, text=video_Title, font=ctk.CTkFont(size=20), text_color="#FFFFFF")
        video_title_label.grid(row=0, column=1, padx=(25, 5), pady=(5,125), sticky='w')

        # Show duration 

        duration_label = CTkLabel(frame_video, text = f"Duration: {Duration}",
                                   font = ctk.CTkFont(size=18), text_color="#008080")
        duration_label.grid(row = 0, column = 1, padx = (25, 10), pady = (50, 10), sticky = 'w')

        # show video date

        date_label = CTkLabel(frame_video, text = f"View count: {short_views}",
                               font = ctk.CTkFont(size=18), text_color="#008080")
        date_label.grid(row = 0, column = 1, padx = (25, 10), pady = (90, 10), sticky = 'w')

        # make download button

        download_button = CTkButton(frame_video, image=icon, 
                                    command=lambda v_link=video_Link: download_video_threaded(v_link),
                                    text=None,
                                width=24, height=24, corner_radius=10,)
        download_button.grid(row = 0, column = 1, padx = (500, 10), pady = (70, 10), sticky = 'w')

        video_count += 1
        all_video_links.update({video_count:video_Link})


def download_video_threaded(video_link):
    download = threading.Thread(target = download_video, args = (video_link,))
    download.start()
    return None


def download_video(video_link):
    audio_check = audio_only.get()
    download_location = path_entry.get()
    

    if not download_location:
        messagebox.showerror('Download error', 'Please specify a download location.')
        return

    ydl_opts = {
        'outtmpl': f'{download_location}/%(title)s.%(ext)s',
    }

    if audio_check:
        ydl_opts['format'] = 'bestaudio[ext=m4a]'  # Fixed to download audio only
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]'  # Download video

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_link])
        messagebox.showinfo("Download Complete", f"Downloaded: {video_link}")
    except Exception as e:
        messagebox.showerror('Download error', 'something went wrong')
    return None

if __name__ == '__main__':
    main_function()