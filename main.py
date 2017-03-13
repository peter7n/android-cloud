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
        listOfCustomerKeys = streamingProvider.query().fetch(keys_only=True)
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
        newStreamingProvider = streamingProvider(name=streamingProviderData['name'])
        # propagate values for newStreamingProvider
        for key, value in streamingProviderData.iteritems():
            setattr(newStreamingProvider, key, value)
        newStreamingProvider.put()
        newStreamingProvider.id = newStreamingProvider.key.id()
        newStreamingProvider.self = "/streaming_provider/" + str(newStreamingProvider.key.id())
        newStreamingProvider.put()
        self.response.write(json.dumps(newStreamingProvider.to_dict()))

    def get(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            self.response.write(json.dumps(streamingProviderObj.to_dict()))
        else:
            # List all streaming providers
            listOfStreamingProviders = []
            allStreamingProvidersQuery = streamingProvider.query()
            for eachStreamingProvider in allStreamingProvidersQuery.fetch():
                listOfStreamingProviders.append(eachStreamingProvider.to_dict())
            self.response.write(json.dumps(listOfStreamingProviders))

    def delete(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            streamingProviderObj.key.delete()
            self.response.write(streamingProviderObj.name + " has been deleted.")

    def patch(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            streamingProviderData = json.loads(self.request.body)
            # patch attribute values for streamingProviderObj
            for key, value in streamingProviderData.iteritems():
                setattr(streamingProviderObj, key, value)
            streamingProviderObj.put()
            self.response.write(json.dumps(streamingProviderObj.to_dict()))

class CustomerBooksHandler(webapp2.RequestHandler):
    def get(self, streamingProviderId=None):
        if streamingProviderId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            bookList = []
            booksCheckedOut = streamingProviderObj.checked_out
            # Fetch Movie links from checked_out list
            for Movie in booksCheckedOut:
                url = "http://rest-nguyenp2.appspot.com" + Movie
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    bookList.append(result.content)
                else:
                    self.response.status_code = result.status_code
            self.response.write(bookList)

class CheckoutHandler(webapp2.RequestHandler):
    def put(self, streamingProviderId=None, movieId=None):
        if streamingProviderId and movieId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            movieObj = Movie.get_by_id(int(movieId))
            # Add checked out Movie to streamingProvider's list
            streamingProviderObj.checked_out.append("/books/" + str(movieId))
            streamingProviderObj.put()
            # Set Movie status to checked out
            movieObj.checkedIn = False
            movieObj.put()
            self.response.write(json.dumps(streamingProviderObj.to_dict()))

    def delete(self, streamingProviderId=None, movieId=None):
        if streamingProviderId and movieId:
            streamingProviderObj = streamingProvider.get_by_id(int(streamingProviderId))
            movieObj = Movie.get_by_id(int(movieId))
            # Remove checked out Movie from streamingProvider's list
            streamingProviderObj.checked_out.remove("/books/" + str(movieId))
            streamingProviderObj.put()
            # Set Movie status to checked in
            movieObj.checkedIn = True
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

    ('/customers', CustomerHandler),

    webapp2.Route(r'/customers/<streamingProviderId:\d+>', handler=CustomerHandler),

    webapp2.Route(r'/customers/<streamingProviderId:\d+>/books', handler=CustomerBooksHandler),

    webapp2.Route(r'/customers/<streamingProviderId:\d+>/books/<movieId:\d+>', handler=CheckoutHandler),
], debug=True)
