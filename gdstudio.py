import urllib.request
import urllib.parse
import json

GDSTUDIO_API = 'https://music-api.gdstudio.xyz/api.php'
SUPPORTED_SOURCES = ['netease', 'joox']

QUALITY_MAP = {
    '128k': 128,
    '192k': 192,
    '320k': 320,
    'flac': 999,
    'flac24bit': 999,
}


def search(keyword, source='netease', count=20, pages=1):
    params = {
        'types': 'search',
        'source': source,
        'name': keyword,
        'count': str(count),
        'pages': str(pages),
    }
    url = GDSTUDIO_API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def get_url(source, track_id, br=320):
    params = {
        'types': 'url',
        'source': source,
        'id': str(track_id),
        'br': str(br),
    }
    url = GDSTUDIO_API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    return data.get('url', ''), data.get('br', -1), data.get('size', 0)


def search_and_get_url(song_name, song_singer='', quality='320k'):
    keyword = f'{song_singer} {song_name}'.strip() if song_singer else song_name
    br = QUALITY_MAP.get(quality, 320)

    for src in SUPPORTED_SOURCES:
        try:
            results = search(keyword, source=src, count=5)
            if not results:
                continue
            for item in results:
                name = item.get('name', '')
                artist_list = item.get('artist', [])
                if isinstance(artist_list, list):
                    artist = '/'.join(a if isinstance(a, str) else a.get('name', '') for a in artist_list)
                else:
                    artist = str(artist_list)
                if not name:
                    continue
                if song_name not in name and name not in song_name:
                    continue
                track_id = item.get('id', '')
                if not track_id:
                    continue
                play_url, actual_br, size = get_url(src, track_id, br)
                if play_url:
                    return play_url, src, track_id, actual_br, size
                if br > 320:
                    play_url, actual_br, size = get_url(src, track_id, 320)
                    if play_url:
                        return play_url, src, track_id, actual_br, size
        except Exception:
            continue
    return None, None, None, None, None
