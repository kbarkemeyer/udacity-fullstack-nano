import httplib
import json

api_key = "[YOUR API KEY GOES HERE]"


def movie_storyline(movie_title):
    conn = httplib.HTTPConnection("api.themoviedb.org")
    film = movie_title.replace(' ', '%20')
    conn.request(
        "GET", "/3/search/movie?include_adult=false&page=1&query=" + film +
        "&language=en-US&api_key=" + api_key, "{}")
    res = conn.getresponse()
    data = json.load(res)
    storyline = data['results'][0]['overview']
    return storyline
