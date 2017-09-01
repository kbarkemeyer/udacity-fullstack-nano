/**
* Model holding intial restaurant data, input for location filter and API key.
**/

var restaurants = [

    {
        name: "Teote",
        location: "SE",
        latitude: 45.511229,
        longitude: -122.653820
    },
    {
        name: "Ground Breaker Brewing",
        location: "SE",
        latitude: 45.508344,
        longitude: -122.658558
    },
    {
        name: "Harlow",
        location: "SE",
        latitude: 45.511968,
        longitude: -122.626219
    },
    {
        name: "Cultured Caveman",
        location: "NW",
        latitude: 45.582923,
        longitude: -122.687067
    },
    {
        name: "Verde Cocina",
        location: "SW",
        latitude: 45.4775825,
        longitude: -122.699932
    },
    {
        name: "A.N.D Cafe",
        location: "NE",
        latitude: 45.522738,
        longitude: -122.607904
    },
    {
        name: "Mi Metro Mole",
        location: "NW",
        latitude: 45.5236601,
        longitude: -122.675150
    },
    {
        name: "Dick\'s Kitchen",
        location: "SE",
        latitude: 45.527876,
        longitude: -122.694337
    },
    {
        name: "Besaws",
        location: "NW",
        latitude: 45.5339005,
        longitude: -122.695046
    },
    {
        name: "Tin Shed",
        location: "NE",
        latitude: 45.559009,
        longitude: -122.650898
    },
    {
        name: "White Owl Social Club",
        location: "SE",
        latitude: 45.513513,
        longitude: -122.657980
    },
    {
        name: "Andina",
        location: "NW",
        latitude: 45.526379,
        longitude: -122.684614
    },
    {
        name: "Departure",
        location: "SW",
        latitude: 45.519003,
        longitude: -122.677819
    }
];

var loc_filters = ["ALL", "NW", "NE", "SW", "SE"];

var MY_ZOMATO_API_KEY = "f3e8a3d60410ca2f0e76842421694061";


/**
* View model with operations performed on data.
**/

