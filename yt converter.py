import threading
import os
import pytube as yt
import tkinter as tk
import tkinter.ttk as ttk
import multiprocessing

# Variables
font = "Comic Sans MS"
fontSizeN = 20
fontSizeS = 14
fontSizeH = 25

color_background = "#303030"
color_button = "#505050"
color_listbox = "#808080"
color_true = "#006600"
color_false = "#660000"
color_transparent = "#E0E0E0"
color_black = "#000000"

url = ""
url_info = 0
id_one_video = 1
format = "mp3"
path_downloads = os.path.expanduser("~") + "\\downloads\\"
current_rows = 2

thread_list = []
kill_thread_list = []

# Frame
root: tk.Tk = None
button_download: tk.Button = None
entry: tk.Entry = None
listbox: tk.Listbox = None
button_format: tk.Button = None
gui_setting: "gui_settings" = None


class gui_settings:
    combobox_value_audio = ["mp3 (recommended)", "wav (recommended)", "3gp",
                            "8svx", "aa", "aac", "aax", "act", "aiff", "alac",
                            "amr", "ape", "au", "awb", "cda", "dss", "dvf",
                            "flac", "gsm", "iklax", "ivs", "m4a", "m4b",
                            "m4b", "mmf", "mpc", "msv", "nmf", "ogg", "oga",
                            "mogg", "opus", "ra", "rm", "raw", "rf64", "sln",
                            "tta", "voc", "vox", "wma", "wv", "webm"]
    combobox_value_video = ["mp4 (recommended)", "3g2", "3gb", "amv", "asf",
                            "avi", "drc", "flv", "f4v", "f4p", "f4a", "f4b",
                            "gif", "gifv", "m4v", "mkv", "mng", "mov", "qt",
                            "m4p", "m4v", "mpg", "mp2", "mpeg", "mpe", "mpv",
                            "mpg", "mpeg", "m2v", "MTS", "m2TS", "TS", "mxf",
                            "nsv", "ogv", "ogg", "rm", "rm", "rmvb", "roq",
                            "svi", "viv", "vob", "webm", "wmv", "yuv"]

    def __init__(self, is_visible: bool):
        self.label_settings = tk.Label(root, text="Settings ⚙",
                                       font=(font, fontSizeN),
                                       background=color_background)

        self.combobox_format_style = ttk.Style()
        print(self.combobox_format_style.theme_names())
        self.combobox_format_style.theme_use("clam")
        self.combobox_format_style.configure("TCombobox",
                                             background=color_button,
                                             foreground=color_black,
                                             fieldbackground=color_listbox,
                                             lightcolor=color_button)
        self.combobox_format = ttk.Combobox(root,
                                            values=self.combobox_value_audio,
                                            style="TCombobox")
        self.combobox_format.option_add("*TCombobox*Listbox*Background",
                                        color_listbox)
        self.combobox_format.set(value=self.combobox_value_audio[0])

        if is_visible:
            self.set_visible()
        else:
            self.set_unvisible()

    def set_visible(self):
        self.label_settings.grid(row=0, column=3)
        self.combobox_format.grid(row=1, column=3)

    def set_unvisible(self):
        self.label_settings.grid_forget()
        self.combobox_format.grid_forget()

    def set_combobox_value_audio(self):
        self.combobox_format["value"] = self.combobox_value_audio
        self.combobox_format.set(self.combobox_value_audio[0])

    def set_combobox_value_video(self):
        self.combobox_format["value"] = self.combobox_value_video
        self.combobox_format.set(self.combobox_value_video[0])

    def get_current_format(self) -> str:
        current_format = self.combobox_format.get()
        current_format = current_format.replace("♫", "")
        current_format = current_format.replace("▶", "")
        current_format = current_format.replace(" ", "")
        current_format = current_format.replace("(recommended)", "")
        return current_format


