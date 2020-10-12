from tkinter import *
from tkinter import messagebox, filedialog, ttk
import shutil
from pytube import *
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
import os


class Application:
    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.quality=''
        self.UI()

    def UI(self):
        self.root = Tk()
        self.root.title = "Youtube Video Downloader"

        self.canvas = Canvas(self.root, width=600, height=400)
        self.canvas.configure(bg="#02d0fc")
        self.canvas.pack()

        self.lbl1 = Label(self.root, text="Download Youtube Videos or Playlist", fg="#020024", bg="#02d0fc")
        self.lbl1.configure(font=("Times", 18, "bold"))
        self.canvas.create_window(295, 20, window=self.lbl1)

        self.entry = Entry(self.root, width=50)
        self.canvas.create_window(295, 70, window=self.entry)

        self.lbl2 = Label(self.root, text="Enter the Video/Playlist Link", fg="#020024", bg="#02d0fc")
        self.canvas.create_window(295, 105, window=self.lbl2)

        self.type = StringVar(self.root, "Video")

        self.radio1 = Radiobutton(self.root, text="Playlist", variable=self.type, value="Playlist", padx=20, fg="#020024",
                                  bg="#02d0fc")
        self.canvas.create_window(370, 200, window=self.radio1)

        self.radio2 = Radiobutton(self.root, text="Video", variable=self.type, value="Video", padx=20, fg="#020024",
                                  bg="#02d0fc")
        self.canvas.create_window(220, 200, window=self.radio2)

        self.download_btn = Button(self.root, text="Download video!", command=self.download_btn)
        self.canvas.create_window(370, 300, window=self.download_btn)

        self.video_quality_btn = Button(self.root, text="Select Video Quality!", command=self.video_quality_btn_clicked)
        self.canvas.create_window(220, 300, window=self.video_quality_btn)

        self.photo = PhotoImage(file="browse-folder.png")
        self.photoimage = self.photo.subsample(5, 5)
        self.sel_dir = Button(self.root, command=self.select_folder, image=self.photoimage)
        self.canvas.create_window(560, 70, window=self.sel_dir)

        self.root.mainloop()
    def select_folder(self):
        self.directory = filedialog.askdirectory(parent=self.root, initialdir=self.directory)
        # self.entry.insert(0,directory)

    def getLink(self):
        self.link = self.entry.get()

        if len(self.link) == 0 :
            messagebox.showinfo("Error!", "Please provide video link :")
            return False
        else:
            print("got link")
            return True

    def get_video_list(self,):
        # extract playlist id from url
        url = self.link
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        print("get all playlist items links from {}".format(playlist_id))
        youtube = googleapiclient.discovery.build("youtube", "v3",
                                                  developerKey="Paste_your_devloper_key_here")

        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)
        playlist_videos = []
        for i in playlist_items:
            temp="https://www.youtube.com/watch?v="+i["snippet"]["resourceId"]["videoId"]+"&list="+playlist_id+"&t=0s"
            playlist_videos.append(temp)

        return playlist_videos

    def download_btn(self):
        if self.quality == '':
            messagebox.showinfo("Error!","Select Video Quality first :")
        else:
            if self.type.get() == "Video":
                self.video = self.yt.streams.filter(progressive=False, resolution=self.quality).first()
                self.progress_bar_UI()
                self.video.download(output_path=self.directory)
                self.downloaded()
            else:
                self.videos = self.get_video_list()
                for items in self.videos:
                    print("selcting",items)
                    count = 1
                    done = True
                    while(count<=5):
                        try:
                            self.select_video(items)
                        except:
                            print("Error for",items)
                            done = False
                        else:
                            done = True
                        count+=1
                        if done:
                            break
                    if done:
                        print("done")
                    else:
                        print("video not downloaded :",items)
                    self.yt.streams.filter(progressive=False, resolution=self.quality).first().download(
                        output_path=self.directory)
    def downloaded(self):
        dwn_msg = "Download Finished \n Folder : {}".format(self.directory)
        messagebox.showinfo("Download Succesful",dwn_msg)
        self.root3.destroy()

    def select_qualties(self):
        self.quality = self.combo_box.get()
        self.root2.destroy()
        if self.type.get() == "Video":
            self.getdetails()
            self.show_details()

    def small_UI(self):
        self.root2 = Tk()
        self.canvas2 = Canvas(self.root2, width=150, height=200)
        self.canvas2.configure(bg="#02d0fc")
        self.canvas2.pack()

        self.combo_box = ttk.Combobox(self.root2, width=15, textvariable=StringVar)
        if self.type.get() == "Video":
            self.combo_box['values'] = self.qualities_list
        else:
            self.combo_box['values'] = ('720p','360p','144p')
        self.combo_box.set('720p')
        self.canvas2.create_window(75, 10, window=self.combo_box)

        self.btt = Button(self.root2, text="Click", command=self.select_qualties)
        self.canvas2.create_window(75, 185, window=self.btt)
        self.root2.mainloop()
    def show_details(self):
        self.msg = ""
        for item in self.details:
            self.msg += "{} : {} \n ".format(item, self.details[item])
        messagebox.showinfo("Video Details :", self.msg)
    def progress_bar_UI(self):
        self.root3 = Tk()
        self.canvas3 = Canvas(self.root3, width=300, height=150)
        self.canvas3.configure(bg="#02d0fc")
        self.canvas3.pack()
        self.progressbar = ttk.Progressbar(self.root3, orient=HORIZONTAL, length=250, mode='determinate')
        self.canvas3.create_window(150, 75, window=self.progressbar)

    def progress_fun(self, stream, chunk, bytes_remaining):
        self.progressbar['value'] = ((self.video.filesize - bytes_remaining)//self.video.filesize) * 100

    def select_video(self,vid_link):
        self.yt = YouTube(vid_link,on_progress_callback=self.progress_fun)
        print("done")

    def availabe_qualities(self):
        quality=[]
        if self.yt.streams.filter(progressive=False,resolution="1080p"):
            quality.append("1080p")
        if self.yt.streams.filter(progressive=False,resolution="720p"):
            quality.append("720p")
        if self.yt.streams.filter(progressive=False,resolution="480p"):
            quality.append("480p")
        if self.yt.streams.filter(progressive=False,resolution="360p"):
            quality.append("360p")
        if self.yt.streams.filter(progressive=False,resolution="240p"):
            quality.append("240p")
        if self.yt.streams.filter(progressive=False,resolution="144p"):
            quality.append("144p")

        return tuple(quality)
    def getdetails(self):
        l=self.yt.length
        length="{} : {} : {}".format(l//(60*60),(l%60)//60,l%60)
        self.details = {"title": self.yt.title, "author": self.yt.author, "length": length, "rating": self.yt.rating,
                        "views": self.yt.views}
    def video_quality_btn_clicked(self):
        if self.getLink():
            if self.type.get() == "Video":
                print("inside")
                try:
                    self.select_video(self.link)
                except:
                    messagebox.showinfo("Error!","Enter Valid link")
                else:
                    self.qualities_list = self.availabe_qualities()
                    self.small_UI()

            else:
                self.small_UI()

obj=Application()

