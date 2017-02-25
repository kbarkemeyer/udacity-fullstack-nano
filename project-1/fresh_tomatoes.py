import webbrowser
import os
import re
import tmdb


# Styles and scripting for the page
main_page_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Fresh Tomatoes!</title>
    <!-- Bootstrap 3 -->
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/css/bootstrap-theme.min.css">
    <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
    <!-- Include tether for tooltips/popover to work -->
    <script src="https://npmcdn.com/tether@1.2.4/dist/js/tether.min.js"></script>
    <script src="https://netdna.bootstrapcdn.com/bootstrap/3.1.0/js/bootstrap.min.js"></script>
    <style type="text/css" media="screen">

        /* GLOBALS */
        body {
            padding-top: 80px;
            background-image: url("background.jpg");
            no-repeat center center fixed;
            -webkit-background-size: cover;
            -moz-background-size: cover;
            -o-background-size: cover;
            background-size: cover;
        }

        /* TRAILER */
        #trailer .modal-dialog {
            margin-top: 200px;
            width: 640px;
            height: 480px;
        }
        .hanging-close {
            position: absolute;
            top: -12px;
            right: -12px;
            z-index: 9001;
        }
        #trailer-video {
            width: 100%;
            height: 100%;
        }

        /*NAVBAR */
        .navbar-brand {
            font-size: 24px;
            font-weight: bold;
        }
        .navbar-nav {
            font-size: 18px;
            font-weight: bold;
        }
        .dropdown-menu {
            font-size: 20px;
            font-weight: bold;
        }

        /* MOVIE-TILE */
        .movie-tile {
            margin-bottom: 20px;
            padding-top: 20px;
        }
        .movie-tile:hover {
            background-color: #083a6b;
            cursor: pointer;
        }
        .scale-media {
            padding-bottom: 56.25%;
            position: relative;
        }
        .scale-media iframe {
            border: none;
            height: 100%;
            position: absolute;
            width: 100%;
            left: 0;
            top: 0;
            background-color: #083a6b;
        }

        /* POPOVER */
        .popover {
            max-width: 100%;
        }
        .popover-content {
            font-size:14px;
        }
        .popover-title {
            font-size: 16px;
            font-weight: bold;
        }


    </style>
    <script type="text/javascript" charset="utf-8">
        // Pause the video when the modal is closed
        $(document).on('click', '.hanging-close, .modal-backdrop, .modal', function (event) {
            // Remove the src so the player itself gets removed, as this is the only
            // reliable way to ensure the video stops playing in IE
            $("#trailer-video-container").empty();
        });
        // Start playing the video whenever the trailer modal is opened
        $(document).on('click', '.movie-tile', function (event) {
            var trailerYouTubeId = $(this).attr('data-trailer-youtube-id')
            var sourceUrl = 'http://www.youtube.com/embed/' + trailerYouTubeId + '?autoplay=1&html5=1';
            $("#trailer-video-container").empty().append($("<iframe></iframe>", {
              'id': 'trailer-video',
              'type': 'text-html',
              'src': sourceUrl,
              'frameborder': 0
            }));
        });
        // Animate in the movies when the page loads
        $(document).ready(function () {
          $('.movie-tile').hide().first().show("fast", function showNext() {
            $(this).next("div").show("fast", showNext);
          });
        });
        // Enable popovers
        $(function () {
            $('[data-toggle="popover"]').popover()
        })
    </script>
</head>
'''


# The main page layout and title bar
# Add links and drop down menu to navbar and costumize navbar appearance
main_page_content = '''
  <body>
    <!-- Trailer Video Modal -->
    <div class="modal" id="trailer">
      <div class="modal-dialog">
        <div class="modal-content">
          <a href="#" class="hanging-close" data-dismiss="modal" aria-hidden="true">
            <img src="https://lh5.ggpht.com/v4-628SilF0HtHuHdu5EzxD7WRqOrrTIDi_MhEG6_qkNtUK5Wg7KPkofp_VJoF7RS2LhxwEFCO1ICHZlc-o_=s0#w=24&h=24"/>
          </a>
          <div class="scale-media" id="trailer-video-container">
          </div>
        </div>
      </div>
    </div>

    <!-- Main Page Content -->
    <div class="container-fluid">
        <nav class="navbar navbar-light navbar-fixed-top" style="background-color: #083a6b;" role="navigation">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">Fresh Tomatoes Movie Trailers</a>
                <ul class= "nav navbar-nav">
                    <li><a href="https://github.com/kbarkemeyer/udacity-fullstack-nano.git/">View on Github</a></li>
                    <li class="dropdown">
                        <a class="dropdown-toggle" data-toggle="dropdown" href="#">Movie Sites</a>
                        <ul class="dropdown-menu">
                            <li><a href="https://www.themoviedb.org/?language=en">The Movie Database</a></li>
                            <li><a href="https://www.rottentomatoes.com/">Rotten Tomatoes</a></li>
                            <li><a href="http://www.imdb.com/">IMDb</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </nav>
    </div>

    <div class="container-fluid">
        <div class=row-fluid">
      {movie_tiles}
        </div>
    </div>
  </body>
</html>
'''


# A single movie entry html template
# Add popover to display movie_info and movie_storyline on 'hover'
movie_tile_content = '''
<div class="col-md-6 col-lg-4 movie-tile text-center" data-trailer-youtube-id="{trailer_youtube_id}" data-toggle="modal" data-target="#trailer">
    <a data-toggle="popover" data-trigger="hover" data-placement="top" title="{movie_info}" data-content="{movie_storyline}">
    <img src="{poster_image_url}" width="220" height="342">
    <h2>{movie_title}</h2></a>

</div>
'''


def create_movie_tiles_content(movies):
    # The HTML content for this section of the page
    content = ''
    for movie in movies:
        # Extract the youtube ID from the url
        youtube_id_match = re.search(
            r'(?<=v=)[^&#]+', movie.trailer_youtube_url)
        youtube_id_match = youtube_id_match or re.search(
            r'(?<=be/)[^&#]+', movie.trailer_youtube_url)
        trailer_youtube_id = (youtube_id_match.group(0) if youtube_id_match
                              else None)
        # Call tmdb_test which uses the Movie Database API to provide
        # the storyline of movies
        storyline = tmdb.movie_storyline(movie.title).encode('utf-8')

        # Append the tile for the movie with its content filled in
        # Replace storyline by info and include storyline retrieved
        # from the Movie Database API
        content += movie_tile_content.format(
            movie_title=movie.title,
            movie_info=movie.info,
            poster_image_url=movie.poster_image_url,
            trailer_youtube_id=trailer_youtube_id,
            movie_storyline=storyline
        )
    return content


def open_movies_page(movies):
    # Create or overwrite the output file
    output_file = open('fresh_tomatoes.html', 'w')

    # Replace the movie tiles placeholder generated content
    rendered_content = main_page_content.format(
        movie_tiles=create_movie_tiles_content(movies))

    # Output the file
    output_file.write(main_page_head + rendered_content)
    output_file.close()

    # open the output file in the browser (in a new tab, if possible)
    # include chrome_path and .get() function because Chrome is only
    # natively supported by Python 3.3+
    url = os.path.abspath(output_file.name)
    chrome_p = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_p).open('file://' + url, new=2)
