from SPARQLWrapper import SPARQLWrapper, N3, RDF, JSON
import pprint

sparql = SPARQLWrapper("http://data.linkedmdb.org/sparql")

# sparql.setQuery("""
#     PREFIX movie: <http://data.linkedmdb.org/resource/movie/>
#     PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns>
#     PREFIX dcterms: <http://purl.org/dc/terms/>

#     SELECT ?actor ?label ?name
#        WHERE { 
#              ?actor a movie:actor .
#              ?actor rdfs:label ?label .
#              ?actor movie:actor_name ?name .
#              FILTER regex(?name, 'depp', 'i') .
#        }
# """)


sparql.setQuery("""
    PREFIX movie: <http://data.linkedmdb.org/resource/movie/>
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns>
    PREFIX dc: <http://purl.org/dc/terms/>

    SELECT ?name ?title
       WHERE { 
             ?actor a movie:actor .
             ?actor rdfs:label ?label .
             ?actor movie:actor_name ?name .
             ?movie a movie:film .
             ?movie movie:actor ?actor .
             ?movie dc:title ?title
             FILTER regex(?name, 'depp', 'i') .
       }
""")

# RDF example
print '\n\n*** RDF Example'
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
pprint.pprint(results)

