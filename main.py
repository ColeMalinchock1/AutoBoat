from kivy_garden.mapview import MapView, MapMarker
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.graphics import *

import time
from geopy import distance

Builder.load_file('design.kv')

class LoadingScreen(Screen):

    def on_enter(self):
        Clock.schedule_interval(lambda dt: self.update_loading_text(), 1.0)

    def update_loading_text(self):
        if (self.checkGPS()):
            self.ids.loading_text.text = "GPS Found"

        else:
            if (self.ids.loading_text.text.count('.') == 3):
                self.ids.loading_text.text = "Waiting for GPS Signal"
            else:
                self.ids.loading_text.text += "."
    
    # Update to check for a valid GPS signal
    def checkGPS(self):
        return False

class SelectLocation(Screen):
    # Initializing lat, long, and zoom
    lat = long = zoom = 11

    # Initialize the mapview
    mapview = MapView(zoom = zoom, lat = lat, lon = long)

    markers = []

    last_marker_time = time.time()
    # Wait 2 seconds between each marker
    wait_time = 1

    # Initially checks if gps is available and uses that lat/long if not it keeps the same lat, long, zoom and creates map
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (self.check_GPS()):
            self.lat, self.long = self.get_GPS()
        self.create_map(self.lat, self.long, self.zoom)
        Clock.schedule_interval(lambda dt: self.update_position(), 1.0)
    
    # Checks if the GPS is available
    def check_GPS(self):
        return False

    # Gets the coordinates from the GPS
    def get_GPS(self):
        return None, None

    # Creates the map with the specified lat, long, zoom and makes it into a widget
    def create_map(self, la, lo, z):
        self.mapview.lat = la
        self.mapview.lon = lo
        self.mapview.zoom = z
        self.ids.map_container.add_widget(self.mapview)

    # Undo last marker that was placed
    def undo_marker(self):
        self.mapview.remove_marker(self.markers.pop())

        # Draw the lines between all the points
        self.draw_lines()

    # Add marker at current position
    def add_marker(self):

        if time.time() - self.last_marker_time > self.wait_time:
            self.ids.add_marker.text = "Wait"
            marker = MapMarker(lat = self.lat, lon = self.long, source = "Images/red_marker.png")
            self.mapview.add_widget(marker)
            self.markers.append(marker)
            self.last_marker_time = time.time()

            # Draw the lines between all the points
            self.draw_lines()

    # For entering a new position
    def enter_position(self):
        try:
            lat = float(self.ids.latitude.text)
            long = float(self.ids.longitude.text)
            self.ids.messenger.text = "Valid Lat/Long"
            if (lat is None or long is None):
                lat = 11
                long = 11
            self.mapview.lat = lat
            self.mapview.lon = long
            self.lat = lat
            self.long = long
            self.update_map_widget()
        except ValueError:
            self.ids.messenger.text = 'Invalid Lat/Long'

    def update_map_widget(self):
        # Remove the previous map widget
        self.ids.map_container.remove_widget(self.mapview)
        
        # Create a new map widget with updated coordinates
        self.mapview = MapView(zoom=self.zoom, lat=self.lat, lon=self.long)
        
        # Add the updated map widget back to the container
        self.ids.map_container.add_widget(self.mapview)

    def draw_lines(self):
        if len(self.markers) < 2:
            return
        
        for i in range(len(self.markers) - 1):

            d = int(distance.distance((self.markers[i].lat, self.markers[i].lon), (self.markers[i + 1].lat, self.markers[i + 1].lon)).meters)

            d = int(d / 5)
            delta_x = (self.markers[i + 1].lat - self.markers[i].lat) / d
            delta_y = (self.markers[i + 1].lon - self.markers[i].lon) / d
            x = self.markers[i].lat
            y = self.markers[i].lon
            
            for i in range(d):
                self.add_to_route(x + delta_x, y + delta_y)
                x += delta_x
                y += delta_y

    def add_to_route(self, lat, lon):
        while (time.time() - self.last_marker_time < self.wait_time):
            pass

        marker = MapMarker(lat = lat, lon = lon, source = "Images/red_dot.png")
        self.mapview.add_widget(marker)

    # Updates the current position of the red dot
    def update_position(self):
        if time.time() - self.last_marker_time < self.wait_time:
            self.ids.add_marker.text = "Wait"
        else:
            self.ids.add_marker.text = "Add Marker"
        prev_lat = self.lat
        prev_long = self.long
        self.lat, self.long = self.mapview.get_latlon_at(int(self.mapview.size[0]/2), int(self.mapview.size[1]/2), zoom = None)

    # Zooming in
    def zoom_in(self):
        self.zoom += 1
        self.mapview.zoom = self.zoom
    
    # Zooming out
    def zoom_out(self):
        self.zoom -= 1
        self.mapview.zoom = self.zoom
    
class MonitoringScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    # Creates the map with the specified lat, long, zoom and makes it into a widget
    def create_map(self):
        self.mapview.lat = self.lat
        self.mapview.lon = self.long
        self.mapview.zoom = self.zoom
        self.ids.map_container.add_widget(self.mapview)


class AAV_MonitoringApp(App):

    def build(self):
        sm = ScreenManager()
        Window.clearcolor = (230/255, 230/255, 230/255, 1)
        sm.add_widget(LoadingScreen(name='loading_screen'))
        sm.add_widget(SelectLocation(name='select_location'))
        sm.add_widget(MonitoringScreen(name='monitoring_screen'))

        return sm

if __name__ == '__main__':
    AAV_MonitoringApp().run()
