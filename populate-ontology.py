from SPARQLWrapper import SPARQLWrapper, N3, RDF, JSON
from dateutil.parser import parse
import pprint
import codecs
import urllib
import re
import json

class Populator:    
    sparql = SPARQLWrapper("http://data.linkedmdb.org/sparql")
    actors = ['Johnny Depp', 'Javier Bardem', 'Helena Bonham Carter',
              'Scarlett Johansson']
    movies_info = {}
    movies_scarlett = ["Avengers: Age of Ultron", "Lucy", "Captain "\
                       " America: The Winter Soldier", "Chef", \
                       "Under the Skin", "Don Jon", "Hitchcock", \
                       "The Avengers", "Iron Man 2", \
                       "He's Just Not That Into You", \
                       "The Spirit", "Vicky Cristina Barcelona", \
                       "The Other Boleyn Girl", "The Nanny Diaries", \
                       "The Prestige", "The Black Dahlia", "Scoop", \
                       "The Island", "Match Point", "In Good Company", \
                       "A Good Woman", "A Love Song for Bobby Long", \
                       "The Perfect Score", "Girl with a Pearl Earring", \
                       "Lost in Translation", "Eight Legged Freaks", \
                       "An American Rhapsody", "Ghost World", \
                       "The Man Who Wasn't There", "My Brother the Pig", \
                       "The Horse Whisperer", "Home Alone 3", "Fall", \
                       "If Lucy Fell", "Manny & Lo", "Just Cause", "North"]

    def get_actors_for_movie(self, movie):
        movie = movie.encode('utf-8')
        movie = urllib.quote(movie)
        urlMovie = 'http://www.omdbapi.com/?t=' + movie + '&plot=full&r=json'
        response = urllib.urlopen(urlMovie)
        data = json.loads(response.read())
        if data.has_key('imdbID'):
            director = data['Director']
            imdbID = data['imdbID']
            year = data['Year']
            urlCredits = 'http://www.imdb.com/title/' + imdbID + '/fullcredits'
            file = urllib.urlopen(urlCredits)
            data = file.read()
            these_regex = '<span class="itemprop" itemprop="name">(.+?)</span>'
            pattern = re.compile(these_regex)
            names = re.findall(pattern, data)
            self.add_movie_info(movie, 'director', director)
            self.add_movie_info(movie, 'release_date', year)
            self.add_movie_info(movie, 'actor', names)

    def populate(self):
        for actor in self.actors:
            self.get_movies_for_actor(actor)
        for movie in self.movies_info.copy():
            self.get_actors_for_movie(movie)
        self.generate_turtle()

    def generate_turtle(self):
        for movie in self.movies_info:
            print movie
            print self.movies_info[movie]

    def get_year(self, date):
        return parse

    def execute_query(self, query):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()

    def get_year(self, date):
        year = ''
        try:
            if date:
                year = parse(date).year
        except:
            year = ''
        return str(year)

    def get_movies_for_actor(self, actor):
        query = """
           PREFIX movie: <http://data.linkedmdb.org/resource/movie/>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns>
           PREFIX dc: <http://purl.org/dc/terms/>
           SELECT ?movie_title ?release_date ?date
           WHERE { 
              ?actor a movie:actor .
              ?actor movie:actor_name ?actor_name .
              ?movie a movie:film .
              ?movie movie:actor ?actor .
              ?movie dc:title ?movie_title .
              ?movie movie:initial_release_date ?release_date .
              ?movie dc:date ?date .
           FILTER regex(?actor_name, '%s', 'i') .
           }
        """ % (actor)
        result = self.execute_query(query)
        for b in result['results']['bindings']:
            self.add_movie_info(b['movie_title']['value'],
                                'release_date',
                                self.get_year(b['release_date']['value']))

    def add_movie_info(self, movie, info, value):
        if not movie in self.movies_info:
            self.movies_info[movie] = {}
        self.movies_info[movie][info] = value        

def main():
    Populator().populate()

main()
