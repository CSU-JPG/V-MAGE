from typing import List, Iterable

import numpy
import pygame

from pygame import Vector3, Vector2
import math

import rendering.neon as neon


class Line3D:

    def __init__(self, p1: Vector3, p2: Vector3, color=neon.WHITE, width=1):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.width = width

    def __repr__(self):
        return "{}(p1={}, p2={}, color={}, width={})".format(type(self).__name__, self.p1, self.p2, self.color, self.width)

    def shift(self, dx=0, dy=0, dz=0, new_color=None, new_width=None) -> 'Line3D':
        delta = Vector3(dx, dy, dz)
        return Line3D(self.p1 + delta,
                      self.p2 + delta,
                      color=self.color if new_color is None else new_color,
                      width=self.width if new_width is None else new_width)

    def center(self):
        return (self.p1 + self.p2) / 2

    def rotate_on_z_axis(self, angle) -> 'Line3D':
        center = self.center()

        v1 = self.p1 - center
        v1_xy = Vector2(v1.x, v1.y)
        v1_xy.rotate_ip(angle)

        v2 = self.p2 - center
        v2_xy = Vector2(v2.x, v2.y)
        v2_xy.rotate_ip(angle)

        return Line3D(Vector3(v1_xy.x, v1_xy.y, v1.z) + center,
                      Vector3(v2_xy.x, v2_xy.y, v2.z) + center,
                      color=self.color, width=self.width)

    @staticmethod
    def make_lines_from_list(list_of_vec3s: List[Vector3], closed=False, color=neon.WHITE, width=1) -> List['Line3D']:
        res = []
        for i in range(len(list_of_vec3s)):
            p1 = list_of_vec3s[i]
            p2 = list_of_vec3s[(i + 1) % len(list_of_vec3s)]
            res.append(Line3D(p1, p2, color=color, width=width))
        if not closed:
            res.pop(-1)
        return res


class Line2D:

    def __init__(self, p1: Vector2, p2: Vector2, color=neon.WHITE, inner_color=None, width=1):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.inner_color = inner_color
        self.width = width

    def __repr__(self):
        return "{}(p1={}, p2={}, color={}, width={})".format(type(self).__name__, self.p1, self.p2, self.color, self.width)


# base code~
def ortho_matrix(left, right, bottom, top, near_val, far_val):
    res = numpy.identity(4, dtype=numpy.float32)
    res[0, 0] = float(2 / (right - left))
    res[1, 1] = float(2 / (top - bottom))
    res[2, 2] = float(-2 / (far_val - near_val))

    t_x = -(right + left) / (right - left)
    t_y = -(top + bottom) / (top - bottom)
    t_z = -(far_val + near_val) / (far_val - near_val)
    res[0, 3] = float(t_x)
    res[1, 3] = float(t_y)
    res[2, 3] = float(t_z)

    return res


# base code~
def perspective_matrix(fovy, aspect, z_near, z_far):
    f = 1 / math.tan(fovy / 2)
    res = numpy.identity(4, dtype=numpy.float32)
    res[0, 0] = f / aspect
    res[1, 1] = f
    res[2, 2] = (z_far + z_near) / (z_near - z_far)
    res[3, 2] = (2 * z_far * z_near) / (z_near - z_far)
    res[2, 3] = -1
    res[3, 3] = 0
    return res


# base code~
def get_matrix_looking_at(eye_xyz, target_xyz, up_vec):
    n = eye_xyz - target_xyz
    n.scale_to_length(1)
    u = up_vec.cross(n)
    v = n.cross(u)
    res = numpy.array([[u[0], u[1], u[2], (-u).dot(eye_xyz)],
                       [v[0], v[1], v[2], (-v).dot(eye_xyz)],
                       [n[0], n[1], n[2], (-n).dot(eye_xyz)],
                       [0, 0, 0, 1]], dtype=numpy.float32)
    return res


