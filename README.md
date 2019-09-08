# MovieCommentsAPI
MovieCommentsAPI is simple REST API that consumes [OMDb API](http://omdbapi.com) and enhance it, allowing user to leave comments on movies.

### Technologies used

* [Django](https://www.djangoproject.com/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* [Requests](https://2.python-requests.org/en/master/)
* [Gunicorn](https://gunicorn.org/)
* [Docker](https://www.docker.com/)

## How to run

You will need `docker` with `compose`.
Download or clone project and in it's root catalog run:

```sh
$ docker-compose up
```
App is preconfigured with OMDb API key used in development, it can however don't work (be overused for givne day or inactivated.)
If you want to use your own api key you can acquire it for free on [OMDb API site](http://www.omdbapi.com/apikey.aspx). You can then use it by setting as environment variable `OMDB_KEY`, or by placing it in projects settings under the same name.

## How to use

There are following endpoints available:
### POST:
| endpoint     | params       | description 
| ------------ | ------------ | ----------- 
| `/movies/`   | `title`      | Returns details about movie with provided `title`. Application will save those details and return them with the ID of this record, that can be used in other requests. If movie already exists in database it's details and ID will be returned. |
| `/comments/` | `id`,`text`  | Saves comment with `text` content to a movie pointed by it's `id`. 

### GET:
| endpoint   | required params      | optional params | description 
| ---------- | ---------------      | --------------- | --------
| `/movies/` |                      | `sort`          | Returns list of all movies saved in application's database. Setting `sort` to value of `T`/`t` or `(T/t)itle` will sort the results by title alphabetically. `Y`/`y` or `(Y/y)ear` will sort by year, ascending. `yt`/`YT`/`(Y/y)ear(T/t)itle` will sort by year and then by title. Other combinations will be ignored.
|`/comments/`|                      | `id`            | Returns list of all comments with corresponding movies' IDs. Setting `id` to movie's ID will filter comments only related to given movie.
| `/top/`    |`date_from`, `date_to`| `include_all`   | Returns ranking of movies, based on number of comments they received in date range provided in `date_from` and `date_to` params. Setting `include_all` to `T`/`t`, `Y`/`y`, `(T/t)rue` or `(Y/y)es` will include movies that didn't get any comments in given period.


