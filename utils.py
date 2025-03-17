from pytubefix import YouTube
import ffmpeg
import requests
from PIL import Image
from io import BytesIO
import os
import uuid


def GetStreams(URL):
    yt = YouTube(URL)
    try:
        print(yt.streams)
        thumb = None
        r = requests.get(yt.thumbnail_url)
        if r.status_code == 200:
            thumb = Image.open(BytesIO(r.content))
        else:
            print("Failed requesting thumbnail")

        return {
            "title": yt.title,
            "thumbnail": thumb,
            "streams": yt.streams,
        }
    except Exception as e:
        print(f"Getting streams failed! Exception: {e}")
        return None


def DeleteFile(path):
    try:
        os.remove(path)
    except PermissionError:
        print(f"Permission denied! Cannot delete: {path}")
    except Exception as e:
        print(f"Error while deleting {path}: {e}")


def ExtractFileExtension(stream):
    return stream.mime_type.split("/")[1]


def Download(itag, streams, path, title, delete_temp=True):
    title = title.replace(" ", "_")
    stream = streams.get_by_itag(itag)
    stream_file_extension = "." + ExtractFileExtension(stream)

    print("DOWNLOADING:\n\t", stream)

    if stream.type == "audio" or stream.is_progressive:
        try:
            stream.download(path, filename=title + stream_file_extension)
        except Exception as e:
            print(f"Download failed! Exception: {e}")
            return False
    elif stream.type == "video":
        audio_stream = streams.filter(only_audio=True).first()
        audio_title = f"{uuid.uuid4().hex}_a.{
            ExtractFileExtension(audio_stream)}"

        video_title = f"{uuid.uuid4().hex}_v{stream_file_extension}"

        try:
            stream.download(path, filename=video_title)
            audio_stream.download(
                path, filename=audio_title)
        except Exception as e:
            print(f"Download failed! Exception: {e}")
            return False

        video_path = path + video_title
        audio_path = path + audio_title

        if os.path.exists(video_path) and os.path.exists(audio_path):
            CombineAV(video_path, audio_path, path, title)
            if delete_temp:
                print("Deleting temporary files")
                DeleteFile(video_path)
                DeleteFile(audio_path)
        else:
            print(f"Error! Files:\n\t{video_path}\n\t{
                  audio_path}\nDon't exist!")
    else:
        print("Nothing to download")
        return False

    print(f"Download successful: {path}{title}")
    return True


def CombineAV(video_path, audio_path, output_path, title):
    print(f"Combining:\n    video: {video_path}\n    audio: {audio_path}")
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        final = output_path + title + ".mp4"
        ffmpeg.output(video, audio, final,
                      vcodec="copy", acodec="copy").run(overwrite_output=True, quiet=True)

        print("Combining successful!")
        return True
    except ffmpeg.Error as e:
        print("FFmpeg Error: ", e.stderr)
        return False
