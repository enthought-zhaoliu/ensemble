from __future__ import unicode_literals
from .base_color_function_component import BaseColorComponent, ColorNode
from .function_component import register_function_component_class
from .function_node import register_function_node_class


COMPONENT_WIDTH = 6.0


class ColorComponent(BaseColorComponent):

    # Let the user know that we can be moved
    hover_pointer = 'hand'

    def add_function_nodes(self, transfer_function):
        """ Add the node(s) for this component.
        """
        transfer_function.color.insert(self.node)

    def draw_contents(self, gc):
        """ Draw the component.
        """
        r, g, b = self.node.color
        screen_x, height = self.relative_to_screen(self.node.center, 1.0)

        with gc:
            gc.set_line_width(1.0)
            gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))
            # FIXME: Bad choice of contrasting color for grays.
            opposite_color = (1.0 - r, 1.0 - g, 1.0 - b, 1.0)
            gc.set_fill_color(opposite_color)
            gc.rect(screen_x - COMPONENT_WIDTH/2.0, 0, COMPONENT_WIDTH, height)
            gc.draw_path()

    @classmethod
    def from_function_nodes(cls, *nodes):
        """ Create an instance from `nodes`.
        """
        if len(nodes) > 1 or not isinstance(nodes[0], ColorNode):
            raise ValueError('Expecting a ColorNode instance!')

        return cls(node=nodes[0])

    def move(self, delta_x, delta_y):
        """ Move the component.
        """
        rel_x, _ = self.screen_to_relative(delta_x, 0.0)
        self.update_node_center(self.node, rel_x)
        self._sync_component_position()

    def node_limits(self, transfer_function):
        """ Compute the movement bounds of the function node.
        """
        limits = transfer_function.color.node_limits(self.node)
        radius = self.node.radius
        return (limits[0] + radius, limits[1] - radius)

    def parent_changed(self, parent):
        """ Called when the parent of this component changes instances or
        bounds.
        """
        self.bounds = (COMPONENT_WIDTH, parent.bounds[1])
        self._sync_component_position()

    def remove_function_nodes(self, transfer_function):
        """ Remove the node(s) for this component.
        """
        transfer_function.color.remove(self.node)

    # -----------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------

    def _sync_component_position(self):
        screen_x, _ = self.relative_to_screen(self.node.center, 0.0)
        self.position = (screen_x - COMPONENT_WIDTH/2.0, 0.0)


# Register our function node
register_function_node_class(ColorNode)
# ... and our function component
register_function_component_class(ColorNode, ColorComponent)
