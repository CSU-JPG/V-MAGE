import pygame
import keybinds
import time

import util.fonts as fonts


class Player:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.length = 1  # how long the player is (affects collisions)
        self.lane = 0
        self.speed = 0  # units per second, this is mainly controlled
        self.dy = 0
        self.modes = ['run', 'jump', 'slide', 'dead']
        self.current_mode = self.modes[0]

        self.last_z_pos = z  # used for collision detection

        self._dead_since = 0  # time of death, in seconds since epoch
        self._last_mode_before_death = None
        self._obstacle_that_killed_me = None

    def set_mode(self, mode):
        if mode in self.modes and mode != self.current_mode:
            if mode == "dead":
                self._dead_since = time.time()
                self._last_mode_before_death = self.current_mode

            self.current_mode = mode

    def is_sliding(self):
        return self.current_mode == 'slide'

    def is_jumping(self):
        return self.current_mode == 'jump'

    def is_running(self):
        return self.current_mode == 'run'

    def is_dead(self):
        return self.current_mode == 'dead'

    def get_mode(self):
        return self.current_mode

    def get_time_dead(self):
        if self.is_dead():
            return time.time() - self._dead_since
        else:
            return -1

    def get_last_mode_before_death(self):
        return self._last_mode_before_death

    def get_death_message(self):
        if self.get_score() < 1000:
            if self._obstacle_that_killed_me is not None:
                return self._obstacle_that_killed_me.get_death_message()
            else:
                # should never be seen
                return "player was killed by the guardians"
        else:
            congrat_msgs = {
                2000: "Good attempt!",
                3000: "You can do better!",
                4000: "Is that all you got?",
                5000: "You're getting the hang of it now!",
                7500: "Great run!",
                10000: "Excellent run!",
                15000: "Super run!",
                20000: "Amazing run!",
            }

            for score_thresh in congrat_msgs:
                if self.get_score() < score_thresh:
                    return congrat_msgs[score_thresh]

            return "Epic run!"

    def move_left(self):
        if not self.is_dead():
            
            self.lane -= 1

    def move_right(self):
        if not self.is_dead():
            
            self.lane += 1

    def move_forward(self, dt):
        self.last_z_pos = self.z
        self.z += self.speed * dt

    def get_lane(self, total_lanes):
        return self.lane % total_lanes

    def run(self):
        self.set_mode('run')

    def jump(self):
        if not self.is_jumping():
            
            self.set_mode('jump')
            self.dy = 5

    def max_jump_height(self):
        return 0.85  # this only matters for rendering. an approximate value is ok.

    def slide(self):
        if self.is_running():
            self.set_mode('slide')

    def set_speed(self, speed):
        self.speed = speed

    def get_score(self):
        return int(self.z / 10) * 10

    def update(self, dt, level, events):
        pressed = pygame.key.get_pressed()
        self._handle_inputs(events, pressed)
        self._handle_collisions(level)
        if not self.is_dead():
            self.set_speed(level.get_player_speed(self.z))
            self._handle_movement(dt, pressed)

    def _handle_inputs(self, events, pressed):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in keybinds.JUMP:
                    self.jump()
                if e.key in keybinds.LEFT:
                    self.move_left()
                if e.key in keybinds.RIGHT:
                    self.move_right()
                if e.key in keybinds.SLIDE:
                    self.slide()
            elif e.type == pygame.KEYUP:
                if e.key in keybinds.SLIDE and self.is_sliding():
                    self.run()

        if any(pressed[k] for k in keybinds.SLIDE):
            self.slide()

    def _handle_movement(self, dt, pressed):
        if self.y > 0 or self.dy != 0:
            fall_speed = 25
            if any(pressed[key] for key in keybinds.JUMP):
                fall_speed -= 10  # slight jump boost if you hold the jump key down
            if any(pressed[key] for key in keybinds.SLIDE):
                fall_speed += 30
            self.dy -= fall_speed * dt

        self.y += self.dy * dt

        if self.y < 0:
            self.y = 0
            self.dy = 0
            if not self.is_sliding():
                self.set_mode('run')

        self.move_forward(dt)

    def _handle_collisions(self, level):
        if self.is_dead():
            return
        else:
            lane_n = self.get_lane(level.number_of_lanes())
            obstacles = level.get_all_obstacles_between(lane_n, self.last_z_pos, self.z + self.length)
            for obs in obstacles:
                if obs.handle_potential_collision(self):
                    self.set_mode('dead')
                    
                    self._obstacle_that_killed_me = obs
                    return

    def draw(self, display):
        # draw info to display
        fonts.Text(display, 'X : ' + str(self.x) + ' | OPTIONAL', 50, 150, 25).draw()
        fonts.Text(display, 'Y : {:.2f}'.format(self.y), 50, 200, 25).draw()
        fonts.Text(display, 'Z : ' + str(int(self.z)), 50, 250, 25).draw()
        fonts.Text(display, 'LANE : ' + str(self.lane), 50, 300, 25).draw()
        fonts.Text(display, 'MODE : ' + self.current_mode, 550, 50, 25).draw()
