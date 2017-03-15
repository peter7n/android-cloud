###########################################
# Author: Peter Nguyen
# Date:
# CS496-400
# Description:
###########################################

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import webapp2
import json
import re

class Home(webapp2.RequestHandler):
    def get(self):
        self.response.write('CS496 - Final Project - Author: Peter Nguyen')

    def delete(self):
        # Delete all Datastore entries
        listOfBookKeys = Movie.query().fetch(keys_only=True)
        listOfCustomerKeys = StreamingProvider.query().fetch(keys_only=True)
        ndb.delete_multi(listOfBookKeys)
        ndb.delete_multi(listOfCustomerKeys)
        self.response.write("All entries successfully deleted.")

class Movie(ndb.Model):
    id = ndb.IntegerProperty()
    title = ndb.StringProperty(required=True)
    year = ndb.IntegerProperty()
    genres = ndb.StringProperty(repeated=True)
    director = ndb.StringProperty()
    actors = ndb.StringProperty(repeated=True)
    streaming_providers = ndb.StringProperty(repeated=True)
    self = ndb.StringProperty()

class StreamingProvider(ndb.Model):
    id = ndb.IntegerProperty()
    name = ndb.StringProperty(required=True)
    number_of_titles = ndb.IntegerProperty()
    movies = ndb.StringProperty(repeated=True)
    exclusive_movies = ndb.StringProperty(repeated=True)
    self = ndb.StringProperty()

class MovieHandler(webapp2.RequestHandler):
    def post(self):
        movieData = json.loads(self.request.body)
        newMovie = Movie(title=movieData['title'])
        # propagate values for newMovie
        for key, value in movieData.iteritems():
            setattr(newMovie, key, value)
        newMovie.put()
        newMovie.id = newMovie.key.id()
        newMovie.self = "/movies/" + str(newMovie.key.id())
        newMovie.put()
        self.response.write(json.dumps(newMovie.to_dict()))

    def get(self, movieId=None, queryString=None):
        if movieId:
            movieObj = Movie.get_by_id(int(movieId))
            self.response.write(json.dumps(movieObj.to_dict()))
        # Check for a query string value
        qStrVal = self.request.get('checkedIn')
        checkedOutList = []
        if qStrVal:
            if qStrVal == "true":
                query = Movie.query(Movie.checkedIn == True)
                for result in query.fetch():
                    checkedOutList.append(result.to_dict())
            elif qStrVal == "false":
                query = Movie.query(Movie.checkedIn == False)
                for result in query.fetch():
                    checkedOutList.append(result.to_dict())
            self.response.write(json.dumps(checkedOutList))
        elif not movieId:
            # List all movies
            listOfMovies = []
            allMoviesQuery = Movie.query()
            for eachMovie in allMoviesQuery.fetch():
                listOfMovies.append(eachMovie.to_dict())
            self.response.write(json.dumps(listOfMovies))

    def delete(self, movieId=None):
        if movieId:
            movieObj = Movie.get_by_id(int(movieId))
            movieObj.key.delete()
            self.response.write(movieObj.title + " has been deleted.")

    def put(self, movieId=None):
        if movieId:
            titlePresent = False
            movieObj = Movie.get_by_id(int(movieId))
            movieData = json.loads(self.request.body)
            # Title field must be present to PUT
            for key, value in movieData.iteritems():
                if key == "title":
                    titlePresent = True
            if titlePresent:
                # Reset all JSON properties
                setattr(movieObj, "year", None)
                setattr(movieObj, "genres", [])
                setattr(movieObj, "director", "")
                setattr(movieObj, "actors", [])
                setattr(movieObj, "running_time", None)
                setattr(movieObj, "streaming_providers", [])
                # Update properties with PUT values
                for key, value in movieData.iteritems():
                    setattr(movieObj, key, value)
                movieObj.put()
                self.response.write(json.dumps(movieObj.to_dict()))
            else:
                self.response.write("title field required!")

    def patch(self, movieId=None):
        if movieId:
            movieObj = Movie.get_by_id(int(movieId))
            movieData = json.loads(self.request.body)
            # patch attribute values for movieObj
            for key, value in movieData.iteritems():
                setattr(movieObj, key, value)
            movieObj.put()
            self.response.write(json.dumps(movieObj.to_dict()))

