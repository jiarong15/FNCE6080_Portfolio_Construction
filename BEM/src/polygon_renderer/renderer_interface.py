# from abc import ABC, abstractmethod
from shapely.geometry import Point, Polygon as shapelyPolygon
from ipyleaflet import Map, Polygon as ipyPolygon
from IPython.display import display

class RendererInterface:
    def __init__(self, id):
        self.id = id

    def build_and_render_map(self):
        map = Map(center=self.center_coordinates, zoom=3.5)
        polygon = ipyPolygon(
            locations=self.polygon_coordinates,
            color="blue",
            fill_color="blue",
            fill_opacity=0.5
        )
        map.add_layer(polygon)
        map.save(f'/reports/{self.renderer_name} map.jpeg')
        display(map)
    
    def is_in_region(self, lon, lat):
        point = Point(lon, lat)
        # point = Point(lat, lon)
        return any(shapelyPolygon(poly_coords).contains(point) for poly_coords in [shapelyPolygon(self.polygon_coordinates)])
    
    def get_polygon_coordinates(self):
        return self.polygon_coordinates
    
    def get_center_coordinates(self):
        return self.center_coordinates
    
    def __repr__(self):
        return f"{self.id}. {self.renderer_name}"


