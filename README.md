# PYTDL

Simple GUI application build with CustomTkinter that allows downloading youtube videos.

## Important notes
1. Most videos get downloaded as separate audio and video streams which are then combined with ffmpeg. For this purpose the app creates temporary files for the streams!

2. The app freezes for the duration of the download, so you may not want to use it for downloading longer videos! I might fix this at some point. (=probably not!)

## Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```
