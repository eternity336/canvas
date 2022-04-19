from datetime import datetime
import glob
import cv2
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload


canvas_location = 'static/img/canvas_*.png'
canvas_video_location = 'static/video/canvas_video_{date}.avi'
oauth_secret = 'oauth/client_secret.json'
channel_id = "UCmr526xZc4eIMOO6ATOA_9Q"
title = 'Eternity336 Canvas {num}'
description = 'Eternity336 Canvas {num} an accumulation of 10,000 uodates!  Goto https://canvas.eternity336.com/ to contribute your expression on the canvas!'
tags = ["canvas","eternity336"]
fps = 1
frames = 300

def enough_images(canvas_location:str = canvas_location, frames:int = frames):
    return len([_ for _ in glob.glob(canvas_location)]) >= frames

def create_video(canvas_location:str = canvas_location, canvas_video_location:str = canvas_video_location, fps:int = fps):
    img_array = []
    for filename in sorted(glob.glob(canvas_location)):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    out = cv2.VideoWriter(canvas_video_location.format(date = str(datetime.now()).replace(' ','_')),0, fps, size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()	

# Sample Python code for youtube.videos.insert
# NOTES:
# 1. This sample code uploads a file and can't be executed via this interface.
#    To test this code, you must run it locally using your own API credentials.
#    See: https://developers.google.com/explorer-help/code-samples#python
# 2. This example makes a simple upload request. We recommend that you consider
#    using resumable uploads instead, particularly if you are transferring large
#    files or there's a high likelihood of a network interruption or other
#    transmission failure. To learn more about resumable uploads, see:
#    https://developers.google.com/api-client-library/python/guide/media_upload


scopes = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_to_youtube(filename:str, title:str = title, description:str = description, tags:list = tags, channel_id:str = channel_id):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        oauth_secret, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().insert(
        body={
          "snippet": {
            "title": f"{title.format(num = 'test')}",
            "channelId": channel_id,
            "description": f"{description.format(num = 'test')}",
            "tags": tags
          }
        },
        
        # TODO: For this request to work, you must replace "YOUR_FILE"
        #       with a pointer to the actual file you are uploading.
        media_body=MediaFileUpload(filename)
    )
    response = request.execute()

    print(response)
