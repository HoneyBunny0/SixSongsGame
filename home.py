from __future__ import unicode_literals
import re, requests, urllib.parse, urllib.request
from bs4 import BeautifulSoup
from pytube import YouTube
import streamlit as st
import glob
import re
from pathlib import Path
import os
from subprocess import Popen, PIPE
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import random

st.set_page_config(
    layout="wide",
    page_title="Six Songs Game",
    page_icon="https://png.pngtree.com/png-vector/20190411/ourmid/pngtree-vector-music-notes-icon-png-image_925660.jpg",
)


def get_song(music_name: str):
    query_string = urllib.parse.urlencode({"search_query": music_name})
    formatUrl = urllib.request.urlopen(
        "https://www.youtube.com/results?" + query_string
    )

    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
    clip = requests.get(
        "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
    )
    song_path = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

    inspect = BeautifulSoup(clip.content, "html.parser")
    yt_title = inspect.find_all("meta", property="og:title")

    for concatMusic1 in yt_title:
        pass

    song_name = concatMusic1["content"]
    return song_path, song_name


def download_song(song_path: str) -> str:
    with st.spinner("Downloading"):
        return (
            YouTube(song_path)
            .streams.filter(only_audio=True)
            .first()
            .download(output_path=f"songs/")
        )


def trim_song(song_path: str) -> str:
    start_time = 0
    end_time = 100
    ffmpeg_extract_subclip("video1.mp4", start_time, end_time, targetname="test.mp4")


def play_audio(song_path: str):
    audio_file = open(song_path, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp4")


basename = lambda path: Path(path).stem

st.title("Six Songs Game")

with st.expander("Song Fetcher"):
    path, name = "", ""
    col1, col2 = st.columns(2)
    with col1:
        song_query = st.text_input(label="1.", label_visibility="collapsed")
    with col2:
        if song_query:
            path, name = get_song(song_query)
            st.write(name)
    if st.button("Download"):
        if path:
            download_song(path)

songs_available = glob.glob("songs/*")

songs, checkboxes = [], []
for i in range(6):
    col1, col2 = st.columns(2)
    with col1:
        song = st.selectbox(f"Song {i}", songs_available, format_func=basename)
        songs.append(song)
    with col2:
        checkbox = st.checkbox(f"chk {i}", value=True, label_visibility="collapsed")
        checkboxes.append(checkbox)

output_path = "output.mp4"
if st.button("Combination"):
    if os.path.exists(output_path):
        os.remove(output_path)
    command = [
        "ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
        *sum(
            [["-ss", "30", "-i", s] for i, s in enumerate(songs) if checkboxes[i]], []
        ),
        "-filter_complex",
        "".join([f"[{i}:a:0]" for i in range(sum(checkboxes))])
        + f"amix=inputs={sum(checkboxes)}:duration=shortest[aout]",
        "-map",
        "[aout]",
        "-t",
        "45",
        output_path,
    ]
    st.info(command)
    process = Popen(command)
    with st.spinner("Combinating"):
        process.wait()
    play_audio(output_path)
