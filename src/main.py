import pygame
import json
from cube_parallelogram_draw import * 
from enum import IntEnum
from pygame.math import Vector2
from typing import Any

SIZE = 880
CUBE_SIZE = SIZE / 10
DOT_SIZE = CUBE_SIZE / 11
_BACKGROUND_COLOR = pygame.Color("#DDDDDD")
CUBE_TOP_COLOR = pygame.Color("#AAAAAA")
BPM = 112
BEAT_PER_SEC = BPM / 60
BEAT_PER_MS = BEAT_PER_SEC / 1000
BEAT16_PER_MS = BEAT_PER_MS * 4
FACE_RESOLUTION = 10

with open('./data/cube_info.json', 'r') as cube_info_file:
    CUBE_INFO = json.load(cube_info_file)

for i, x in enumerate(CUBE_INFO):
    try:
        with open(f"./data/Timing/{x["tone"]}.json", 'r') as timing_file:
            CUBE_INFO[i]["timing"] = json.load(timing_file)
    except FileNotFoundError:
        CUBE_INFO[i]["timing"] = [
            {
            "id": 0,
            "beats": 256,
            "duration": 0,
            "type": 0,
            "total": 0
            }
        ]

class Tone(IntEnum):
    Drums = 0
    Chord = 1
    FA_Front = 2
    FA_Back = 3
    WWDTM_High = 4
    WWDTM_Low = 5
    SF_Roll = 6
    SF_Tap = 7
    PM = 8
    Arp = 9

class Pattern:
    def __init__(self, face: str, dots: list[str]):
        self.face = face
        self.matrix: list[int] = [int(x, 2) for x in dots]
    def draw_self(self, screen: pygame.Surface, position: Vector2, color: pygame.Color = pygame.Color("#C004E6")):
        for i, line in enumerate(self.matrix):
            for j in range(FACE_RESOLUTION):
                if line & (1 << j):
                    ori_point = position + (PARALLELOGRAM_OFFSET[self.face][1] * j + PARALLELOGRAM_OFFSET[self.face][3] * i) * DOT_SIZE
                    points = cal_parallelogram(ori_point, self.face, DOT_SIZE)
                    pygame.draw.polygon(screen, color, points)

DEF_PATTERN = Pattern(
                face = "left",
                dots = [
                    "0b00000000000",
                    "0b00000100000",
                    "0b00000000000",
                    "0b00001110000",
                    "0b00000000000",
                    "0b00011111000",
                    "0b00000000000",
                    "0b00111111100",
                    "0b00000000000",
                    "0b01111111110",
                    "0b00000000000"
                ]
            )

class Animation():
    def __init__(self, Ainfo: dict[str, Any], cube: Tone, id: int):
        #self.pattern = CUBE_INFO[cube]["patterns"][Ainfo["type"]]
        if len(CUBE_INFO[cube]["patterns"]) == 0:
            self.pattern = DEF_PATTERN
        else:
            self.pattern = Pattern(CUBE_INFO[cube]["patterns"][Ainfo["type"]]["face"], CUBE_INFO[cube]["patterns"][Ainfo["type"]]["dots"])
            #self.pattern = CUBE_INFO[cube]["patterns"][Ainfo["type"]]
        self.duration = Ainfo["duration"]
        self.beats = Ainfo["beats"]
        self.id = id

    def update(self, step_ms: float):
        step_beat = step_ms * BEAT16_PER_MS
        self.duration -= step_beat
        self.beats -= step_beat

    def isTriggered(self) -> bool:
        return self.duration > 0

    def reachEnd(self) -> bool:
        return self.beats <= 0

class Face:
    def __init__(self, aspect : str, color : pygame.Color):
        self.aspect = aspect
        self.color = color
    def draw_self(self, screen : pygame.Surface, position : Vector2) -> None:
        points = cal_parallelogram(position, self.aspect, CUBE_SIZE)
        pygame.draw.polygon(screen, self.color, points)

class Cube:
    def __init__(self, position : Vector2, tone: str, color : dict[str, str], patterns : list[Pattern], timing : list[dict[str, Any]]):
        self.tone = Tone[tone]
        self.color = color
        self.position = position
        self.faces = {"left": Face("left", pygame.Color(color["main"])),
                    "right": Face("right", pygame.Color(color["shadow"])),
                    "top": Face("top", CUBE_TOP_COLOR),
                    "top_light": Face("top", pygame.Color(color["top_light"]))
                    }

        self.timing = timing
        self.animation = Animation(timing[0], self.tone, 0)
        self.anima_id = 0
        self.patterns = patterns
        
    def draw(self, screen : pygame.Surface) -> None:
        self.faces["top"].draw_self(screen, self.position)
        self.faces["right"].draw_self(screen, self.position)
        self.faces["left"].draw_self(screen, self.position)
        if self.animation.isTriggered():
            self.animation.pattern.draw_self(screen, self.position, pygame.Color(self.color["light"]))
            self.faces["top_light"].draw_self(screen, self.position, )

    def update(self, screen: pygame.Surface, step: float):
        self.animation.update(step)
        if self.animation.reachEnd():
            self.anima_id = (self.anima_id + 1) % len(self.timing)
            self.animation = Animation(self.timing[self.anima_id], self.tone, self.anima_id)

pygame.mixer.init()
pygame.mixer.music.load("./data/song.wav")
pygame.init()
pygame.mixer.music.play()
screen = pygame.display.set_mode((SIZE, SIZE))
screen.fill(_BACKGROUND_COLOR)
Running = 1

cubes: list[Cube] = []

for i in range(len(CUBE_INFO)):
    x = i % 4
    y = i // 4
    x = x * 2 + 1
    y = y * 2 + 1
    x *= SIZE // 8
    y *= SIZE // 8
    cubes.append(Cube(Vector2(x, y), **CUBE_INFO[i], ))
    cubes[i].draw(screen)

clock = pygame.time.Clock()
while Running:
    times = clock.tick()
    for cube in cubes:
        cube.update(screen, times)
        cube.draw(screen)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = 0

pygame.quit()