import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
import pygame
import os
import time
from tkinter import ttk
from random import randint

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("音乐播放器")
        self.root.geometry("500x570")
        self.paused = False
        self.current_song = ""
        self.full_paths = []
        self.current_mode = 0
        self.now = 0
        self.last_update_time = time.time()
        self.playback_modes = ["顺序播放", "随机播放", "单曲循环"]
        self.dragging_slider = False
        pygame.mixer.init()
        pygame.display.init()
        self.create_widgets()
        self.check_song_end()
        self.auto_import_music_files()
        self.dragging_slider = False
        self.update_slider()
        self.last_position = 0

    def create_widgets(self):
        self.status_bar = tk.Label(self.root, text="", bd=2, relief=tk.SUNKEN, anchor=tk.W)
        self.update_status_bar()

        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)

        playlist_frame = tk.Frame(self.root)
        playlist_frame.pack(pady=20)
        self.playlist_scrollbar = tk.Scrollbar(playlist_frame, orient="vertical")

        self.playlist = tk.Listbox(playlist_frame, bg="white", fg="black", width=60, selectbackground="gray",
                                   yscrollcommand=self.playlist_scrollbar.set)
        self.playlist.pack(side=tk.LEFT, fill=tk.BOTH)

        self.playlist_scrollbar.config(command=self.playlist.yview)
        self.playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        style = ttk.Style()
        style.configure('TButton', foreground='black', background='lightgray', font=('Arial', 10))
        style.map('TButton', foreground=[('active', 'black')], background=[('active', 'gray')])

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        button_frame_1 = tk.Frame(self.root)
        button_frame_1.pack()

        add_button = ttk.Button(button_frame_1, text="添加音乐", command=self.add_to_playlist)
        add_button.pack(side=tk.LEFT, padx=5)
        delete_button = ttk.Button(button_frame_1, text="删除选定音乐", command=self.delete_song)
        delete_button.pack(side=tk.LEFT, padx=5)

        button_frame_2 = tk.Frame(self.root)
        button_frame_2.pack()

        play_button = ttk.Button(button_frame_2, text="播放", command=self.play_music)
        play_button.pack(side=tk.LEFT, padx=5)
        pause_button = ttk.Button(button_frame_2, text="暂停", command=self.pause_music)
        pause_button.pack(side=tk.LEFT, padx=5)

        button_frame_3 = tk.Frame(self.root)
        button_frame_3.pack()

        previous_button = ttk.Button(button_frame_3, text="上一首", command=self.previous_song)
        previous_button.pack(side=tk.LEFT, padx=5)
        next_button = ttk.Button(button_frame_3, text="下一首", command=self.next_song)
        next_button.pack(side=tk.LEFT, padx=5)

        volume_frame = tk.Frame(self.root)
        volume_frame.pack(pady=5)

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        volume_label = tk.Label(volume_frame, text="音量:")
        volume_label.pack(side=tk.LEFT)

        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(50)
        pygame.mixer.music.set_volume(0.7)
        self.volume_slider.pack(pady=5, side=tk.LEFT)

        self.status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)

        self.song_position_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, length=400, command=self.set_song_position)
        self.song_position_slider.bind("<ButtonPress-1>", self.handle_slider_press)
        self.song_position_slider.bind("<ButtonRelease-1>", self.handle_slider_release)
        self.song_position_slider.pack(pady=5)

        self.current_time_label = tk.Label(self.root, text="当前时间: 00:00")
        self.current_time_label.pack()

        self.song_length_label = tk.Label(self.root, text="总时长: 00:00")
        self.song_length_label.pack()

        self.mode_button = ttk.Button(button_frame_3, text="切换模式", command=self.change_playback_mode)
        self.mode_button.pack(side=tk.LEFT, padx=5)

        self.custom_font = tkfont.Font(family="Georgia", size=12)

        self.extra_status_bar = tk.Label(self.root, text="这个世界不能没有音乐                           "
                                                         "                                          "
                                                         "zAone_", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                         font=self.custom_font)
        self.extra_status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.custom_font)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def auto_import_music_files(self):
        current_directory = os.getcwd()
        music_folder_path = os.path.join(current_directory, 'MusicTest')
        if os.path.exists(music_folder_path):
            music_files = os.listdir(music_folder_path)
            music_files = [file for file in music_files if file.endswith(('.mp3', '.wav'))]
            for file in music_files:
                self.playlist.insert(tk.END, os.path.basename(file))
                self.full_paths.append(os.path.join(music_folder_path, file))

    def get_song_length(self, song):
        try:
            audio = pygame.mixer.Sound(song)
            return audio.get_length()
        except pygame.error as e:
            messagebox.showerror("错误", f"获取音乐时长失败: {e}")
            return 0

    def update_music_length(self):
        song_length = self.get_song_length(self.current_song)
        self.song_position_slider.config(to=song_length)
        minutes, seconds = divmod(song_length, 60)
        self.song_length_label.config(text=f"总时长: {int(minutes):02d}:{int(seconds):02d}")

    def play_music(self, event=None):
        self.last_update_time = time.time()

        if self.paused:
            pygame.mixer.music.unpause()
            self.status_bar.config(text="音乐继续播放")
            self.paused = False
            self.update_slider()
        else:
            try:
                index = self.playlist.curselection()[0]
                self.current_song = self.full_paths[index]
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play(loops=0)
                self.status_bar.config(text=f"正在播放： {os.path.basename(self.current_song)}")
                self.last_position = 0
                self.song_position_slider.set(0)
                self.current_time_label.config(text="当前时间: 00:00")
                self.now = 0
                self.update_music_length()
                self.update_slider()
                self.update_status_bar()
            except IndexError:
                messagebox.showerror("错误", "请选择要播放的音乐！")
            except pygame.error as e:
                messagebox.showerror("错误", f"无法播放音乐: {e}")

    def add_to_playlist(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        for file in files:
            self.playlist.insert(tk.END, os.path.basename(file))
            self.full_paths.append(file)

    def set_song_position(self, val):
        if not self.dragging_slider:
            position = int(val)
            self.song_position_slider.set(position)

    def handle_slider_press(self, event):
        self.dragging_slider = True

    def update_slider(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            current_time = time.time()
            time_difference = current_time - self.last_update_time

            if time_difference >= 1:
                self.now += int(time_difference)
                self.last_update_time = current_time
            if not self.dragging_slider:
                if self.last_position == 0 :
                    current_position = self.now
                else:
                    current_position = self.last_position + self.now
                self.song_position_slider.set(current_position)
                minutes, seconds = divmod(current_position, 60)
                minutes = round(minutes)
                seconds = round(seconds)
                self.current_time_label.config(text=f"当前时间: {minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_slider)

    def handle_slider_release(self, event):
        position = self.song_position_slider.get()
        pygame.mixer.music.set_pos(position)
        self.last_position = position
        self.dragging_slider = False
        self.now = 0
        self.update_slider()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.last_position = 0
        self.song_position_slider.set(0)
        self.current_time_label.config(text="当前时间: 00:00")
        self.status_bar.config(text="音乐已停止")

    def pause_music(self):
        self.paused = True
        pygame.mixer.music.pause()
        self.status_bar.config(text="音乐已暂停")

    def set_volume(self, val):
        volume = int(val) / 100
        pygame.mixer.music.set_volume(volume)

    def delete_song(self):
        selected_song = self.playlist.curselection()
        if selected_song:
            for index_1, song_path in enumerate(self.full_paths):
                if pygame.mixer.music.get_busy() and song_path == self.current_song:
                    if index_1 == selected_song[0]:
                        self.stop_music()
            index = selected_song[0]
            self.playlist.delete(index)
            self.full_paths.pop(index)
            if self.current_song and index < len(self.full_paths):
                self.current_song = self.full_paths[index]

    def play_specific_song(self, index):
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(index)
        self.playlist.activate(index)
        self.current_song = self.full_paths[index]
        if self.paused:
            self.paused = False
        self.play_music()

    def previous_song(self):
        current_selection = self.playlist.curselection()
        if current_selection:
            current_index = current_selection[0]
        else:
            return

        if self.current_mode == 0:
            current_index -= 1
            if current_index >= 0:
                self.play_specific_song(current_index)

        elif self.current_mode == 1:
            current_index = randint(0, self.playlist.size() - 1)
            self.play_specific_song(current_index)

        elif self.current_mode == 2:
            self.play_specific_song(current_index)

        self.last_position = 0
        self.song_position_slider.set(0)
        self.current_time_label.config(text="当前时间: 00:00")

    def next_song(self):
        current_selection = self.playlist.curselection()
        if current_selection:
            current_index = current_selection[0]
        else:
            return

        if self.current_mode == 0:
            current_index += 1
            if current_index < self.playlist.size():
                self.play_specific_song(current_index)

        elif self.current_mode == 1:
            current_index = randint(0, self.playlist.size() - 1)
            self.play_specific_song(current_index)

        elif self.current_mode == 2:
            self.play_specific_song(current_index)

        self.last_position = 0
        self.song_position_slider.set(0)
        self.current_time_label.config(text="当前时间: 00:00")

    def change_playback_mode(self):
        self.current_mode = (self.current_mode + 1) % len(self.playback_modes)
        self.update_status_bar()

    def update_status_bar(self):
        mode_text = f"当前模式: {self.playback_modes[self.current_mode]}"
        song_text = f"当前音乐: {os.path.basename(self.current_song)}" if self.current_song else ""
        self.status_bar.config(text=mode_text + "\n" + song_text, justify=tk.LEFT)

    def check_song_end(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.last_position = 0
                self.song_position_slider.set(0)
                self.current_time_label.config(text="当前时间: 00:00")

            self.next_song()

        self.root.after(100, self.check_song_end)

def main():
    root = tk.Tk()
    music_player = MusicPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
