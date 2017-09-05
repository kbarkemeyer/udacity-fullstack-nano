function mapLoaded() {
    initialize("withMap");
}

function mapNotLoaded() {
    initialize("withoutMap")
}

function initialize(param) {
    var mapValue = param;

    var MY_ZOMATO_API_KEY = "f3e8a3d60410ca2f0e76842421694061";

    /**
    * View model with operations performed on data.
    **/

    var ViewModel = function () {
        var self = this;

        // If all goes well with google maps api proceed with default features. 
        if (mapValue === "withMap") {
            self.googleMapsError = ko.observable(false);

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
                                self.pdxmap.panTo(mrk.getPosition());
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

            self.locFilters = ["ALL"];

            restaurants.map(r => {
                if (!self.locFilters.includes(r.location)) {
                    self.locFilters.push(r.location);
                }
            });

            // Set intial filter to All to display all restaurantw.
            self.selectedLoc = ko.observable("ALL");

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

                if (self.selectedLoc() === "ALL") {
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
                        if (mrk.location === self.selectedLoc()) {
                            mrk.setVisible(true);
                        } else {
                            mrk.setVisible(false);
                        }
                    });

                    return ko.utils.arrayFilter(self.markers(), function (mrk) {
                        return mrk.location === self.selectedLoc();
                    });
                }
            });

        } else { 
            // In case google map error just create list of restaurants and display error message instead of map.

            self.googleMapsError = ko.observable(true); // Observable which takes boolean value to signal to knockout that google map error occurred.

            self.restList = ko.observableArray([]);

            for (r in restaurants) {
                restaurants[r].title = restaurants[r].name;
                restaurants[r].addressShown = false;
                restaurants[r].address = "";
            }

            restaurants.forEach(function(rest) {
                self.restList.push(rest);
            });

            self.locFilters = ["ALL"];

            restaurants.map(r => {
                if (!self.locFilters.includes(r.location)) {
                    self.locFilters.push(r.location);
                }
            });

            self.selectedLoc = ko.observable("ALL");

            self.filteredMarkers = ko.computed(function () {
                if (self.selectedLoc() === "ALL") {
                    return self.restList();
                } else {
                    return ko.utils.arrayFilter(self.restList(), function(r) {
                        return r.location === self.selectedLoc();
                    });
                }
            });
        }

        // Open or close sidebar and resize map accordingly on click.
        
        self.activated = ko.observable(false);
        
        self.toggleActive = function() {
            self.activated(!self.activated());
            google.maps.event.trigger(self.pdxmap, "resize");
        }

    };

    ko.applyBindings(new ViewModel());

}