def download(video, path_download: str, is_audio: bool, format: str) -> tuple:
    if is_audio:
        video = video.streams.filter(only_audio=True).first()
        format_download = ".mp3"
    else:
        video = video.streams.get_highest_resolution()
        format_download = ".mp4"
    video.download(output_path=path_download, filename=replace_illegal_names(
        video.title) + "_downloaded_formating" + format_download)
    listbox_append("downloaded")
    source = path_download + replace_illegal_names(video.title) \
             + "_downloaded_formating" + format_download
    target = path_download + replace_illegal_names(video.title) + "." + format
    listbox_append("Formating..." + source)
    p = multiprocessing.Process(daemon=True,
                                target=format_video,
                                args=[source, target])
    p.start()
    return p, target


def format_video(source: str, target: str):
    os.system(f"ffmpeg -i \"{source}\" \"{target}\"")
    os.remove(source)


def download_one_mp3():
    print(url)
    video = yt.YouTube(url=url)
    graphics = new_praefix_label_progressbar_button(name=video.title,
                                                    new_progressbar=False,
                                                    präfix="♫")
    p, target = download(video=video,
                         path_download=path_downloads,
                         is_audio=True,
                         format=gui_setting.get_current_format())
    p.join()
    listbox_append(f"Formated: {target}")
    for graphic in graphics:
        graphic.destroy()


def download_one_mp4():
    video = yt.YouTube(url=url)
    graphics = new_praefix_label_progressbar_button(name=video.title,
                                                    new_progressbar=False,
                                                    präfix="▶")
    p, target = download(video=video,
                         path_download=path_downloads,
                         is_audio=False,
                         format=gui_setting.get_current_format())
    p.join()
    listbox_append(f"Formated: {target}")
    for graphic in graphics:
        graphic.destroy()


def download_playlist_mp3():
    playlist = yt.Playlist(url=url)
    path_playlist = path_downloads + replace_illegal_names(
        playlist.title) + "\\"
    graphics = new_praefix_label_progressbar_button(name=playlist.title,
                                                    new_progressbar=True,
                                                    präfix="♫",
                                                    maximum=playlist.length)
    procs = []
    for url_video in playlist:
        procs.append(download(video=yt.YouTube(url=url_video),
                              path_download=path_playlist,
                              is_audio=True,
                              format="mp3"))
        graphics[2]["value"] += 1
        if kill_thread_list[int((graphics[0].grid_info()["row"] + 1) / 2) - 2]:
            break
    for p, target in procs:
        p.join()
        listbox_append(f"Formated: {target}")
    for graphic in graphics:
        graphic.destroy()


def download_playlist_mp4():
    playlist = yt.Playlist(url=url)
    path_playlist = path_downloads + replace_illegal_names(
        playlist.title) + "\\"
    graphics = new_praefix_label_progressbar_button(name=playlist.title,
                                                    new_progressbar=True,
                                                    präfix="▶",
                                                    maximum=playlist.length)
    procs = []
    for url_video in playlist:
        procs.append(download(video=yt.YouTube(url=url_video),
                              path_download=path_playlist,
                              is_audio=False,
                              format="mp4"))
        graphics[2]["value"] += 1
        if kill_thread_list[int((graphics[0].grid_info()["row"] + 1) / 2) - 2]:
            break
    for p, target in procs:
        p.join()
        listbox_append(f"Formated: {target}")
    for graphic in graphics:
        graphic.destroy()


def new_praefix_label_progressbar_button(name: str, new_progressbar: bool,
                                         präfix: str, maximum=0):
    global current_rows
    current_rows += 2
    kill_thread_list.append(False)
    praefix_label = tk.Label(root, text=präfix, font=(font, fontSizeN),
                             bg=color_background)
    praefix_label.grid(row=current_rows - 1, column=0, padx=10)
    label = tk.Label(root, text=name, font=(font, fontSizeN),
                     bg=color_background)
    label.grid(row=current_rows - 1, column=1, padx=10)
    if new_progressbar:
        button = tk.Button(root, text="⌫", font=(font, fontSizeH),
                           bg=color_button, command=lambda: break_download(
                int(label.grid_info()["row"] + 1), progressbar=progressbar))
        button.grid(row=current_rows - 1, column=2, rowspan=2, sticky="nesw",
                    padx=(0, 10))
        style = ttk.Style()
        style.theme_use("alt")
        style.configure("Horizontal.TProgressbar",
                        troughcolor=color_background, background=color_listbox)
        progressbar = ttk.Progressbar(root, style="Horizontal.TProgressbar",
                                      maximum=maximum)
        progressbar.grid(row=current_rows, column=0, columnspan=2,
                         sticky="nesw", padx=10)
        return [praefix_label, label, progressbar, button]
    return [praefix_label, label]


