from pytubefix import YouTube
import ffmpeg


def Download(URL, path):
    yt = YouTube(URL)

    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4")
    audio_stream = yt.streams.filter(only_audio=True, file_extension="webm")

    title = yt.title.replace(" ", "_")

    video_title = title + "_temp.mp4"
    audio_title = title + "_temp.webm"

    try:
        print(f"Downloading: {URL}\nTo: {path}")
        video_file = video_stream.first().download(path, filename=video_title)
        audio_file = audio_stream.first().download(path, filename=audio_title)
    except:
        print("Download failed")
        return None

    print("Download successful!")

    video_path = f"{path}{video_title}"
    audio_path = f"{path}{audio_title}"

    return video_path, audio_path, title


def CombineAV(video_path, audio_path, output_path, title):
    print(f"Combining:\n    video: {video_path}\n    audio: {audio_path}")

    audio_input = ffmpeg.input(audio_path)
    video_input = ffmpeg.input(video_path)

    final_path = output_path + title + ".mp4"

    try:
        ffmpeg.concat(video_input, audio_input, v=1,
                      a=1).output(final_path, codec="copy").run()
        print("Combining successful!")
    except ffmpeg.Error as e:
        print("FFmpeg Error: ", e.stderr)

    return None
