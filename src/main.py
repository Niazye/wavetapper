import pygame
import json
import math

SIZE = 880
CUBE_SIZE = SIZE / 10
DOT_SIZE = CUBE_SIZE / 11
_BACKGROUND_COLOR = pygame.Color("#DDDDDD")
_TOP_COLOR = pygame.Color("#AAAAAA")
BPM = 112
BEAT_PER_SEC = BPM / 60
BEAT_PER_MS = BEAT_PER_SEC / 1000
BEAT16_PER_MS = BEAT_PER_MS * 4

OFFSET = {
    "top" : [(0, 0), (-math.sqrt(3) / 2, -0.5), (0, -1), (math.sqrt(3) / 2, -0.5)],
    "left" : [(0, 0), (-math.sqrt(3) / 2, -0.5), (-math.sqrt(3) / 2, 0.5), (0, 1)], #AC
    "right" : [(0, 0), (math.sqrt(3) / 2, -0.5), (math.sqrt(3) / 2, 0.5), (0, 1)]   #CW
}


class Cube:
    def __init__(self, _x, _y, _color, _trigger):
        self.x = _x
        self.y = _y
        self.color = _color
        self.animation = _trigger
    def draw(self, screen):
        points = [[self.x,self.y]] * 4
        for i in range(4):
            points[i] = (self.x + CUBE_SIZE * OFFSET["left"][i][0], self.y + CUBE_SIZE * OFFSET["left"][i][1]);
        pygame.draw.polygon(screen, self.color["main"], points)
        for i in range(4):
            points[i] = (self.x + CUBE_SIZE * OFFSET["right"][i][0], self.y + CUBE_SIZE * OFFSET["right"][i][1]);
        pygame.draw.polygon(screen, self.color["shadow"], points)
        for i in range(4):
            points[i] = (self.x + CUBE_SIZE * OFFSET["top"][i][0], self.y + CUBE_SIZE * OFFSET["top"][i][1]);
        pygame.draw.polygon(screen, _TOP_COLOR, points)
    def trigger(self, screen, _type):
        _dots = self.animation[_type]["dots"]
        _face = self.animation[_type]["face"]
        dots = list(map(lambda x : int(x, 2), _dots));
        points = [1] * 4
        if _face == "left":
            for i in range(11):
                for j in range(11):
                    if dots[i] & (1 << j):
                        xx = self.x - j * DOT_SIZE / 2 * math.sqrt(3)
                        yy = self.y + DOT_SIZE * i - DOT_SIZE * j / 2; 
                        for k in range(4):
                            points[k] = (xx + DOT_SIZE * OFFSET["left"][k][0], yy + DOT_SIZE * OFFSET["left"][k][1]);
                        pygame.draw.polygon(screen, pygame.Color(self.color["light"]), points)
        if _face == "right":
            for i in range(11):
                for j in range(11):
                    if dots[i] & ((1 << 10) >> j):
                        xx = self.x + j * DOT_SIZE / 2 * math.sqrt(3)
                        yy = self.y + DOT_SIZE * i - DOT_SIZE * j / 2; 
                        for k in range(4):
                            points[k] = (xx + DOT_SIZE * OFFSET["right"][k][0], yy + DOT_SIZE * OFFSET["right"][k][1]);
                        pygame.draw.polygon(screen, pygame.Color(self.color["light"]), points)
        for i in range(4):
            points[i] = (self.x + CUBE_SIZE * OFFSET["top"][i][0], self.y + CUBE_SIZE * OFFSET["top"][i][1]);
        pygame.draw.polygon(screen, pygame.Color(self.color["top_light"]), points)


pygame.mixer.init()
pygame.mixer.music.load("song.wav")
pygame.init()
pygame.mixer.music.play()
screen = pygame.display.set_mode((SIZE, SIZE))
screen.fill(_BACKGROUND_COLOR)
Running = 1

cubes = []
timings = []
f = open("cube_info.json", "r")
cubes = json.load(f)
f.close()

for x in cubes:
    f = open(f"Timing/{x["tone"]}.json")
    timings.append(json.load(f))
    f.close()
for i, xx in enumerate(cubes):
    x = i % 4
    y = i // 4
    x = x * 2 + 1
    y = y * 2 + 1
    x *= SIZE // 8
    y *= SIZE // 8
    tmp = Cube(x, y, xx["color"], xx["trigger"])
    cubes[i]= tmp

currents = [0] * 16
trigger_remain_beats = [0] * 16
beat_waiting_beats = [0] * 16
clock = pygame.time.Clock()
for i, x in enumerate(cubes):
    trigger_remain_beats[i] = timings[i][0]["duration"]
    beat_waiting_beats[i] = timings[i][0]["beats"]
while Running:
    times = clock.tick()
    for cube in cubes:
        cube.draw(screen)
    trigger_remain_beats = [max(0, x - times * BEAT16_PER_MS) for x in trigger_remain_beats]
    beat_waiting_beats = [max(0, x - times * BEAT16_PER_MS) for x in beat_waiting_beats]
    for i in range(1):
        if trigger_remain_beats[i] > 0:
            cubes[i].trigger(screen, timings[i][currents[i]]["type"])
        if beat_waiting_beats[i] <= 0:
            currents[i] = (currents[i] + 1)
            trigger_remain_beats[i] = timings[i][currents[i]]["duration"]
            beat_waiting_beats[i] = timings[i][currents[i]]["beats"]
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = 0