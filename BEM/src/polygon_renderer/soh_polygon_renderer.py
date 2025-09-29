from .renderer_interface import RendererInterface

class SohPolygonRenderer(RendererInterface):
    def __init__(self, id):
        super(SohPolygonRenderer, self).__init__(id)
        self.renderer_name = "Straits of Hormuz"

        # Coordinates for Straits of Hormuz
        self.center_coordinates = (26.5667, 56.2500)
        self.polygon_coordinates = [
            [54.69052, 26.455261],
            [55.470373, 26.533921],
            [55.948171, 26.607616],
            [56.365557, 26.999851],
            [56.793928, 26.975376],
            [56.986145, 26.656719],
            [57.041065, 26.258376],
            [57.150904, 25.982175],
            [56.469905, 25.927845],
            [56.579744, 26.406071],
            [56.288672, 26.440506],
            [55.920713, 25.8982],
            [55.679182, 25.739403],
            [54.69052, 26.455261],
        ]