class StreamingProviderHandler(webapp2.RequestHandler):
    def post(self):
        streamingProviderData = json.loads(self.request.body)
        newStreamingProvider = StreamingProvider(name=streamingProviderData['name'])
        # propagate values for newStreamingProvider
        for key, value in streamingProviderData.iteritems():
            setattr(newStreamingProvider, key, value)
        newStreamingProvider.put()
        newStreamingProvider.id = newStreamingProvider.key.id()
        newStreamingProvider.self = "/streaming-providers/" + str(newStreamingProvider.key.id())
        newStreamingProvider.put()
        self.response.write(json.dumps(newStreamingProvider.to_dict()))

    def get(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            self.response.write(json.dumps(streamingProviderObj.to_dict()))
        else:
            # List all streaming providers
            listOfStreamingProviders = []
            allStreamingProvidersQuery = StreamingProvider.query()
            for eachStreamingProvider in allStreamingProvidersQuery.fetch():
                listOfStreamingProviders.append(eachStreamingProvider.to_dict())
            self.response.write(json.dumps(listOfStreamingProviders))

    def delete(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            streamingProviderObj.key.delete()
            self.response.write(streamingProviderObj.name + " has been deleted.")

    def put(self, streamingProviderId=None):
        if streamingProviderId:
            namePresent = False
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            streamingProviderData = json.loads(self.request.body)
            # Title field must be present to PUT
            for key, value in streamingProviderData.iteritems():
                if key == "name":
                    namePresent = True
            if namePresent:
                # Reset all JSON properties
                setattr(streamingProviderObj, "number_of_titles", None)
                setattr(streamingProviderObj, "movies", [])
                setattr(streamingProviderObj, "exclusive_movies", [])
                # Update properties with PUT values
                for key, value in streamingProviderData.iteritems():
                    setattr(streamingProviderObj, key, value)
                streamingProviderObj.put()
                self.response.write(json.dumps(streamingProviderObj.to_dict()))
            else:
                self.response.write("name field required!")

    def patch(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            streamingProviderData = json.loads(self.request.body)
            # patch attribute values for streamingProviderObj
            for key, value in streamingProviderData.iteritems():
                setattr(streamingProviderObj, key, value)
            streamingProviderObj.put()
            self.response.write(json.dumps(streamingProviderObj.to_dict()))

class ProviderGetMoviesHandler(webapp2.RequestHandler):
    def get(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            movieList = []
            moviesAvailable = streamingProviderObj.movies
            # Fetch Movie links from checked_out list
            for movie in moviesAvailable:
                url = "http://localhost:8080" + movie
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    movieList.append(result.content)
                else:
                    self.response.status_code = result.status_code
            self.response.write(movieList)

class ProviderAddRemoveMoviesHandler(webapp2.RequestHandler):
    def put(self, streamingProviderId=None, movieId=None):
        if streamingProviderId and movieId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            movieObj = Movie.get_by_id(int(movieId))
            # Add Movie link to StreamingProvider's list
            streamingProviderObj.movies.append("/movies/" + str(movieId))
            streamingProviderObj.put()
            # Add StreamingProvider link to Movie's list
            movieObj.streaming_providers.append("/streaming_providers/" + str(streamingProviderId))
            movieObj.put()
            self.response.write(json.dumps(streamingProviderObj.to_dict()))

    def delete(self, streamingProviderId=None, movieId=None):
        if streamingProviderId and movieId:
            streamingProviderObj = StreamingProvider.get_by_id(int(streamingProviderId))
            movieObj = Movie.get_by_id(int(movieId))
            # Remove Movie link from StreamingProvider's list
            streamingProviderObj.movies.remove("/movies/" + str(movieId))
            streamingProviderObj.put()
            # Removie StreamingProvider link from Movie's list
            movieObj.streaming_providers.remove("/streaming_providers/" + str(streamingProviderId))
            movieObj.put()
            self.response.write(json.dumps(streamingProviderObj.to_dict()))

# Allow patch operations
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', Home),

    ('/movies', MovieHandler),

    webapp2.Route(r'/movies/<movieId:\d+>', handler=MovieHandler),

    # webapp2.Route(r'/movies<queryString:\s+>', handler=BookHandler),

    ('/streaming-providers', StreamingProviderHandler),

    webapp2.Route(r'/streaming-providers/<streamingProviderId:\d+>', handler=StreamingProviderHandler),

    webapp2.Route(r'/streaming-providers/<streamingProviderId:\d+>/movies', handler=ProviderGetMoviesHandler),

    webapp2.Route(r'/streaming-providers/<streamingProviderId:\d+>/exclusive-movies', handler=ProviderGetExclusiveMoviesHandler),

    webapp2.Route(r'/streaming-providers/<streamingProviderId:\d+>/movies/<movieId:\d+>', handler=ProviderAddRemoveMoviesHandler),

    webapp2.Route(r'/streaming-providers/<streamingProviderId:\d+>/exclusive-movies/<movieId:\d+>', handler=ProviderAddRemoveExclusiveMoviesHandler),
], debug=True)
