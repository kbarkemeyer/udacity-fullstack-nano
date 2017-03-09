import movies
import fresh_tomatoes

Amy = movies.Movie("Amy",
                   "2015 documentary by Asif Kapadia",
                   "https://images-na.ssl-images-amazon.com/images/M/MV5BMTQ1MzE4MTE3OF5BMl5BanBnXkFtZTgwOTcyNDM3NTE@._V1_SY1000_CR0,0,674,1000_AL_.jpg",  # NOQA
                   "https://www.youtube.com/watch?v=_2yCIwmNuLE")


Gegen_die_Wand = movies.Movie("Gegen die Wand",
                              "2004 German-Turkish drama by Fatih Akin in 2004",  # NOQA
                              "https://images-na.ssl-images-amazon.com/images/M/MV5BMjE2OTkxMTk0NF5BMl5BanBnXkFtZTcwMjk5MTAzMQ@@._V1_.jpg",  # NOQA
                              "https://www.youtube.com/watch?v=I93Hv44kQWA")


Talk_to_her = movies.Movie("Hable con ella",
                           "2002 Spanish drama/romance Pedro Almodovar",
                           "http://ia.media-imdb.com/images/M/MV5BMTczNTU2NjIwOF5BMl5BanBnXkFtZTYwNzExMDg5._V1_.jpg",  # NOQA
                           "https://www.youtube.com/watch?v=iAdqAcfJvN8")


Im_Juli = movies.Movie("Im Juli",
                        "2000 German-Turkish road movie/romance by Fatih Akin",
                        "https://images-na.ssl-images-amazon.com/images/M/MV5BMTIwMTM0MzMzNF5BMl5BanBnXkFtZTcwMTczNTUyMQ@@._V1_.jpg",  # NOQA
                        "https://www.youtube.com/watch?v=Mr7WImqnKBM")


East_is_East = movies.Movie("East is East",
                            "1999 British comedy-drama by Ayub Khan-Din and Damien O'Donnell",  # NOQA
                            "http://ia.media-imdb.com/images/M/MV5BMTI0MDk3ODQ4M15BMl5BanBnXkFtZTcwMDQ1NDkyMQ@@._V1_.jpg",  # NOQA
                            "https://www.youtube.com/watch?v=cwz74AcIC-o")


Mifune = movies.Movie("Mifunes sidste sang",
                      "1999 Danish romantic drama by Soren Kragh-Jacobsen",
                      "https://images-na.ssl-images-amazon.com/images/M/MV5BMTIzOTY4NDA4OF5BMl5BanBnXkFtZTYwNDIwMTg4._V1_.jpg",  # NOQA
                      "https://www.youtube.com/watch?v=o6PsTbD8tZQ")


fav_movies = (Amy, Gegen_die_Wand, Talk_to_her, Im_Juli, East_is_East, Mifune)
fresh_tomatoes.open_movies_page(fav_movies)