def break_download(row: int, progressbar):
    style = ttk.Style()
    style.theme_use("alt")
    style.configure("red.Horizontal.TProgressbar", foreground=color_background,
                    background=color_false)
    progressbar.config(style="red.Horizontal.TProgressbar")
    kill_thread_list[int((row / 2) - 2)] = True


def listbox_append(msg: str):
    listbox.insert("end", msg)
    listbox.see("end")


def button_download_clicked():
    if url_info != 0:
        if format == "mp3":
            download_one_mp3() if url_info == id_one_video else download_playlist_mp3()
        elif format == "mp4":
            download_one_mp4() if url_info == id_one_video else download_playlist_mp4()


def check_url(event):
    global url_info, url
    url = entry.get()
    try:
        yt.Playlist(url=url).title
        url_info = 2
    except KeyError:
        try:
            yt.YouTube(url=url).title
            url_info = 1
        except yt.exceptions.RegexMatchError:
            url_info = 0
    if url_info == 0:
        button_download.config(bg=color_false)
    else:
        button_download.config(bg=color_true)


def change_format():
    global format
    if format == "mp3":
        format = "mp4"
        button_format.config(text="▶")
        gui_setting.set_combobox_value_video()
    else:
        format = "mp3"
        button_format.config(text="♫")
        gui_setting.set_combobox_value_audio()


def new_thread():
    if url_info != 0:
        listbox_append(msg="start new thread...")
        thread_list.append(
            threading.Thread(target=button_download_clicked, daemon=True))
        thread_list[-1].start()
        listbox_append(msg="thread started")
    else:
        listbox_append(msg="Video not found!")
        print(gui_setting.combobox_format["value"])


def replace_illegal_names(string: str) -> str:
    string = string.replace("\\", "")
    string = string.replace("/", "")
    string = string.replace(":", "")
    string = string.replace("*", "")
    string = string.replace("?", "")
    string = string.replace("\"", "")
    string = string.replace("<", "")
    string = string.replace(">", "")
    string = string.replace("|", "")
    return string


def main():
    global root, button_download, entry, listbox, button_format, gui_setting
    # Frame
    root = tk.Tk()
    root.config(bg=color_background)
    root.wm_attributes("-transparentcolor", color_transparent)
    root.title("Youtube Downloader ⤓   © Theo Tappe")

    tk.Label(root, text="Youtube Downloader ⤓   © Theo Tappe",
             font=(font, fontSizeH), bg=color_background).grid(row=0, column=0,
                                                               columnspan=2,
                                                               pady=20)

    entry = tk.Entry(root, font=(font, fontSizeS), bg=color_listbox)
    entry.grid(row=1, column=0, columnspan=2, sticky="nesw", padx=10)
    entry.bind("<KeyRelease>", check_url)

    button_download = tk.Button(root, text="⤓", font=(font, fontSizeH),
                                bg=color_false, command=new_thread)
    button_download.grid(row=1, column=2, sticky="nesw", padx=(0, 10))

    listbox = tk.Listbox(root, font=(font, fontSizeS), width=55,
                         bg=color_listbox)
    listbox.grid(row=2, column=0, columnspan=2, sticky="nesw", pady=10,
                 padx=10)

    button_format = tk.Button(root, text="♫", font=(font, fontSizeH),
                              bg=color_button, width=5, command=change_format)
    button_format.grid(row=2, column=2, sticky="nesw", pady=10, padx=(0, 10))

    root.wm_resizable(width=False, height=False)

    gui_setting = gui_settings(is_visible=True)

    root.mainloop()


if __name__ == "__main__":
    main()
