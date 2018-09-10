import requests
import json


class NEM_spider(object):

    def __init__(self):
        self.headers={
        'host':'music.163.com',
        'Referer':'http://music.163.com/search',
        'User-Agent':('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36')
        }
        self.cookies={'appver':'1.5.2'}


    def get_playlist_detail(self,playlist_id):
        url='http://music.163.com/api/playlist/detail'
        payload={'id':playlist_id}

        r=requests.get(url,params=payload,headers=self.headers,cookies=self.cookies)
        playlist_detail=r.json()['result']['tracks']
        print(playlist_detail)
        return playlist_detail

    def from_playlist_get_song_list(self,playlist_id):
        playlist_detail=self.get_playlist_detail(playlist_id)
        songlist=[]
        for song_detail in playlist_detail:
            song={}
            song['id']= song_detail['id']
            song['name']=song_detail['name']
            artists_detail=[]
            for artist in song_detail['artists']:
                artist_detail={}
                artist_detail['name']=artist['name']
                artist_detail['id']=artist['id']
                artists_detail.append(artist_detail)
            song['artists']=artists_detail
            songlist.append(song)

        return songlist


    def get_artists_songlist(self,artist_id):
        url='http://music.163.com/api/artist/{}'.format(artist_id)

        r=requests.get(url,headers=self.headers,cookies=self.cookies)
        hotSongs=r.json()['hotSongs']

        songlist=[]
        for hotSong in hotSongs:
            song={}
            song['id']=hotSong['id']
            song['name']=hotSong['name']
            songlist.append(song)

        return songlist

    def get_song_lyric(self, song_id):
        url='http://music.163.com/api/song/lyric'
        payload = {
        'os':'pc',
        'id': song_id,
        'lv': -1,
        'kv': -1,
        'tv': -1
        }

        r=requests.get(url,params=payload, headers=self.headers,
            cookies=self.cookies)

        result=r.json()

        if('nolyric' in result) or ('uncollected' in result):
            return None
        elif 'lyric' not in result['lrc']:
            return None
        else:
            return result['lrc']['lyric']

    def get_song_comments(self,song_id,offset=0,total='false',limit=100):
        url = ('http://music.163.com/api/v1/resource/comments/R_SO_4_{}/'
            ''.format(song_id))
        payload={
        'rid': 'R_SO_4_{}'.format(song_id),
        'offset': offset,
        'total': total,
        'limit': limit
        }

        r=requests.get(url,params=payload,headers=self.headers,cookies=self.cookies)
        print(r.json())
        return r.json()

    def get_total_comments(self,song_id):
        comments= self.get_song_comments(song_id)['comments']
        comments_list=[]
        offset=0
        while comments:
            for comment in comments:
                comment_detail ={}
                comment_detail['user_name']=comment['user']['nickname']
                comment_detail['user_id']=comment['user']['userId']
                comment_detail['content']=comment['content']
                comment_detail['time']=comment['time']
                comments_list.append(comment_detail)
            offset=offset+100
            commets=self.get_song_commets(song_id,
                offset=offset)['comments']

        return comments_list

    def from_playlist_get_artist_id(self,*playlists):
        artist_id_list =[]
        for playlist_id in playlists:
            song_list=self.from_playlist_get_song_list(playlist_id)
            for song in song_list:
                for artist in song['artists']:
                    print("Got {}'s id ==>{}".format(artist['name'],
                        artist['id']))

                artist_id_list.append(artist['id'])

        artist_id_list=list(set(artist_id_list))
        return artist_id_list

    def from_playlist_get_full_lyric_text(self,*playlists):
        artist_id_list=self.from_playlist_get_artist_id(playlists)
        song_id_list=[]
        lyric_list=[]

        for artist_id in artist_id_list:
            print('Processing the work of the artist with id:{}'
            ''.format(artist_id))
            songlist=self.get_artists_songlist(artist_id)
            artist_song_id_list=[song['id'] for song in songlist]
            song_id_list.extend(artist_song_id_list)

        song_id_list=list(set(song_id_list))

        for song_id in song_id_list:
            print('Processing the lyric of the song with id: {}'
                ''.format(song_id))
            lyric = self.get_song_lyric(song_id)

            if lyric is not None:
                lyric_list.append(lyric)

        return lyric_list

if __name__ == '__main__':
    spider = NEM_spider()
    lyriclist = spider.from_playlist_get_full_lyric_text(605415618,2051837289)
    with open('data/lyric_list.json', 'w') as f:
        json.dump(lyriclist, f)
    print('Done!')
