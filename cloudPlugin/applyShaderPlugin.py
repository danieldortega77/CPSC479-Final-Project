import bpy

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.shading_system = True



mat_name = "CloudTest"

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

objects = bpy.context.selected_objects

for i in range(len(objects)):
    mat = bpy.data.materials.get(mat_name)
    if objects[i].data.materials:
        objects[i].data.materials[0] = mat
    else:
        objects[i].data.materials.append(mat)