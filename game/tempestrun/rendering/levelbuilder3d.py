import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


from typing import List
from pygame import Vector3, Vector2
import math
import os
import traceback
import json
import time
import config
import rendering.threedee as threedee
import rendering.neon as neon
import util.utility_functions as utility_functions


def get_ring_points(z, level, rotation=None) -> List[Vector3]:
    n = level.number_of_lanes()
    radius = level.get_radius(z)
    if rotation is None:
        rotation = level.get_rotation(z)
    res = []
    for i in range(n):
        p = Vector3(radius, 0, z)
        p.rotate_ip(i * 360 / n + rotation, Vector3(0, 0, 1))
        res.append(p)
    return res


def build_section(z, length, level) -> List[threedee.Line3D]:
    ground_lines = []
    near_ring = get_ring_points(z, level)
    far_ring = get_ring_points(z + length, level)

    for i in range(level.number_of_lanes()):
        ground_lines.append(threedee.Line3D(near_ring[i], far_ring[i], color=level.get_color(z)))
        ground_lines.append(threedee.Line3D(far_ring[i], far_ring[i - 1], color=level.get_color(z)))

    return ground_lines


def get_rotation_to_make_lane_at_bottom(z, lane, level):
    unrotated_ring_pts = get_ring_points(z, level, rotation=0)
    pt_left = unrotated_ring_pts[(lane - 1) % level.number_of_lanes()]
    pt_right = unrotated_ring_pts[lane % level.number_of_lanes()]
    pt_center = (pt_left + pt_right) / 2
    res = Vector2(0, -1).as_polar()[1] - Vector2(pt_center.x, pt_center.y).as_polar()[1]
    if res < 0:
        res += 360
    return res


EXPLOSION_DURATION = 1  # second
EXPLOSION_DIST = 0.75      # units
EXPLOSION_ROT_SPEED = 20
EXPLOSION_SRC_POINT = Vector3(0, 0, 0)


def build_obstacle(obs, level, player) -> List[threedee.Line3D]:
    model = obs.get_model()

    if not config.Debug.jumping_enemies:
        # This makes enemies explode when you slide through them.
        time_dead = obs.get_time_dead()
        if time_dead > 1:
            return []  # it's gone
        elif time_dead <= 0:
            pass
        elif time_dead > 0:
            model = blow_up(model,
                            EXPLOSION_SRC_POINT,
                            EXPLOSION_DIST * (time_dead / EXPLOSION_DURATION),
                            rotation_speed=EXPLOSION_ROT_SPEED)
    else:
        # this makes enemies jump when the player approaches, so the player slides underneath them
        # instead of killing them. It makes it a little more clear that you can't jump over them,
        # but I don't really like it.
        if obs.should_rise_with_player() and (obs.lane - player.lane) % level.number_of_lanes() == 0:
            z_range = 30
            z_dist = abs(obs.z - player.z)
            if z_dist < z_range:
                model = [l.shift(dy=0.4 * (1 - z_dist / z_range)) for l in model]
    return align_shape_to_level_surface(model,
                                        obs.z,
                                        obs.z + obs.length,
                                        obs.lane,
                                        level,
                                        obs.should_squeeze())


def blow_up(lines: List[threedee.Line3D], from_pt: Vector3, amount, rotation_speed=30, axis=(0, 1)) -> List[threedee.Line3D]:
    res = []
    for l in lines:
        c = l.center()
        direction = c - from_pt
        if direction.length() < 0.001 or amount == 0:
            res.append(l)
        else:
            direction.scale_to_length(amount)
            dx = direction.x if 0 in axis else 0
            dy = direction.y if 1 in axis else 0
            dz = direction.z if 2 in axis else 0
            rot = rotation_speed * amount
            if direction.x < 0:
                rot = -rot
            res.append(l.rotate_on_z_axis(rot).shift(dx, dy, dz))
    return res


