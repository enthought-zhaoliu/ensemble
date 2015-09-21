import unittest

import numpy as np

from traits_enaml.testing.enaml_test_assistant import EnamlTestAssistant
from tvtk.api import tvtk

from ensemble.volren.volume_axes import VolumeAxes
from ensemble.volren.volume_bounding_box import VolumeBoundingBox
from ensemble.volren.volume_cut_planes import VolumeCutPlanes
from ensemble.volren.volume_data import VolumeData
from ensemble.volren.volume_viewer import VolumeViewer, CLIP_MAX


AXES_ACTOR_CLASS = tvtk.CubeAxesActor
CUT_PLANE_ACTOR_CLASS = tvtk.ImagePlaneWidget
CLIP_BOUNDS = [0, CLIP_MAX/2, 0, CLIP_MAX/2, 0, CLIP_MAX/2]


def count_types(type_class, obj_list):
    return sum(int(isinstance(obj, type_class)) for obj in obj_list)


class VolumeViewerTestCase(EnamlTestAssistant, unittest.TestCase):

    def setUp(self):

        EnamlTestAssistant.setUp(self)

        enaml_source = """
from enaml.widgets.api import Container
from ensemble.volren.volume_viewer_ui import VolumeViewerContainer

enamldef MainView(Container): view:
    attr viewer

    VolumeViewerContainer:
        viewer << view.viewer

"""
        volume = np.random.normal(size=(32, 32, 32))
        volume = (255*(volume-volume.min())/volume.ptp()).astype(np.uint8)
        volume_data = VolumeData(raw_data=volume)
        volume_axes = VolumeAxes(visible_axis_scales=(True, True, True))
        volume_bbox = VolumeBoundingBox()
        volume_cut_planes = VolumeCutPlanes()
        scene_members = {'axes': volume_axes, 'bbox': volume_bbox,
                         'cut_planes': volume_cut_planes}
        self.viewer = VolumeViewer(volume_data=volume_data,
                                   scene_members=scene_members,
                                   clip_bounds=CLIP_BOUNDS)
        self.view, _ = self.parse_and_create(enaml_source,
                                             viewer=self.viewer)

        with self.event_loop():
            self.view.show()

    def tearDown(self):
        self.view = None
        self.viewer = None
        EnamlTestAssistant.tearDown(self)

    def test_renderer_initialized(self):
        self.assertTrue(self.viewer.volume_renderer.volume is not None)

        # Count various actor types in the scene.
        # XXX: The actor class for `VolumeBoundingBox` is too generic to be
        # counted.
        scene_model = self.viewer.model
        axes_count = count_types(AXES_ACTOR_CLASS, scene_model.renderer.actors)
        cutplane_count = count_types(CUT_PLANE_ACTOR_CLASS,
                                     scene_model.actor_list)

        self.assertEqual(axes_count, 1)
        self.assertEqual(cutplane_count, 3)

    def test_renderer_clipping_bounds(self):
        self.assertEqual(self.viewer.volume_renderer.clip_bounds, CLIP_BOUNDS)

    def test_renderer_screenshot(self):
        # With default resolution
        image_array = self.viewer.screenshot()
        s1 = image_array.size
        self.assertTrue(image_array.ndim == 3)
        self.assertTrue(image_array.shape[-1] == 3)

        # With higher resolution
        magnification = 3
        image_array = self.viewer.screenshot(magnification=magnification)
        s2 = image_array.size
        self.assertTrue(image_array.ndim == 3)
        self.assertTrue(image_array.shape[-1] == 3)
        self.assertEqual(s2 / s1, magnification * magnification)

if __name__ == "__main__":
    unittest.main()
