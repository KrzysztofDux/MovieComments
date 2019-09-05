from django.db import transaction

from ..models import Movie, Rating

expected_external_api_response = {
    "Title": "It",
    "Year": "2017",
    "Rated": "R",
    "Released": "08 Sep 2017",
    "Runtime": "135 min",
    "Genre": "Horror",
    "Director": "Andy Muschietti",
    "Writer": "Chase Palmer (screenplay by), Cary Joji Fukunaga (screenplay by), Gary Dauberman (screenplay by), Stephen King (based on the novel by)",
    "Actors": "Jaeden Martell, Jeremy Ray Taylor, Sophia Lillis, Finn Wolfhard",
    "Plot": "In the summer of 1989, a group of bullied kids band together to destroy a shape-shifting monster, which disguises itself as a clown and preys on the children of Derry, their small Maine town.",
    "Language": "English",
    "Country": "USA, Canada",
    "Awards": "4 wins & 30 nominations.",
    "Poster": "https://m.media-amazon.com/images/M/MV5BZDVkZmI0YzAtNzdjYi00ZjhhLWE1ODEtMWMzMWMzNDA0NmQ4XkEyXkFqcGdeQXVyNzYzODM3Mzg@._V1_SX300.jpg",
    "Ratings":
        [
            {
                "Source": "Internet Movie Database",
                "Value": "7.4/10"
            },
            {
                "Source": "Rotten Tomatoes",
                "Value": "86%"
            },
            {
                "Source": "Metacritic",
                "Value": "69/100"
            }
        ],
    "Metascore": "69",
    "imdbRating": "7.4",
    "imdbVotes": "376,032",
    "imdbID": "tt1396484",
    "Type": "movie",
    "DVD": "09 Jan 2018",
    "BoxOffice": "$326,898,358",
    "Production": "Warner Bros. Pictures",
    "Website": "http://itthemovie.com/",
    "Response": "True"
}

""" API should return response from external api with additional Id field """
expected_api_response = {"Id": "6"}
expected_api_response.update(expected_external_api_response)
expected_api_response['imdbVotes'] = expected_api_response['imdbVotes'].replace(",", "")


def get_saved_test_movie():
    with transaction.atomic():
        movie = Movie.objects.create(
            title="It",
            year=2017,
            rated="R",
            released="08 Sep 2017",
            runtime="135 min",
            genre="Horror",
            director="Andy Muschietti",
            writer="Chase Palmer (screenplay by), Cary Joji Fukunaga (screenplay by), Gary Dauberman (screenplay by), Stephen King (based on the novel by)",
            actors="Jaeden Martell, Jeremy Ray Taylor, Sophia Lillis, Finn Wolfhard",
            plot="In the summer of 1989, a group of bullied kids band together to destroy a shape-shifting monster, which disguises itself as a clown and preys on the children of Derry, their small Maine town.",
            language="English",
            country="USA, Canada",
            awards="4 wins & 30 nominations.",
            poster="https://m.media-amazon.com/images/M/MV5BZDVkZmI0YzAtNzdjYi00ZjhhLWE1ODEtMWMzMWMzNDA0NmQ4XkEyXkFqcGdeQXVyNzYzODM3Mzg@._V1_SX300.jpg",
            metascore=69,
            imdb_rating=7.4,
            imdb_votes=376032,
            imdb_id="tt1396484",
            type="movie",
            dvd="09 Jan 2018",
            box_office="$326,898,358",
            production="Warner Bros. Pictures",
            website="http://itthemovie.com/")
        movie.rating_set.create(
            source="Metacritic",
            value="69/100")
        movie.rating_set.create(
            source="Rotten Tomatoes",
            value="86%")
        movie.rating_set.create(
            source="Internet Movie Database",
            value="7.4/10")
    return movie


class MockMovieDetailsProvider:
    def get_details(self, title):
        return expected_external_api_response
