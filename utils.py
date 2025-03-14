from pytubefix import YouTube
import ffmpeg
import requests
from PIL import Image
from io import BytesIO


def GetStreams(URL, only_audio):
    yt = YouTube(URL)
    try:
        streams = yt.streams.filter(only_audio=only_audio)
        thumb = None
        r = requests.get(yt.thumbnail_url)
        if r.status_code == 200:
            thumb = Image.open(BytesIO(r.content))
        else:
            print("Failed requesting thumbnail")

        return {"title": yt.title, "thumbnail": thumb, "streams": streams}
    except:
        print("Video not available")
        return None


def DownloadProgressive(URL, path):
    yt = YouTube(URL)
    title = yt.title.replace(" ", "_")

    print(f"Downloading:\n\t{URL}\n\t{title}\nTo: {path}")
    try:
        av_stream = yt.streams.filter(
            progressive=True, file_extension="mp4").order_by("resolution").desc()
        av_title = title + ".mp4"
        av_file = av_stream.first().download(path, filename=av_title)
        print("Download successful!")
        return f"{path}{av_title}"
    except:
        print("Download failed")
        return None


def DownloadAdaptive(URL, path):
    yt = YouTube(URL)

    title = yt.title.replace(" ", "_")

    print(f"Downloading: {URL}\nTo: {path}")
    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4")
    audio_stream = yt.streams.filter(
        only_audio=True, file_extension="mp4")

    video_title = title + "_v.mp4"
    audio_title = title + "_a.mp4"

    try:
        video_file = video_stream.first().download(path, filename=video_title)
        audio_file = audio_stream.first().download(path, filename=audio_title)
        print("Download successful!")

        video_path = f"{path}{video_title}"
        audio_path = f"{path}{audio_title}"

        return video_path, audio_path, title
    except:
        print("Download failed")
        return None


def CombineAV(video_path, audio_path, output_path, title):
    print(f"Combining:\n    video: {video_path}\n    audio: {audio_path}")
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        final = output_path + title + ".mp4"
        ffmpeg.output(video, audio, final,
                      vcodec="copy", acodec="copy").run()

        print("Combining successful!")
    except ffmpeg.Error as e:
        print("FFmpeg Error: ", e.stderr)
