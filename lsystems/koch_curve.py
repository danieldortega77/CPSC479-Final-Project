import math
import random
from typing import Any, Union
import bpy

class Vector3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y =y
        self.z = z
    
    def __add__(self, other: 'Vector3'):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other: Any):
        if type(other) is type(self):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector3(other * self.x, other * self.y, other * self.z)

    def __rmul__(self, other: Any):
        return self.__mul__(other)

    def __sub__(self, other: 'Vector3'):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vector3(-1 * self.x, -1 * self.y, -1 * self.y)

    def __abs__(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        return self.__mul__(1/ self.__abs__()) 

    def project(self, other: 'Vector3'):
        normal = other.normalize()
        return normal * self.__mul__(normal)

    def __str__(self):
        return "({0},{1},{2})".format(self.x, self.y, self.z)

    def __pow__(self, other: 'Vector3'):
        return Vector3(self.y * other.z - other.y * self.z, - self.x * other.z + other.x * self.z, self.x * other.y - other.x * self.y)

    def to_list(self):
        return [self.x, self.y, self.z]

class ProductionRule(object):
    def __init__(self, input, outputs):
        self.input = input
        self.outputs = outputs
        self.n_outputs = len(outputs)

    def apply(self, input_string):
        new_string = ""
        for letter in input_string:
            if letter == self.input:
                r = (int)(self.n_outputs * random.random())
                new_string += self.outputs[r]
            else:
                new_string += letter
        return new_string

class LSystem(object):
    def __init__(self, production_rules, axiom):
        self.production_rules = production_rules
        self.current_iteration = axiom
        self.n_iterations = 0

    def iterate(self, n):
        for i in range(n):
            self.n_iterations += 1
            for production in self.production_rules:
                self.current_iteration = production.apply(self.current_iteration)

        return self.current_iteration

class Turtle(object):
    def __init__(self, location: Vector3, tangent: Vector3, normal: Vector3):
        self.location = location
        self.tangent = tangent.normalize()
        self.normal = normal.normalize()
        self.binormal = (tangent ** normal).normalize()

        self.delta = math.pi * 0.5
        self.branch_length = 1

        self.stack = []

    def process_word(self, word):
        for c in word:
            if c == '[':
                self.push_stack()
            elif c == ']':
                self.pop_stack()
            elif c == '+':
                self.rotate_tangent(self.delta)
            elif c == '-':
                self.rotate_tangent(-1 * self.delta)
            elif c == '&':
                self.rotate_normal(self.delta)
            elif c == '^':
                self.rotate_normal(-1 * self.delta)
            elif c == '\\':
                self.rotate_binormal(self.delta)
            elif c == '/':
                self.rotate_binormal(-1 * self.delta)
            elif c == 'F':
                self.move_forward(self.branch_length)

    def move_forward(self, length):
        old_location = self.location
        self.location += self.tangent * length

        self.draw_branch(old_location, self.location, self.normal, self.binormal)

    def draw_branch(self, start, end, normal, binormal):
        radius = 0.1
        vertices = []
        edges = []
        faces = []

        resolution = 10

        top_face = []
        bottom_face = []

        for i in range(0, resolution):
            theta = 2 * math.pi * i / resolution
            disp = math.cos(theta) * normal + math.sin(theta) * binormal
            vertices.append((end + radius * disp).to_list())
            vertices.append((start + radius * disp).to_list())

            top_face.append(2 * i + 1)
            bottom_face.append(2 * i)

        for i in range(0, resolution):
            bottom_v = 2 * i
            top_v = 2 * i + 1
            next_bottom_v = (2 * i + 2) % (2 * resolution)
            next_top_v = (2 * i + 3) % (2 * resolution)

            edges.append([bottom_v, top_v])
            edges.append([bottom_v, next_bottom_v])
            edges.append([top_v, next_top_v])

            faces.append([bottom_v, next_bottom_v, next_top_v, top_v])

        #faces.append(top_face)
        #faces.append(bottom_face)

        generate_mesh(vertices, edges, faces)

    def push_stack(self):
        current_state = {
            'location': self.location,
            'tangent': self.tangent,
            'normal': self.normal,
            'binormal': self.binormal
        }
        self.stack.append(current_state)

    def pop_stack(self):
        current_state = self.stack.pop()
        self.location = current_state['location']
        self.tangent = current_state['tangent']
        self.normal = current_state['normal']
        self.binormal = current_state['binormal']

    def rotate_tangent(self, delta):
        new_nor = math.cos(delta) * self.normal + math.sin(delta) * self.binormal
        new_bin = math.cos(delta) * self.binormal - math.sin(delta) * self.normal

        self.normal = new_nor.normalize()
        self.binormal = new_bin.normalize()

    def rotate_normal(self, delta):
        new_tan = math.cos(delta) * self.tangent + math.sin(delta) * self.binormal
        new_bin = math.cos(delta) * self.binormal - math.sin(delta) * self.tangent

        self.tangent = new_tan.normalize()
        self.binormal = new_bin.normalize()

    def rotate_binormal(self, delta):
        new_tan = math.cos(delta) * self.tangent + math.sin(delta) * self.normal
        new_nor = math.cos(delta) * self.normal - math.sin(delta) * self.tangent

        self.tangent = new_tan.normalize()
        self.normal = new_nor.normalize()

def generate_mesh(vertices, edges, faces):
    new_mesh = bpy.data.meshes.new('new_mesh')
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()

    new_object = bpy.data.objects.new('new_object', new_mesh)

    new_collection = bpy.data.collections.new('new_collection')
    bpy.context.scene.collection.children.link(new_collection)

    new_collection.objects.link(new_object)

p1 = ProductionRule('F', ['F^F&F&FF^F^F&F'])
axiom = 'F^F^F^F'

L = LSystem([p1], axiom)
word = L.iterate(2)

origin = Vector3(0,0,0)
e1 = Vector3(1,0,0)
e2 = Vector3(0,1,0)

T = Turtle(origin, e1, e2)
T.process_word(word)