var ViewModel = function () {
    var self = this;

    // Google map.
    self.pdxmap = new google.maps.Map(document.getElementById("pdxmap"), {
        center: {
            lat: 45.534712,
            lng: -122.661035
        },
        zoom: 12
    });

    // Trigger recenter of map when appropriate.
    google.maps.event.addDomListener(window, "resize", function () {
        var center = self.pdxmap.getCenter();
        google.maps.event.trigger(self.pdxmap, "resize");
        self.pdxmap.setCenter(center);
    });

    // Create observable array to hold restuarant objects as markers.
    self.markers = ko.observableArray([]);

    /* Create a map marker for every restaurant in model and store in observable array.
    * Add @params address and addressShown as an observable arrays for every restaurant/marker, 
    * so address can be retrieved and displayed on click.
    * Add @params url and pic to be displayed on click in infowindow.
    */

    self.createMarker = function (name, location, latitude, longitude) {
        var pos = new google.maps.LatLng(latitude, longitude);
        var marker = new google.maps.Marker({
            position: pos,
            map: self.pdxmap,
            title: name,
            location: location,
            lat: latitude,
            lon: longitude,
            address: ko.observable(),
            url: null,
            pic: null,
            addressShown: ko.observable(false)
        });

        self.markers().push(marker);

        marker.addListener("click", function () {
            self.showAddress(marker);
        });
    };

    restaurants.forEach(function (r) {
        self.createMarker(r.name, r.location, r.latitude, r.longitude);
    });

    self.infoWindow = new google.maps.InfoWindow();

    // Function to display restaurant info on click.
    self.showAddress = function (data) {

        var API_KEY = MY_ZOMATO_API_KEY;
        var N = data.title;
        var LAT = data.lat;
        var LON = data.lon;

        var restaurantRequestTimeout = setTimeout(function () {
            alert("An error occured. Failed to retrieve restaurant details.");}, 8000);

        // API call to zomato.com to retrieve necessary info and add it to restaurant-markers.
        $.ajax({
            url: "https://developers.zomato.com/api/v2.1/search?q=" + N + "&lat=" + LAT + "&lon=" + LON + "&apikey=" + API_KEY,

            success: function (response) {
                data.address(response.restaurants[0].restaurant.location.address);
                data.url = response.restaurants[0].restaurant.url;
                data.pic = response.restaurants[0].restaurant.featured_image;

                if (!(data.pic)) {
                    data.pic = "Images/generic_photo.jpeg";
                }

                // Create infowindow content.
                var windowContent = '<div id="content">'+
                    '<div id="siteNotice">'+
                    '</div>'+
                    '<h3 id="firstHeading" class="firstHeading">' + data.title + '</h3>'+
                    '<div id="bodyContent">'+
                    '<div><img src="' + data.pic + '">' +
                    '<h5>' + data.address() + '</h5>' +
                    '<h4><a href="'+ data.url + '" target="_blank">More Info On Zomato.com</a></h4>' +
                    '</div>' +
                    '</div>' +
                    '</div>';

                // Go through filtered markers and show or hide restaurant address on click.
                self.filteredMarkers().forEach(function (mrk) {
                    if (data === mrk) {
                        mrk.addressShown(!mrk.addressShown());
                    } else {
                        mrk.addressShown(false);
                    }
                });

                // Close prior infowindow.
                if (self.infoWindow) {
                    self.infoWindow.close();
                }

                // Fill infowindow with new content.
                self.infoWindow.setContent(windowContent);

                // Go through filtered markers, set icon to appropriate color and open infowindow with new content.
                self.filteredMarkers().forEach(function (mrk) {
                    var icon = mrk.getIcon();
                    if (data.title === mrk.title && icon !== "https://www.google.com/mapfiles/marker_green.png") {
                        mrk.setIcon("https://www.google.com/mapfiles/marker_green.png");
                        self.infoWindow.open(self.pdxmap, mrk);
                    } else {
                        mrk.setIcon();
                    }
                });

                clearTimeout(restaurantRequestTimeout);

            },

            error: function () {
            alert("An error occured. Failed to retrieve restaurant details.");
            }
        });
    };

    self.loc_filters = loc_filters;

    // Set intial filter to All to display all restaurantw.
    self.selected_loc = ko.observable("ALL");

    /* 
    * ko computed function to apply filter to markers array.
    * Returns array of filtered markers to be diplayed in sidebar.
    * Sets map markers to visible accordingly, so only selected restaurants are shown as markers on map.
    * Closes inforwindow on every new select, resets all markers to initial state if ALL is selected.
    */

    self.filteredMarkers = ko.computed(function () {
        if (self.infoWindow) {
            self.infoWindow.close();
        }

        if (self.selected_loc() === "ALL") {
            ko.utils.arrayForEach(self.markers(), function (mrk) {
                mrk.setVisible(true);
                mrk.addressShown(false);
                mrk.setIcon();
            });
            var center = {lat: 45.534712, lng: -122.661035};
            self.pdxmap.setCenter(center);
            return self.markers();
        } else {
            ko.utils.arrayForEach(self.markers(), function (mrk) {
                if (mrk.location === self.selected_loc()) {
                    mrk.setVisible(true);
                } else {
                    mrk.setVisible(false);
                }
            });

            return ko.utils.arrayFilter(self.markers(), function (mrk) {
                return mrk.location === self.selected_loc();
            });
        }
    });

    // Open or close sidebar and resize map accordingly on click.
    // Adapted from tutorial at https://bootstrapious.com/p/bootstrap-sidebar
    $(document).ready(function () {
        $("#sidebarCollapse").on("click", function () {
            $("#sidebar").toggleClass("active");
            google.maps.event.trigger(self.pdxmap, "resize");
        });
    });

};

ko.applyBindings(new ViewModel());

