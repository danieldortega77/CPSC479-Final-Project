import bpy
from math import *
from mathutils import *


# Clear all objects

meshes = set()

for obj in bpy.context.visible_objects:
    meshes.add(obj.data)
    bpy.data.objects.remove(obj)

for mesh in [m for m in meshes if m.users == 0]:
    bpy.data.meshes.remove(mesh)

# Add sun, planets, and moons

sun_rad = 10;
sun_rot_period = 5;

# Distance from origin of revolution
p1_dist = 50;
# Radius of sphere
p1_rad = 3;
# Period of revolution
p1_rev_period = 4
# Period of rotation
p1_rot_period = 1
# Stretch orbit: 1 = circle, 0.9 = ellipsoid, 0.7 = narrow ellipsoid
p1_ellipse_stretch = 0.9

m1_dist = 7;
m1_rad = 0.75;
m1_rev_period = 1
m1_rot_period = 0.5
m1_ellipse_stretch = 1.1

p2_dist = 100;
p2_rad = 2;
p2_rev_period = 10
p2_rot_period = 0.5
p2_ellipse_stretch = 0.8

m2_dist = 5;
m2_rad = 0.5;
m2_rev_period = 2
m2_rot_period = 0.25
m2_ellipse_stretch = 0.7

bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0), radius=sun_rad)
sun = bpy.context.object
sun.name = "Sun"

bpy.ops.mesh.primitive_uv_sphere_add(location=(p1_dist, 0, 0), radius=p1_rad)
p1 = bpy.context.object
p1.name = "Planet 1"
bpy.ops.mesh.primitive_uv_sphere_add(location=(p1_dist + m1_dist, 0, 0), radius=m1_rad)
m1 = bpy.context.object
m1.name = "Moon 1"

bpy.ops.mesh.primitive_uv_sphere_add(location=(p2_dist, 0, 0), radius=p2_rad)
p2 = bpy.context.object
p2.name = "Planet 2"
bpy.ops.mesh.primitive_uv_sphere_add(location=(p2_dist + m2_dist, 0, 0), radius=m2_rad)
m2 = bpy.context.object
m2.name = "Moon 2"

# Clear all previous animation data
for obj in bpy.context.visible_objects:
    obj.animation_data_clear()

runtime = 100
fps = 60
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = int(runtime * fps) + 1

# loop frames and insert keyframes every 10th frame
keyframe_freq = 10
lastFrame = bpy.context.scene.frame_end
for n in range(lastFrame):
    if n % keyframe_freq == 0:
        
        # Get current value for time
        
        t = runtime * n / lastFrame
        # Set current frame
        bpy.context.scene.frame_set(n)
        
        # Rotate spheres
        
        sun.rotation_euler = (0, 0, (t/sun_rot_period) % (2 * pi))
        
        p1.rotation_euler = (0, 0, (t/p1_rot_period) % (2 * pi))
        m1.rotation_euler = (0, 0, (t/m1_rot_period) % (2 * pi))
        
        p2.rotation_euler = (0, 0, (t/p2_rot_period) % (2 * pi))
        m2.rotation_euler = (0, 0, (t/m2_rot_period) % (2 * pi))
        
        # Translate spheres
        
        p1.location = Vector((sin(t/p1_rev_period) * p1_dist / p1_ellipse_stretch, cos(t/p1_rev_period) * p1_dist / (2 - p1_ellipse_stretch), 0))
        m1.location = Vector((sin(t/m1_rev_period) * m1_dist / m1_ellipse_stretch, cos(t/m1_rev_period) * m1_dist / (2 - m1_ellipse_stretch), 0)) + p1.location
        
        p2.location = Vector((sin(t/p2_rev_period) * p2_dist  / p2_ellipse_stretch, cos(t/p2_rev_period) * p2_dist / (2 - p2_ellipse_stretch), 0))
        m2.location = Vector((sin(t/m2_rev_period) * m2_dist / m2_ellipse_stretch, cos(t/m2_rev_period) * m2_dist / (2 - m2_ellipse_stretch), 0)) + p2.location

        # Make new keyframes
        
        sun.keyframe_insert(data_path="rotation_euler")
        p1.keyframe_insert(data_path="location")
        p1.keyframe_insert(data_path="rotation_euler")
        m1.keyframe_insert(data_path="location")
        m1.keyframe_insert(data_path="rotation_euler")
        p2.keyframe_insert(data_path="location")
        p2.keyframe_insert(data_path="rotation_euler")
        m2.keyframe_insert(data_path="location")
        m2.keyframe_insert(data_path="rotation_euler")

# Play the animation
bpy.ops.screen.animation_play()
