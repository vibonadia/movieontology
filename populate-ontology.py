# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, N3, RDF, JSON
from dateutil.parser import parse
import pprint
import codecs
import urllib
import re
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Populator:    
    sparql = SPARQLWrapper("http://data.linkedmdb.org/sparql")
    all_actors = {}
    all_directors = {}
    actors = ['Johnny Depp', 'Javier Bardem', 'Helena Bonham Carter',	
              'Scarlett Johansson']
    directors = ['Woody Allen', 'Tim Burton']
    directors = []
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

    def __init__(self):
       for m in self.movies_scarlett:
           self.add_movie_info(m.strip(), 'x', 'x')
       for m in open("WoodyAlen_Movies.txt", "r").readlines():
           self.add_movie_info(m.strip(), 'x', 'x')
       for m in open("TimBurton_Movies.txt", "r").readlines():
           self.add_movie_info(m.strip(), 'x', 'x')

    def get_actors_for_movie(self, movie):
        movie = movie.encode('utf-8')
        movieQuote = urllib.quote(movie)
        urlMovie = 'http://www.omdbapi.com/?t=' +movieQuote+ '&plot=full&r=json'
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
        #else:
        #    print '\n\n MOVIE IGNORED: '+movie

    def populate(self):
        for actor in self.actors:
            self.get_movies_for_actor(actor)
        for movie in self.movies_info.copy():
            self.get_actors_for_movie(movie)
        self.generate_turtle_actors()
        	
    def get_key(self, key):
        return key.replace(' ', '_').lower()

    def generate_turtle_actors(self):
        self.generate_actor_ids()
        for actor in self.all_actors:
            print self.get_turtle_for_actor(actor)

    def split_name(self, name):
        splitted_name = name.split(' ', 1)
        if len(splitted_name) < 2:
            splitted_name.append('')
        return splitted_name

    def generate_actor_ids(self):
        self.all_actors = {}
        for movie in self.movies_info:
            print self.get_turtle_for_movie(movie)
            if 'actor' in self.movies_info[movie]:
                for actor in self.movies_info[movie]['actor']:
                    self.all_actors[actor] = self.get_key(actor)
            if 'director' in self.movies_info[movie]:
                director = self.movies_info[movie]['director']
                self.all_directors[director] = self.get_key(director)
                print self.get_turtle_for_director(director)

    def get_turtle_for_person(self, name, concept, key_source):
        (first_name, last_name) = self.split_name(name)
        return """ 
:%s rdf:type movies:%s, owl:NamedIndividual ;
     mfoaf:FOAF-modifiedfirstName "%s"^^rdfs:Literal ;
     mfoaf:FOAF-modifiedfamilyName "%s"^^rdfs:Literal .""" %\
         (key_source[name], concept, first_name, last_name)

    def get_turtle_for_movie(self, movie):
        movie = movie.strip()
        info = self.movies_info[movie]
        if not 'director' in info:
            return ''
        actors_info = ''
        if 'actor' in info:
            for actor in info['actor']:
                actors_info += '\n      movies:hasActor :%s ;' % (self.get_key(actor))
        return """
:%s rdf:type movies:Movie, owl:NamedIndividual ;
     movies:hasYear "%s"^^xsd:int ;
     movies:hasTitle "%s"^^rdfs:Literal ;
     %s
     movies:hasDirector :%s .
""" % (self.get_key(movie), info['release_date'], movie, actors_info,\
       self.get_key(info['director']))

    def get_turtle_for_actor(self, actor):
        return self.get_turtle_for_person(actor, 'Actor',
                                          self.all_actors)

    def get_turtle_for_director(self, director):
        return self.get_turtle_for_person(director, 'Director',
                                          self.all_directors)
        		
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
