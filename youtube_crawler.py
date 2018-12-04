"""
youtube api 이용한 comments crawler
by 임정빈.
"""
import json
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen
from pandas import DataFrame
import pandas as pd

YOUTUBE_COMMENT_URL = 'https://content.googleapis.com/youtube/v3/commentThreads'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'


class YouTubeApi:

    def __init__(self):
        self.texts = []
        self.authors = []
        self.dates = []

    def load_comments(self, mat):
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            author = comment["snippet"]["authorDisplayName"]
            text = comment["snippet"]["textDisplay"]
            date = comment["snippet"]["publishedAt"]
            if author and text and date:
                self.authors.append(author)
                self.texts.append(text)
                self.dates.append(date[0:10])
            if 'replies' in item.keys():
                for reply in item['replies']['comments']:
                    rauthor = reply['snippet']['authorDisplayName']
                    rtext = reply["snippet"]["textDisplay"]
                    rdate = reply["snippet"]["publishedAt"]
                    if rauthor and rtext and rdate:
                        self.authors.append("Re:" + rauthor)
                        self.texts.append(rtext)
                        self.dates.append(rdate[0:10])

    def get_video_comment(self, videourl, key):
        mxres = 100
        vid = str()

        try:
            video_id = urlparse(videourl)
            q = parse_qs(video_id.query)
            vid = q["v"][0]

        except:
            print("Invalid YouTube URL")

        parms = {
                    'part': 'snippet,replies',
                    'maxResults': mxres,
                    'videoId': vid,
                    'textFormat': 'plainText',
                    'key': key
                }

        try:

            matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
            i = 2
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")
            print("\nPage : 1")
            print("------------------------------------------------------------------")
            self.load_comments(mat)

            while nextPageToken:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
                mat = json.loads(matches)
                nextPageToken = mat.get("nextPageToken")
                print("\nPage : ", i)
                print("------------------------------------------------------------------")

                self.load_comments(mat)

                i += 1
        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot Open URL or Fetch comments at a moment")

    def openURL(self, url, parms):
            f = urlopen(url + '?' + urlencode(parms))
            data = f.read()
            f.close()
            matches = data.decode("utf-8")
            return matches


def main():
    y = YouTubeApi()
    # 이 부분에 댓글 가져오고 싶은 영상의 url과 본인의 유튜브 api 키 입력해주세요..!
    y.get_video_comment("https://www.youtube.com/watch?v=nZbUcmvW4TA", "유튜브 api 키 입력 해주세요!")
    text_list = [y.authors, y.texts, y.dates]
    return text_list


if __name__ == '__main__':
    text_list = main()
    # 파일명 가수_노래로 해주세요
    writer = pd.ExcelWriter('닐로_지나가다.xlsx', engine='xlsxwriter')
    df = DataFrame(
        {'Author': text_list[0], 'Comment': text_list[1], 'PublishedAt': text_list[2]})
    count_dic = {}
    for date in df['PublishedAt']:
        if str(date) in count_dic:
            count_dic[str(date)] += 1
        else:
            count_dic[str(date)] = 1
    frequency = DataFrame(
        {'PublishedAt': list(count_dic.keys()), 'Frequency': list(count_dic.values())})
    # 댓글 내용은 comment에 저장됩니다.
    df.to_excel(writer, sheet_name='comment', encoding='utf-8')
    # 빈도수는 frequency sheet에 저장됩니다.
    frequency.to_excel(writer, sheet_name='frequency', encoding='utf-8')
    writer.save()
    # 선물 : https://www.youtube.com/watch?v=qYYJqWsBb1U
    # 지나오다 : https://www.youtube.com/watch?v=nZbUcmvW4TA

