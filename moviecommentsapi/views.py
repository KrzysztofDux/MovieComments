from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def movies(request):
    if request.method == 'GET':
        get_movies(request)
    elif request.method == 'POST':
        post_movies(request)


def get_movies(request):
    pass


def post_movies(request):
    pass


@api_view(['GET', 'POST'])
def comments(request):
    if request.method == 'GET':
        get_movies(request)
    elif request.method == 'POST':
        post_movies(request)


def get_comments(request):
    pass


def post_comments(request):
    pass


@api_view(['GET'])
def top(request):
    pass
