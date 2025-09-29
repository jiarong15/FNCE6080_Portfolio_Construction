from .renderer_interface import RendererInterface

class BemWiderAreaPolygonRenderer(RendererInterface):
    def __init__(self, id):
        super(BemWiderAreaPolygonRenderer, self).__init__(id)
        self.renderer_name = "Bab el Mandeb Wider Area"
        
        # Coordinates for Bab el Mandeb wider area
        self.center_coordinates = (12.58, 43.33)
        self.polygon_coordinates = [
            [38, 18.0],
            [53.0, 16.5],
            [54, 14.0],
            [60.25, 10.0],
            [48.75, -6.0],
            [41.5667, -1.6667],
        ]
