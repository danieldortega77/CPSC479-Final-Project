import bpy
noise = bpy.data.texts['noise.py'].as_module()

pnf = noise.PerlinNoiseFactory(2, tile=(0, 3))

cube = bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
newMat = bpy.ops.material.new()
#noiseNode = bpy.ops.node.add_node(type="ShaderNodeTexNoise", use_transform=True)
