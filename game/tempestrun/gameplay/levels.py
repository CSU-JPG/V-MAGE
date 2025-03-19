from typing import List
from pygame import Vector3, Color
from rendering.threedee import Line3D
import rendering.neon as neon
import util.utility_functions as utils
import time
import random


class Obstacle:
    """Base class for obstacles"""

    def __init__(self, lane, z, length, color, can_jump_over, can_slide_through, can_run_through=False):
        # the lane the obstacle covers
        self.lane = lane

        # obstacle's position and size in the z-axis
        self.z = z
        self.length = length

        self.color = color

        self._can_jump = can_jump_over
        self._can_slide_through = can_slide_through
        self._can_run_through = can_run_through

        self._is_dead = False
        self._dead_since = 0  # time of death, in seconds (since the the epoch)

        # used to avoid recreating the 3D model every frame
        # will be a List[Line3D] if present
        self._cached_3d_model = None

    def get_death_message(self):
        return "avoid obstacles!"

    def get_color(self):
        return self.color

    def should_squeeze(self):
        return True

    def should_rise_with_player(self):
        return False

    def handle_potential_collision(self, player) -> bool:
        """
        :return: whether the player should die as a result of this collision.
        """
        if player.is_dead() or self._is_dead:
            return False
        if player.z + player.length / 2 < self.z or self.z + self.length < player.last_z_pos:
            return False

        if player.is_jumping():
            if not self.can_jump_over():
                return True
            else:
                return player.y <= self.get_jump_clearance_height()
        elif player.is_sliding():
            if self.can_slide_through():
                # this kills the crab
                self._handle_death()
                return False
            else:
                return True
        elif player.is_running():
            return not self.can_run_through()
        else:
            return False

    def _handle_death(self):
        if not self._is_dead:
            self._is_dead = True
            
            self._dead_since = time.time()

    def can_jump_over(self):
        return self._can_jump

    def can_run_through(self):
        return self._can_run_through

    def get_time_dead(self):
        if self._is_dead:
            return time.time() - self._dead_since
        else:
            return -1

    def get_jump_clearance_height(self):
        return 0.1

    def can_slide_through(self):
        return self._can_slide_through

    def get_model(self) -> List[Line3D]:
        """
        :return: a 3D representation of the obstacle, as if its corners were at:
            [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0)],
            and facing upwards in the z-axis.
        """
        if self._cached_3d_model is None:
            self._cached_3d_model = self.generate_3d_model_at_origin()

        return self._cached_3d_model

    def generate_3d_model_at_origin(self) -> List[Line3D]:
        """Generates the obstacle's 3D model from scratch."""
        return [
            # basic square outline
            Line3D(Vector3(-1, 0, 1), Vector3(1, 0, 1), color=self.get_color()),
            Line3D(Vector3(1, 0, 1), Vector3(1, 0, -1), color=self.get_color()),
            Line3D(Vector3(1, 0, -1), Vector3(-1, 0, -1), color=self.get_color()),
            Line3D(Vector3(-1, 0, -1), Vector3(-1, 0, 1), color=self.get_color()),
            # 'X' through the middle
            Line3D(Vector3(-1, 0, 1), Vector3(1, 0, -1), color=self.get_color()),
            Line3D(Vector3(1, 0, 1), Vector3(-1, 0, -1), color=self.get_color())
        ]


class Spikes(Obstacle):

    def __init__(self, lane, z, length):
        super().__init__(lane, z, length, neon.RED, True, False)

    def get_death_message(self):
        return "jump over spikes!"

    def generate_3d_model_at_origin(self) -> List[Line3D]:
        height = 0.2
        pts = [
            Vector3(-1, 0, 0),
            Vector3(-0.8, height, 0),
            Vector3(-0.4, 0, 0),
            Vector3(0, height, 0),
            Vector3(0.4, 0, 0),
            Vector3(0.8, height, 0),
            Vector3(1, 0, 0)
        ]
        return Line3D.make_lines_from_list(pts, closed=True, color=self.get_color())


class Enemy(Obstacle):
    """An obstacle you can slide through"""

    def __init__(self, lane, z, length):
        super().__init__(lane, z, length, neon.LIME, False, True)

    def get_death_message(self):
        return "slide through enemies!"

    def should_squeeze(self):
        return False

    def should_rise_with_player(self):
        return True

    def generate_3d_model_at_origin(self) -> List[Line3D]:
        # ooh, scary
        bot_left = Vector3(-0.5, 0.1, 0)
        bot_right = Vector3(0.5, 0.1, 0)
        top_left = Vector3(-0.5, 0.3, 0)
        top_right = Vector3(0.5, 0.3, 0)
        outline = Line3D.make_lines_from_list([bot_left, bot_right, top_right, top_left], closed=True, color=self.get_color())
        left_eye = Line3D(Vector3(-.4, 0.25, 0), Vector3(-.1, 0.2, 0), color=self.get_color())
        right_eye = Line3D(Vector3(0.4, 0.25, 0), Vector3(.1, 0.2, 0), color=self.get_color())
        mouth = Line3D(Vector3(-0.4, 0.15, 0), Vector3(0.4, 0.15, 0), color=self.get_color())
        return outline + [left_eye, right_eye, mouth]