def build_rect(z_start, length, level, lane_n, hover_height, color, width, with_x=False) -> List[threedee.Line3D]:
    """Builds a 3D rectangle lying flat against the surface of the level."""
    near_ring = get_ring_points(z_start, level)
    far_ring = get_ring_points(z_start + length, level)
    corners = [near_ring[lane_n % level.number_of_lanes()],
               near_ring[(lane_n - 1) % level.number_of_lanes()],
               far_ring[(lane_n - 1) % level.number_of_lanes()],
               far_ring[lane_n % level.number_of_lanes()]]

    # make the rect hover a bit
    inset_corners = []
    for c in corners:
        hover_offset = Vector3(-c[0], -c[1], 0)
        hover_offset.scale_to_length(hover_height)
        inset_corners.append(c + hover_offset)

    res = [
        threedee.Line3D(inset_corners[0], inset_corners[1], color=color, width=width),
        threedee.Line3D(inset_corners[1], inset_corners[2], color=color, width=width),
        threedee.Line3D(inset_corners[2], inset_corners[3], color=color, width=width),
        threedee.Line3D(inset_corners[3], inset_corners[0], color=color, width=width)
    ]

    if with_x:
        res.append(threedee.Line3D(inset_corners[0], inset_corners[2], color=color, width=width))
        res.append(threedee.Line3D(inset_corners[1], inset_corners[3], color=color, width=width))

    return res


_CACHED_PLAYER_ART = {}


def load_player_art(w=0.8, h=0.5):
    
    
    min_x = float(1000)
    max_x = float(-1000)
    min_y = float(1000)
    max_y = float(-1000)

    anims = ["jump", "run", "slide"]

    # first pass just finds the max / mins of the set of animations
    for anim_name in anims:
        try:
            raw_path = "game/tempestrun/assets/wireframe_models/player/" + anim_name
            safe_path = utility_functions.resource_path(raw_path)

            for filename in sorted(os.listdir(safe_path)):
                if filename.endswith(".json"):
                    with open(utility_functions.resource_path(raw_path + "/" + filename)) as f:
                        for line in json.load(f):
                            for pt in line:
                                x = float(pt[0])
                                y = float(pt[1])
                                min_x = min(min_x, x)
                                max_x = max(max_x, x)
                                min_y = min(min_y, y)
                                max_y = max(max_y, y)
        except Exception:
            traceback.print_exc()

    # 2nd pass builds the actual lines
    # yes we're loading the files a 2nd time but it's 4am i don't care
    for anim_name in anims:
        frames = []
        try:
            raw_path = "game/tempestrun/assets/wireframe_models/player/" + anim_name
            safe_path = utility_functions.resource_path(raw_path)

            for filename in sorted(os.listdir(safe_path)):
                lines_for_frame = []
                lines_for_frame_xflip = []
                if filename.endswith(".json"):
                    with open(utility_functions.resource_path(raw_path + "/" + filename)) as f:
                        for line in json.load(f):
                            norm_pts = []
                            norm_pts_xflip = []
                            for pt in line:
                                x = float(pt[0])
                                y = float(pt[1])
                                norm_pts.append((
                                    utility_functions.map_from_interval_to_interval(x, [min_x, max_x], [-w/2, w/2]),
                                    utility_functions.map_from_interval_to_interval(y, [max_y, min_y], [0, h])
                                ))
                                norm_pts_xflip.append((
                                    utility_functions.map_from_interval_to_interval(x, [min_x, max_x], [w/2, -w/2]),
                                    utility_functions.map_from_interval_to_interval(y, [max_y, min_y], [0, h])
                                ))
                            lines_for_frame.append(threedee.Line3D(Vector3(norm_pts[0][0], norm_pts[0][1], 0),
                                                                   Vector3(norm_pts[1][0], norm_pts[1][1], 0)))
                            lines_for_frame_xflip.append(threedee.Line3D(Vector3(norm_pts_xflip[0][0], norm_pts_xflip[0][1], 0),
                                                                   Vector3(norm_pts_xflip[1][0], norm_pts_xflip[1][1], 0)))
                frames.append(lines_for_frame)
                frames.append(lines_for_frame_xflip)
            _CACHED_PLAYER_ART[anim_name] = frames
        except Exception:
            print("Exception loading player art of type: {}".format(anim_name))
        


