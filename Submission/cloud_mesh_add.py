import bpy
import bmesh
from bpy_extras.object_utils import AddObjectHelper

from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
)


def add_box(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [
        (+1.0, +1.0, -1.0),
        (+1.0, -1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (-1.0, +1.0, -1.0),
        (+1.0, +1.0, +1.0),
        (+1.0, -1.0, +1.0),
        (-1.0, -1.0, +1.0),
        (-1.0, +1.0, +1.0),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces


class AddClouds(bpy.types.Operator, AddObjectHelper):
    """Add a simple cloud mesh"""
    bl_idname = "mesh.primitive_clouds_add"
    bl_label = "Clouds"
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name="Width",
        description="Clouds Width",
        min=0.01, max=100.0,
        default=10.0,
    )
    height: FloatProperty(
        name="Height",
        description="Clouds Height",
        min=0.01, max=100.0,
        default=1.0,
    )
    depth: FloatProperty(
        name="Depth",
        description="Clouds Depth",
        min=0.01, max=100.0,
        default=10.0,
    )
    scale: FloatProperty(
        name="Scale",
        description="Scale of cloud texture within volume",
        min=0.01, max=100.0,
        default=5.0,
    )
    time_rate: FloatProperty(
        name="Time Rate",
        description="Rate of change within cloud texture",
        min=0.01, max=100.0,
        default=1.0,
    )
    wind_rate: FloatProperty(
        name="Wind Rate",
        description="Rate of change within cloud texture",
        min=0.01, max=100.0,
        default=1.0,
    )
    wind_direction: FloatVectorProperty(
        name = "Wind Direction",
        description="Direction cloud texture will move within the volume",
        default=[3.0,2.0,1.0],
    )

    def execute(self, context):

        verts_loc, faces = add_box(
            self.width,
            self.height,
            self.depth,
        )

        mesh = bpy.data.meshes.new("Clouds")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        bm.to_mesh(mesh)
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        cloudObject = object_utils.object_data_add(context, mesh, operator=self)

        # Add cloud texture to mesh
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.shading_system = True

        mat_name = "Clouds"

        # Test if material exists
        # If it does not exist, create it:
        mat = (bpy.data.materials.get(mat_name) or 
            bpy.data.materials.new(mat_name))

        # Enable 'Use nodes':
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Remove any old nodes that exist in material
        for node in nodes:
            nodes.remove(node)

        # Create new nodes
        scriptNode = nodes.new('ShaderNodeScript')
        scriptNode.location = (-300,0)
        scriptNode.script = bpy.data.texts["turbulence.osl"]
        scriptNode.inputs[4].default_value = self.scale

        colorRampNode = nodes.new(type="ShaderNodeValToRGB")
        colorRampNode.color_ramp.elements[0].color = (0, 0, 0, 1)
        colorRampNode.color_ramp.elements[0].position = 0.45
        colorRampNode.color_ramp.elements[1].color = (1, 1, 1, 1)
        colorRampNode.color_ramp.elements[1].position = 0.9
        colorRampNode.color_ramp.interpolation = 'EASE'
        colorRampNode.location = (-100,0)

        volumeNode = nodes.new("ShaderNodeVolumePrincipled")
        volumeNode.inputs[0].default_value = (1, 1, 1, 1)
        volumeNode.location = (200,0)


        outNode = nodes.new("ShaderNodeOutputMaterial")
        outNode.location = (500,0)


        # Connect the two nodes
        links.new(scriptNode.outputs[0], colorRampNode.inputs[0])
        links.new(colorRampNode.outputs[0], volumeNode.inputs[2])
        links.new(volumeNode.outputs[0], outNode.inputs[1])

        # Apply cloud material to object
        mat = bpy.data.materials.get(mat_name)
        cloudObject.data.materials.append(mat)
        cloudObject.data.materials[0] = mat

        # Add keyframes to clouds
        
        time_rate = self.time_rate
        wind_rate = self.wind_rate
        wind_direction = self.wind_direction
        runtime = 10
        fps = 24
        
        lastFrame = int(runtime * fps)
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = lastFrame
        
        # Add procedural animation over time to cloud texture
        # 
        # First frame
        bpy.context.scene.frame_set(0)
        # Set time value of texture
        scriptNode.inputs[1].default_value = 0
        scriptNode.inputs[1].keyframe_insert("default_value")
        # Set 3D translation of texture within the volume
        scriptNode.inputs[3].default_value = [0, 0, 0]
        scriptNode.inputs[3].keyframe_insert("default_value")

        # Last frame
        bpy.context.scene.frame_set(lastFrame)
        # Set time value of texture
        scriptNode.inputs[1].default_value = runtime / 1000 * time_rate
        scriptNode.inputs[1].keyframe_insert("default_value")
        # Set 3D translation of texture within the volume
        wind_rate *= runtime / 10
        scriptNode.inputs[3].default_value = [-x * wind_rate for x in wind_direction]
        scriptNode.inputs[3].keyframe_insert("default_value")

        # Set to linear interpolation
        area = bpy.context.area
        old_type = area.type
        area.type = 'DOPESHEET_EDITOR'
        bpy.ops.action.interpolation_type(type='LINEAR')
        area.type = old_type

        # Play the animation
        bpy.ops.screen.animation_play()

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddClouds.bl_idname, icon='MESH_CUBE')

# Register and add to the "add mesh" menu (required to use F3 search "Add Box" for quick access)
def register():
    bpy.utils.register_class(AddClouds)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddClouds)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.mesh.primitive_clouds_add()