class Wall(Obstacle):
    """An obstacle you can neither slide through nor jump over."""

    def __init__(self, lane, z, length):
        super().__init__(lane, z, length, neon.PURPLE, False, False)

    def get_death_message(self):
        return "avoid walls!"

    def generate_3d_model_at_origin(self) -> List[Line3D]:
        height = 0.5

        # TODO do we want something "truly" 3D? it's a bit weird looking
        # l1 = Vector3(-1, 0, -1)
        # l2 = Vector3(-1, 0, 1)
        # r1 = Vector3(1, 0, -1)
        # r2 = Vector3(1, 0, 1)
        #
        # top_left = Vector3(-1, height, 0)
        # top_right = Vector3(1, height, 0)
        #
        # ground_square = Line3D.make_lines_from_list([l1, l2, r2, r1], closed=True, color=self.get_color())
        # front_face = Line3D.make_lines_from_list([l1, top_left, top_right, r1], closed=False, color=self.get_color())
        # extra_lines = [
        #     Line3D(top_left, l2, color=self.get_color()),
        #     Line3D(top_right, r2, color=self.get_color()),
        #     Line3D(l1, top_right, color=self.get_color()),
        #     Line3D(r1, top_left, color=self.get_color())
        # ]
        #
        # return ground_square + front_face + extra_lines

        l1 = Vector3(-1, 0, 0)
        l2 = Vector3(-1, height, 0)
        r1 = Vector3(1, 0, 0)
        r2 = Vector3(1, height, 0)

        return Line3D.make_lines_from_list([l1, l2, r2, r1], closed=True, color=self.get_color()) + \
            [Line3D(l1, r2, color=self.get_color()),
             Line3D(l2, r1, color=self.get_color())]


class Level:
    """Parent class for Levels."""

    def __init__(self, lanes):
        self._n_lanes = lanes
        self._rot = 0

    def number_of_lanes(self):
        return self._n_lanes

    def get_player_speed(self, z: float):
        """Return's the player's forward speed (in units per second) at the given z coordinate."""
        return 10

    def get_cell_length(self):
        """Returns the z-length of the level's 'cells'."""
        return None

    def should_render_cells(self):
        return True

    def get_color(self, z: float) -> Color:
        """Returns the level's color at the given z coordinate."""
        return neon.BLUE

    def get_rotation(self, z: float) -> float:
        """Returns the level's rotation (along the z-axis), in degrees, when the camera is at the given z coordinate."""
        return self._rot

    def set_rotation(self, val_in_degrees: float):
        self._rot = val_in_degrees % 360

    def get_radius(self, z: float) -> float:
        """returns: radius of level at the given z coordinate."""
        return 10

    def get_all_obstacles_between(self, n, z_start, z_end) -> List[Obstacle]:
        """returns: Obstacles in lane n, between the two z coordinates."""
        return []

    def load_obstacles(self, z_start, z_end):
        """If necessary, loads (or generates) obstacles between the two z coordinates."""
        pass

    def unload_obstacles(self, z_end):
        """If necessary, unload all obstacles prior to the given z coordinate."""
        pass


class GenerationParameters:

    def __init__(self):
        self.cell_length = 20     # how far apart obstacles are
        self.speeds = [(0, 200),   # at z = [0], the speed will be [1]. In between, values are interpolated linearly.
                       (3000, 90),
                       (10000, 120),   # 120 is very fast but still playable
                       (100000, 200)]  # 200 is insane

        self.random_rate = 0.33  # how often obstacles spawn
        
    def get_player_speed(self, z):
        if z <= self.speeds[0][0]:
            return self.speeds[0][1]
        elif z >= self.speeds[-1][0]:
            return self.speeds[-1][1]
        else:
            for i in range(1, len(self.speeds)):
                z1 = self.speeds[i-1][0]
                z2 = self.speeds[i][0]
                if z1 <= z <= z2:
                    return utils.lerp((z - z1) / (z2 - z1), self.speeds[i-1][1], self.speeds[i][1])

class DesignableGenrationParameters(GenerationParameters):
    def __init__(self, cell_length=20, speed=90, random_rate=0.33):
        super().__init__()
        self.cell_length = cell_length
        self.speed = speed
        self.random_rate = random_rate
    def get_player_speed(self, z):
        return self.speed