def get_player_shape_at_origin(player) -> List[threedee.Line3D]:

    player_mode = player.get_mode() if not player.is_dead() else player.get_last_mode_before_death()

    art_to_use = None
    if player_mode == 'jump':
        art_to_use = "jump"
    elif player_mode == 'slide':
        art_to_use = "slide"
    else:
        art_to_use = "run"

    dist_from_ground = 0.3 * player.y / player.max_jump_height()
    color = neon.YELLOW if not player.is_dead() else neon.RED
    width = 2

    if len(_CACHED_PLAYER_ART) == 0:
        load_player_art()
        
    if not config.Display.use_player_art or art_to_use not in _CACHED_PLAYER_ART or len(_CACHED_PLAYER_ART[art_to_use]) == 0:
        # just a rectangle
        width = 0.5 if not player.is_sliding() else 0.6
        height = 0.4 if not player.is_sliding() else 0.2
        top_left = Vector3(-width / 2.0, height + dist_from_ground, 0)
        top_right = Vector3(width / 2.0, height + dist_from_ground, 0)
        bot_left = Vector3(-width / 2.0, dist_from_ground, 0)
        bot_right = Vector3(width / 2.0, dist_from_ground, 0)

        return [threedee.Line3D(top_left, top_right, color=color, width=width),
                threedee.Line3D(top_right, bot_right, color=color, width=width),
                threedee.Line3D(bot_right, bot_left, color=color, width=width),
                threedee.Line3D(bot_left, top_left, color=color, width=width)]
    else:
        frame_n = int(player.z) // 20
        all_frames = _CACHED_PLAYER_ART[art_to_use]
        lines_in_frame = all_frames[frame_n % len(all_frames)]
        return [l.shift(dy=dist_from_ground, new_color=color, new_width=width) for l in lines_in_frame]


def get_player_shape(player, level) -> List[threedee.Line3D]:
    shape_2d = get_player_shape_at_origin(player)
    if player.is_dead():
        death_dur = player.get_time_dead()
        if death_dur > EXPLOSION_DURATION:
            return []
        elif death_dur > 0:
            shape_2d = blow_up(shape_2d,
                               EXPLOSION_SRC_POINT,
                               EXPLOSION_DIST * (death_dur / EXPLOSION_DURATION),
                               2 * EXPLOSION_ROT_SPEED)
    return align_shape_to_level_surface(shape_2d, player.z, player.z, player.lane, level, squeeze=False)


def align_shape_to_level_surface(lines_to_xform: List[threedee.Line3D], z_start: float, z_end: float, lane_n: int, level, squeeze=False) -> List[threedee.Line3D]:
    """
    :param lines_to_xform: the shape to transform
    :param z_start: z position of the object in the level
    :param z_end: end z position of the object in the level
    :param lane_n: lane the object is in
    :param squeeze: whether the object should be "squeezed" inward as it approaches the center of the level
                    (this is needed for things like walls that should meet each other cleanly at their boundaries).
    :return: a new set of Line3Ds, aligned to the level
    """
    if z_start == z_end:
        z_end += 0.001

    near_ring_pts = get_ring_points(z_start, level)
    far_ring_pts = get_ring_points(z_end, level)

    near_left = near_ring_pts[(lane_n - 1) % level.number_of_lanes()]
    near_right = near_ring_pts[lane_n % level.number_of_lanes()]
    near_top = Vector3(0, 0, z_start)
    near_bottom = (near_left + near_right) / 2

    near_normal_vec = near_top - near_bottom
    near_normal_vec.scale_to_length(1)

    far_left = far_ring_pts[(lane_n - 1) % level.number_of_lanes()]
    far_right = far_ring_pts[lane_n % level.number_of_lanes()]
    far_top = Vector3(0, 0, z_end)
    far_bottom = (far_left + far_right) / 2

    far_normal_vec = far_top - far_bottom
    far_normal_vec.scale_to_length(1)

    res = []

    def convert_pt(pt):
        z_factor = utility_functions.map_from_interval_to_interval(pt.z, [-1, 1], [0, 1])
        vert_factor = pt.y
        horz_factor = utility_functions.map_from_interval_to_interval(pt.x, [-1, 1], [0, 1])

        if not squeeze:
            near_pt = near_left + horz_factor * (near_right - near_left) + vert_factor * (near_top - near_bottom)
            far_pt = far_left + horz_factor * (far_right - far_left) + vert_factor * (far_top - far_bottom)
            return utility_functions.lerp(z_factor, near_pt, far_pt)
        else:
            near_pt = utility_functions.lerp(vert_factor, near_left + horz_factor * (near_right - near_left), near_top)
            far_pt = utility_functions.lerp(vert_factor, far_left + horz_factor * (far_right - far_left), far_top)
            return utility_functions.lerp(z_factor, near_pt, far_pt)

    for l in lines_to_xform:
        new_p1 = convert_pt(l.p1)
        new_p2 = convert_pt(l.p2)
        res.append(threedee.Line3D(new_p1, new_p2, color=l.color, width=l.width))

    return res