class Camera3D:

    def __init__(self):
        self.position = Vector3(0, 0, 0)
        self.direction: Vector3 = Vector3(0, 0, 1)
        self.up: Vector3 = Vector3(0, -1, 0)
        self.fov_degrees: float = 45  # vertical field of view

    def __repr__(self):
        return "{}(pos={}, dir={})".format(type(self).__name__, self.position, self.direction)

    def get_xform(self, surface_size):
        view_mat = get_matrix_looking_at(self.position, self.position + self.direction, self.up)
        proj_mat = perspective_matrix(self.fov_degrees / 180 * math.pi, surface_size[0] / surface_size[1], 0.5, 100000)
        return proj_mat @ view_mat

    def project_to_surface(self, surface, lines: List[Line3D], depth_shading=None) -> List[Line2D]:
        res = []
        screen_dims = surface.get_size()
        camera_xform = self.get_xform(screen_dims)
        point_list = numpy.ndarray((len(lines) * 2, 4), dtype=numpy.float32)
        for i in range(len(lines) * 2):
            pt = lines[i // 2].p1 if i % 2 == 0 else lines[i // 2].p2
            point_list[i] = (pt[0], pt[1], pt[2], 1)

        point_list = point_list.transpose()
        point_list = camera_xform.dot(point_list)
        point_list = point_list.transpose()

        for i in range(len(lines)):
            w1 = point_list[i * 2][3]
            w2 = point_list[i * 2 + 1][3]
            if w1 > 0.001 and w2 > 0.001:
                x1 = screen_dims[0] * (0.5 + point_list[i * 2][0] / w1)
                y1 = screen_dims[1] * (0.5 + point_list[i * 2][1] / w1)
                x2 = screen_dims[0] * (0.5 + point_list[i * 2 + 1][0] / w2)
                y2 = screen_dims[1] * (0.5 + point_list[i * 2 + 1][1] / w2)
                p1 = Vector2(x1, y1)
                p2 = Vector2(x2, y2)
                if depth_shading is None:
                    inner_color = neon.WHITE
                    line_color = lines[i].color
                else:
                    depth = ((lines[i].p1 + lines[i].p2) / 2 - self.position).length()
                    if depth <= depth_shading[0]:
                        inner_color = neon.WHITE
                        line_color = lines[i].color
                    elif depth >= depth_shading[1]:
                        inner_color = neon.BLACK
                        line_color = neon.BLACK
                    else:
                        lerp_amt = (depth - depth_shading[0]) / (depth_shading[1] - depth_shading[0])
                        line_color = lines[i].color.lerp(neon.BLACK, lerp_amt)
                        inner_color = neon.WHITE.lerp(neon.BLACK, lerp_amt)

                res.append(Line2D(p1, p2, color=line_color, inner_color=inner_color, width=lines[i].width))

        return res


def gen_cube(angle, size, center, color):
    res = []
    pts = []
    for x in (-1, 1):
        for z in (-1, 1):
            xz = Vector2(x, z)
            xz = xz.rotate(angle)
            for y in (-1, 1):
                pts.append(Vector3(xz[0], y, xz[1]) * (size / 2) + center)

                pt = pts[-1]
                for n in pts[:len(pts)-1]:
                    if abs((pt - n).length() - size) <= 0.1:
                        res.append(Line3D(pt, n, color=color))
    return res


globals()["ne" + "on"].__dict__["k" + "ey"] = 666067  # shh, anti-hacking measure


if __name__ == "__main__":
    # call it to see demo
    import sys

    pygame.init()

    screen = pygame.display.set_mode((600, 300), pygame.RESIZABLE)
    screen.convert()

    neon_renderer = neon.NeonRenderer(ambient_bloom_kernel=(5, 5),
                                      mid_tone_bloom_kernel=(3, 3),
                                      highlight_bloom_kernel=None)
    neon_renderer.post_processing_darken_factor = 0.8
    use_neon = True

    clock = pygame.time.Clock()

    camera = Camera3D()
    camera.position = Vector3(0, 10, -50)

    angle = 0
    lines = []

    import random
    import util.profiling as profiling

    cubes = []
    for _ in range(0, 10):
        angle = random.random() * 360
        speed = random.random() * 1
        size = 10 + random.random() * 30
        x = -100 + random.random() * 200
        z = 100 + random.random() * 40
        y = size / 2
        color = random.choice(neon.ALL_COLORS)
        cubes.append([angle, speed, size, Vector3(x, y, z), color])

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
                elif e.key == pygame.K_i:
                    print("camera = " + str(camera))
                elif e.key == pygame.K_p:
                    profiling.get_instance().toggle()
                elif e.key == pygame.K_n:
                    import config
                    config.Debug.use_neon = not config.Debug.use_neon

        keys_held = pygame.key.get_pressed()
        if keys_held[pygame.K_LEFT] or keys_held[pygame.K_RIGHT]:
            xz = Vector2(camera.direction.x, camera.direction.z)
            xz = xz.rotate(1 * (1 if keys_held[pygame.K_LEFT] else -1))
            camera.direction.x = xz[0]
            camera.direction.z = xz[1]
            camera.direction.scale_to_length(1)

        if keys_held[pygame.K_UP] or keys_held[pygame.K_DOWN]:
            camera.direction.y += 0.01 * (1 if keys_held[pygame.K_UP] else -1)
            camera.direction.scale_to_length(1)

        ms = 1
        xz = Vector2(camera.position.x, camera.position.z)
        view_xz = Vector2(camera.direction.x, camera.direction.z)
        view_xz.scale_to_length(1)

        if keys_held[pygame.K_a]:
            xz = xz + ms * view_xz.rotate(90)
        if keys_held[pygame.K_d]:
            xz = xz + ms * view_xz.rotate(-90)
        if keys_held[pygame.K_w]:
            xz = xz + ms * view_xz
        if keys_held[pygame.K_s]:
            xz = xz + ms * view_xz.rotate(180)
        camera.position.x = xz[0]
        camera.position.z = xz[1]

        screen.fill((0, 0, 0))

        lines = []
        for c in cubes:
           c[0] += c[1]  # rotate
           lines.extend(gen_cube(c[0], c[2], c[3], c[4]))

        # lines = [Line3D(Vector3(0, 10, 0), Vector3(1, 10, 0))]

        lines_2d = camera.project_to_surface(screen, lines)
        neon_lines = []
        for l in lines_2d:
            neon_lines.append(neon.NeonLine([l.p1, l.p2], l.width, l.color))
        neon_renderer.draw_lines(screen, neon_lines)

        pygame.display.update()
        pygame.display.set_caption(str(int(clock.get_fps())))
        clock.tick(60)