class InfiniteGeneratingLevel(Level):

    def __init__(self, lanes, gen_params=None):
        super().__init__(lanes)
        self._obstacle_grid = {}  # (lane_n, cell_idx) -> Obstacle
        self._currently_loaded_cell_range = None  # will be [int, int] if populated
        self._gen_params = gen_params if gen_params is not None else GenerationParameters()

        self.color_dist = 1000  # color changes every X cells
        self.level_colors_to_use = [neon.BLUE, neon.CYAN, neon.WHITE, neon.YELLOW, neon.ORANGE, neon.BLACK]

    def get_random_rate(self):
        return self._gen_params.random_rate

    def get_cell_length(self):
        return self._gen_params.cell_length

    def get_color(self, z: float):
        idx1 = int(z // self.color_dist) % len(self.level_colors_to_use)
        idx2 = int((z // self.color_dist + 1) % len(self.level_colors_to_use))
        amount = (z % self.color_dist) / self.color_dist
        return self.level_colors_to_use[idx1].lerp(self.level_colors_to_use[idx2], amount)

    def get_player_speed(self, z: float):
        return self._gen_params.get_player_speed(z)

    def _generate_obstacles(self, cell_start, cell_end, ):
        for n in range(self.number_of_lanes()):
            for i in range(cell_start, cell_end):
                obs = self.generate_obstacle_at_cell(n, i)
                if obs is not None:
                    self._obstacle_grid[(n, i)] = obs

    def generate_obstacle_at_cell(self, n, i) -> Obstacle:
        """Subclasses can override this to implement custom generation logic."""
        if n == 0 and i < 5:
            # don't let obstacles spawn right in your face at the start of a run
            return None

        if random.random() < self.get_random_rate() * min(1, i / 20):
            r = random.randint(0, 3)
            cs = self.get_cell_length()
            length = 3
            if r == 0:
                return Wall(n, (i + 0.5) * cs - length / 2, length)
            elif r == 1:
                return Spikes(n, (i + 0.5) * cs - length / 2, length)
            else:
                return Enemy(n, (i + 0.5) * cs - length / 2, length)
        else:
            return None

    def get_obstacle_at_cell_if_loaded(self, n, i):
        if (n, i) in self._obstacle_grid:
            return self._obstacle_grid[(n, i)]
        else:
            return None

    def unload_obstacles(self, z_end):
        cell_end = int(z_end / self.get_cell_length())
        if self._currently_loaded_cell_range is None or self._currently_loaded_cell_range[0] >= cell_end:
            pass  # nothing to unload
        else:
            self._obstacle_grid = {p: self._obstacle_grid[p] for p in self._obstacle_grid if p[1] >= cell_end}
            if cell_end < self._currently_loaded_cell_range[1]:
                # we unloaded a portion of the loaded cells
                self._currently_loaded_cell_range[0] = cell_end
            else:
                # we unloaded everything
                self._currently_loaded_cell_range = None

    def get_all_obstacles_between(self, n, z_start, z_end) -> List[Obstacle]:
        """
        Fetches all the obstacles in the specified lane between the two z coordinates. Will generate
        that portion of the level if necessary.
        """
        n = n % self.number_of_lanes()
        cs = self.get_cell_length()
        cell_start = int(z_start / cs)
        cell_end = int(z_end / cs + 1)

        new_range = [cell_start, cell_end]
        old_range = self._currently_loaded_cell_range

        if old_range is None:
            # starting from scratch
            self._generate_obstacles(new_range[0], new_range[1])
            self._currently_loaded_cell_range = [new_range[0], new_range[1]]
            old_range = self._currently_loaded_cell_range
        elif new_range[1] <= old_range[0]:
            # new region is completely before the already-generated region
            self._generate_obstacles(cell_start, self._currently_loaded_cell_range[0])
        elif old_range[1] <= new_range[0]:
            # new region is completely after the already-generated region
            self._generate_obstacles(self._currently_loaded_cell_range[0], cell_end)
        elif old_range[0] <= new_range[0] and new_range[1] <= old_range[1]:
            pass  # we've already generated the requested region
        else:
            # new and old regions are overlapping
            if new_range[0] < old_range[0]:
                self._generate_obstacles(new_range[0], old_range[0])
            if old_range[1] < new_range[1]:
                self._generate_obstacles(old_range[1], new_range[1])

        self._currently_loaded_cell_range[0] = min(new_range[0], old_range[0])
        self._currently_loaded_cell_range[1] = max(new_range[1], old_range[1])

        return [self._obstacle_grid[(n, i)] for i in range(cell_start, cell_end) if (n, i) in self._obstacle_grid]
