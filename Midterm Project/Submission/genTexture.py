import bpy

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.shading_system = True

texture_names = ["Fire",  "Marble", "Turbulence", "Water"]


for name in texture_names:
    mat_name = name

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
    scriptNode.location = (0,0)
    scriptNode.script = bpy.data.texts[name.lower() + ".osl"]

    outNode = nodes.new("ShaderNodeOutputMaterial")
    outNode.location = (200,0)


    # Connect the two nodes
    links.new(scriptNode.outputs[0], outNode.inputs[0])

objects = bpy.data.objects

for i in range(len(objects)):
    mat = bpy.data.materials.get(texture_names[i % len(texture_names)])
    if objects[i].data.materials:
        objects[i].data.materials[0] = mat
    else:
        objects[i].data.materials.append(mat)