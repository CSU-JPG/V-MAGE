from classes.Maths import Vec2D


class Camera:
    def __init__(self, pos, entity, mapLength=60):
        # self.pos = Vec2D(pos.x, pos.y)
        self.pos = Vec2D(0, 0)
        self.entity = entity
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32
        self.mapLength = mapLength

    def move(self):
        xPosFloat = self.entity.getPosIndexAsFloat().x
        if 10 < xPosFloat < self.mapLength - 10:
            self.pos.x = -xPosFloat + 10
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32
