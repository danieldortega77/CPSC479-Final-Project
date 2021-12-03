import bpy
import math
import numpy as np

def v_index(i, j, n):
    return i * n + j

def interpolate_mesh(start_vertices, end_vertices, iterations):
    vertices = []
    edges = []
    faces = []

    difference_vectors = end_vertices - start_vertices
    n = len(start_vertices)

    for i in range(0, iterations + 1):
        for j in range(0, n):
            start_v = start_vertices[j]
            diff_v = difference_vectors[j]

            vertex = start_v + (1.0 * i / iterations) * diff_v

            vertices.append(list(vertex))

    for i in range(0, iterations + 1):
        for j in range(0, n):
            bottom_left = v_index(i, j, n)
            bottom_right = v_index(i, (j + 1) % n, n)

            edges.append([bottom_left, bottom_right])

            if i < iterations:
                top_left = v_index(i + 1, j, n)
                top_right = v_index(i + 1, (j+1) % n, n)

                edges += [
                    [bottom_left, top_left], 
                    [bottom_right, top_right], 
                    [top_left, top_right]
                ]

                faces.append([bottom_left, bottom_right, top_right, top_left])

    new_mesh = bpy.data.meshes.new('new_mesh')
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()

    new_object = bpy.data.objects.new('new_object', new_mesh)

    new_collection = bpy.data.collections.new('new_collection')
    bpy.context.scene.collection.children.link(new_collection)

    new_collection.objects.link(new_object)

def make_circle(x, y, z, r, n):
    center = np.array([x, y, z])
    theta = 2 * math.pi / n
    vertices = []
    for i in range(0, n):
        xi = r * math.cos(i * theta) + center[0]
        yi = r * math.sin(i * theta) + center[1]
        zi = z
        pi = np.array([xi, yi, zi])
        vertices.append(pi)
    return np.array(vertices)

def make_square(x,y,z,r,n):
    center = np.array([x,y,z])
    theta = 2 * math.pi / n
    side_offset = math.pi / 2
    offset = math.pi / 4
    vertices = []

    for i in range(0, n):
        side = int(i * 4 / n)
        ri = r / math.sqrt(2) / math.cos(i * theta - side * side_offset - offset)
        xi = ri * math.cos(i * theta) + center[0]
        yi = ri * math.sin(i * theta) + center[1]
        zi = z
        pi = np.array([xi, yi, zi])
        vertices.append(pi)
    return np.array(vertices)

def make_hexagon(x,y,z,r,n):
    center = np.array([x,y,z])
    theta = 2 * math.pi / n
    side_offset = math.pi / 3
    offset = math.pi / 6
    vertices = []

    for i in range(0, n):
        side = int(i * 6 / n)
        ri = r / math.cos(i * theta - side * side_offset - offset)
        xi = ri * math.cos(i * theta) + center[0]
        yi = ri * math.sin(i * theta) + center[1]
        zi = z
        pi = np.array([xi, yi, zi])
        vertices.append(pi)
    return np.array(vertices)
    
c1 = make_circle(0, 0, 0, 1, 100)
c2 = make_circle(0,0,10,2,100)

c3 = make_circle(10,0,0,1,100)
s1 = make_square(10,0,10,2,100)

s2 = make_square(0,10,0,1,100)
h1 = make_hexagon(0,10,10,2,100)

interpolate_mesh(c1, c2, 20)
interpolate_mesh(c3,s1,20)
interpolate_mesh(s2, h1, 20)
