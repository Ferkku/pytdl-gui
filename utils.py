from pytubefix import YouTube
import ffmpeg
import requests
from PIL import Image
from io import BytesIO
import os
import uuid
import logging
import warnings

warnings.filterwarnings("ignore", module="customtkinter")
logging.basicConfig(level=logging.ERROR)


def GetStreams(URL):
    yt = YouTube(URL)
    try:
        logging.debug(yt.streams)
        thumb = None
        r = requests.get(yt.thumbnail_url)
        if r.status_code == 200:
            thumb = Image.open(BytesIO(r.content))
        else:
            logging.debug("Failed requesting thumbnail")

        return {
            "title": yt.title,
            "thumbnail": thumb,
            "streams": yt.streams,
        }
    except Exception as e:
        logging.debug(f"Getting streams failed! Exception: {e}")
        return None


def DeleteFile(path):
    try:
        os.remove(path)
    except PermissionError:
        logging.debug(f"Permission denied! Cannot delete: {path}")
    except Exception as e:
        logging.debug(f"Error while deleting {path}: {e}")


def ExtractFileExtension(stream):
    return stream.mime_type.split("/")[1]


def Download(itag, streams, path, title, delete_temp=True):
    title = title.replace(" ", "_")
    stream = streams.get_by_itag(itag)
    stream_file_extension = "." + ExtractFileExtension(stream)

    logging.debug("DOWNLOADING:\n\t", stream)

    if stream.type == "audio" or stream.is_progressive:
        try:
            stream.download(path, filename=title + stream_file_extension)
        except Exception as e:
            logging.debug(f"Download failed! Exception: {e}")
            return False
    elif stream.type == "video":
        audio_stream = streams.filter(
            only_audio=True, file_extension=ExtractFileExtension(stream)).first()
        audio_title = f"{uuid.uuid4().hex}_a.{
            ExtractFileExtension(audio_stream)}"

        video_title = f"{uuid.uuid4().hex}_v{stream_file_extension}"

        try:
            stream.download(path, filename=video_title)
            audio_stream.download(
                path, filename=audio_title)
        except Exception as e:
            logging.debug(f"Download failed! Exception: {e}")
            return False

        video_path = path + video_title
        audio_path = path + audio_title

        if os.path.exists(video_path) and os.path.exists(audio_path):
            CombineAV(video_path, audio_path, path,
                      title, stream_file_extension)
            if delete_temp:
                logging.debug("Deleting temporary files")
                DeleteFile(video_path)
                DeleteFile(audio_path)
        else:
            logging.debug(f"Error! Files:\n\t{video_path}\n\t{
                audio_path}\nDon't exist!")
    else:
        logging.debug("Nothing to download")
        return False

    logging.debug(f"Download successful: {path}{title}")
    return True


def CombineAV(video_path, audio_path, output_path, title, file_extension):
    logging.debug(f"Combining:\n    video: {
                  video_path}\n    audio: {audio_path}")
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        final = output_path + title + file_extension
        ffmpeg.output(video, audio, final,
                      vcodec="copy", acodec="copy").run(overwrite_output=True, quiet=True)

        logging.debug("Combining successful!")
        return True
    except ffmpeg.Error as e:
        logging.debug("FFmpeg Error: ", e.stderr)
        return False
