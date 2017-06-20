#!/usr/bin/python

# Based on:
# https://developers.google.com/youtube/v3/code_samples/python#create_and_manage_comment_threads
#
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
#
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

import httplib2
import os
import sys
import csv
import re

from unidecode import unidecode
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

reload(sys)
sys.setdefaultencoding("utf-8")

CLIENT_SECRETS_FILE = "client_secret.apps.googleusercontent.com.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE
    )
    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
    with open("youtube-v3-discoverydocument.json", "r") as f:
        doc = f.read()
        return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

def get_videos(youtube, channelId, maxResults, pageToken):
    print 'channelId: {}'.format(channelId);
    result = youtube.search().list(
        part="snippet",
        channelId=channelId,
        pageToken=pageToken,
        order="viewCount",
        publishedAfter="2015-01-01T00:00:00Z",
        publishedBefore="2017-01-01T00:00:00Z",
        safeSearch="none",
        type="video",
        maxResults=maxResults
    ).execute()
    return result

def get_comments(youtube, videoId, maxResults, pageToken):
    print 'videoId: {}'.format(videoId);
    result = youtube.commentThreads().list(
        part="snippet",
        videoId=videoId,
        pageToken=pageToken,
        order="relevance",
        textFormat="plainText",
        maxResults=maxResults
    ).execute()
    return result

def clean_str(string):
    return re.sub(r"\s+", " ", string.encode("ascii", "ignore")).strip()

args = argparser.parse_args()
youtube = get_authenticated_service(args)

# Casey neistat - channelId UCtinbF-Q-fVthA0qrFQTgXQ
channels = [{
    "id" : "UCtinbF-Q-fVthA0qrFQTgXQ", "name": "CaseyNeistat",
    "id" : "UC-lHJZR3Gqxm24_Vd_AJ5Yw", "name": "PewDiePie",
    "id" : "UC1-szPBG7Oh4icM1FcQakQg", "name": "FleurDeForce",
    "id" : "UCkxgqm7W2kJ--jb3cB0CT8Q", "name": "FleurDeVlog"
}]

for channel in channels:
    videos = []
    pageToken = None

    for _ in range(1):
        if pageToken != False:
            resultVideos = get_videos(youtube, channel["id"], 50, pageToken)
            videos.extend(resultVideos["items"])
            pageToken = resultVideos.get("nextPageToken", False)

    with open("videos_%s.csv" % channel["name"], "wb+") as videoFile:
        videoWriter = csv.writer(videoFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        videoWriter.writerows([[
            "channelId",
            "channelTitle",
            "videoId",
            "videoTitle",
            "videoDesc",
            "videoPublishedAt"
        ]])
        for video in videos:
            videoWriter.writerows([[
                video["snippet"]["channelId"],
                clean_str(video["snippet"]["channelTitle"]),
                video["id"]["videoId"],
                clean_str(video["snippet"]["title"]),
                clean_str(video["snippet"]["description"]),
                video["snippet"]["publishedAt"].encode("ascii", "ignore")
            ]])

    comments = []
    for i, vi in enumerate(videos):
        print "%s: %d" % (channel["name"], i)
        videoId = vi["id"]["videoId"]
        pageToken = None
        for _ in range(4):
            if pageToken != False:
                try:
                    resultComments = get_comments(youtube, videoId, 100, pageToken)
                    comments.extend(resultComments.get("items", []))
                    pageToken = resultComments.get("nextPageToken", False)
                except Exception as e:
                    print "Http Error happened"
                    pass

    with open("comments_%s.csv" % channel["name"], "wb+") as commentFile:
        commentWriter = csv.writer(commentFile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        commentWriter.writerows([[
            "videoId",
            "commentId",
            "author",
            "text",
            "replies",
            "likes",
            "publishedAt"
        ]])
        for comment in comments:
            clc = comment["snippet"]["topLevelComment"]["snippet"]
            commentWriter.writerows([[
                comment["snippet"]["videoId"],
                comment["snippet"]["topLevelComment"]["id"],
                clean_str(clc["authorDisplayName"]),
                clean_str(clc["textDisplay"]),
                comment["snippet"]["totalReplyCount"],
                clc["likeCount"],
                clc["publishedAt"].encode("ascii", "ignore")
            ]])
