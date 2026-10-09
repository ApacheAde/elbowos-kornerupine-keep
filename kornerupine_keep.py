#!/usr/bin/env python3
"""Kornerupine Keep — neon tower-lite arcade for ElbowOS. Python 3 + pygame.

Plant crystal pylons on the keep pads. They lance descending prism moths.
A / D or arrows pick a column, W / S pick a row, Space plants. R restarts.
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--play" not in sys.argv
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if RECORD:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/KORNERUPINE_KEEP_ElbowOS.mp4")
TITLE, HANDLE = "KORNERUPINE KEEP", "x.com/ElbowOS"
INK = (7, 12, 32)
LANE = (16, 28, 62)
TEAL = (46, 220, 198)
LIME = (190, 255, 74)
CORAL = (255, 96, 82)
GOLD = (255, 198, 78)
VIOLET = (176, 104, 255)
WHITE = (240, 246, 255)
COLS, ROWS = 4, 3


def clamp(v, a, b):
    return a if v < a else b if v > b else v


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if not RECORD else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("DejaVu Sans", 64, bold=True)
        self.mid = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
        self.small = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        self.reset()

    def reset(self):
        random.seed(11)
        self.t = 0
        self.score = 0
        self.shield = 8
        self.cd = 6
        self.col = 0
        self.row = 1
        self.spawn = 10
        self.moths = []
        self.pylons = []
        self.bolts = []
        self.bits = []
        self.flash = 0
        self.stars = [(random.randrange(W), random.randrange(H), random.choice((2, 2, 3))) for _ in range(70)]

    def pad_xy(self, c, r):
        return 180 + c * 240, 1180 + r * 170

    def taken(self, c, r):
        return any(p[0] == c and p[1] == r for p in self.pylons)

    def place(self, c, r):
        if self.taken(c, r) or len(self.pylons) >= 8:
            return False
        self.pylons.append([c, r, 0])
        x, y = self.pad_xy(c, r)
        self.burst(x, y, LIME, 14)
        return True

    def burst(self, x, y, col, n):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(2, 9)
            self.bits.append([x, y, math.cos(a) * s, math.sin(a) * s, col, random.randint(10, 22)])

    def hottest(self):
        best, bc, by = 0, 9e9, 0
        for m in self.moths:
            if m[1] > by:
                by, bc = m[1], m[0]
        return bc

    def auto(self):
        self.cd -= 1
        self.col = self.hottest() % COLS
        open_rows = [r for r in range(ROWS) if not self.taken(self.col, r)]
        self.row = open_rows[0] if open_rows else 1
        if self.cd <= 0 and open_rows and len(self.pylons) < 8:
            self.place(self.col, open_rows[0])
            self.cd = 16

    def step(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        self.spawn -= 1
        if self.spawn <= 0:
            c = random.randrange(COLS)
            kind = 1 if random.random() < 0.22 else 0
            self.moths.append([c, -40, 3.2 + self.t / 280 + kind * 1.4, 2 + kind, kind])
            self.spawn = max(8, 22 - self.t // 40)
        if RECORD:
            self.auto()
        for p in self.pylons:
            p[2] -= 1
            if p[2] <= 0:
                x, y = self.pad_xy(p[0], p[1])
                tgt = None
                for m in self.moths:
                    if m[0] == p[0] and m[1] < y:
                        if tgt is None or m[1] > tgt[1]:
                            tgt = m
                if tgt:
                    p[2] = 9
                    self.bolts.append([x, y - 70, tgt, 18])
        for b in self.bolts:
            b[3] -= 1
            m = b[2]
            if m in self.moths:
                b[0] += (self.pad_xy(m[0], 0)[0] - b[0]) * 0.45
                b[1] += (m[1] - b[1]) * 0.45
                if abs(b[1] - m[1]) < 36:
                    m[3] -= 1
                    self.burst(self.pad_xy(m[0], 0)[0], m[1], GOLD if m[4] else CORAL, 10)
                    if m[3] <= 0:
                        self.score += 25 if m[4] else 10
                        self.moths.remove(m)
                        self.burst(self.pad_xy(m[0], 0)[0], m[1], LIME, 18)
                    b[3] = 0
        self.bolts = [b for b in self.bolts if b[3] > 0]
        kept = []
        for m in self.moths:
            m[1] += m[2]
            if m[1] > 1680:
                self.shield -= 1
                self.flash = 8
                self.burst(self.pad_xy(m[0], 0)[0], 1660, VIOLET, 16)
                if self.shield <= 0:
                    self.shield = 8
                    self.score = max(0, self.score - 20)
            else:
                kept.append(m)
        self.moths = kept
        for bit in self.bits:
            bit[0] += bit[2]
            bit[1] += bit[3]
            bit[5] -= 1
        self.bits = [b for b in self.bits if b[5] > 0]

    def draw(self, surf):
        surf.fill(INK)
        for i in range(8):
            pygame.draw.rect(surf, (12 + i * 3, 20 + i, 48 + i * 4), (0, i * 240, W, 240))
        for x, y, r in self.stars:
            yy = (y + self.t * (r + 1)) % H
            pygame.draw.circle(surf, (80, 110, 170), (x, int(yy)), r)
        for c in range(COLS):
            x = 180 + c * 240
            pygame.draw.rect(surf, LANE, (x - 78, 220, 156, 1460), border_radius=28)
            pygame.draw.rect(surf, (40, 70, 130), (x - 78, 220, 156, 1460), 3, border_radius=28)
        pygame.draw.rect(surf, (40, 18, 48) if self.flash else (18, 36, 70), (70, 1668, 940, 36), border_radius=12)
        pygame.draw.rect(surf, TEAL, (74, 1672, int(932 * clamp(self.shield, 0, 8) / 8), 28), border_radius=10)
        for c in range(COLS):
            for r in range(ROWS):
                x, y = self.pad_xy(c, r)
                hot = c == self.col and r == self.row
                pygame.draw.circle(surf, GOLD if hot else (30, 54, 96), (x, y), 46, 4)
                pygame.draw.circle(surf, (255, 220, 120) if hot else (50, 80, 120), (x, y), 18)
        for c, r, cd in self.pylons:
            x, y = self.pad_xy(c, r)
            pulse = 6 + int(4 * math.sin(self.t / 5 + c))
            pygame.draw.polygon(surf, TEAL, [(x, y - 92), (x + 28, y - 20), (x - 28, y - 20)])
            pygame.draw.polygon(surf, LIME, [(x, y - 78), (x + 14, y - 30), (x - 14, y - 30)])
            pygame.draw.circle(surf, WHITE, (x, y - 70), pulse)
        for m in self.moths:
            x = self.pad_xy(m[0], 0)[0]
            y = int(m[1])
            col = GOLD if m[4] else CORAL
            wing = 28 + int(8 * math.sin(self.t / 3 + y))
            pygame.draw.polygon(surf, VIOLET, [(x - wing, y), (x, y - 16), (x, y + 16)])
            pygame.draw.polygon(surf, VIOLET, [(x + wing, y), (x, y - 16), (x, y + 16)])
            pygame.draw.polygon(surf, col, [(x, y - 26), (x + 16, y), (x, y + 26), (x - 16, y)])
            pygame.draw.circle(surf, WHITE, (x, y), 5)
        for b in self.bolts:
            pygame.draw.line(surf, LIME, (b[0], b[1]), (b[0], b[1] + 50), 8)
            pygame.draw.circle(surf, WHITE, (int(b[0]), int(b[1])), 10)
        for bit in self.bits:
            pygame.draw.circle(surf, bit[4], (int(bit[0]), int(bit[1])), max(2, bit[5] // 5))
        banner = self.font.render(TITLE, True, WHITE)
        surf.blit(banner, banner.get_rect(center=(W // 2, 90)))
        sc = self.mid.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 168)))
        tag = self.small.render(HANDLE, True, TEAL)
        surf.blit(tag, tag.get_rect(center=(W // 2, 1840)))
        hint = self.small.render("plant pylons  ·  lance the moths", True, (170, 200, 230))
        surf.blit(hint, hint.get_rect(center=(W // 2, 1888)))

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_a, pygame.K_LEFT):
                        self.col = (self.col - 1) % COLS
                    elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                        self.col = (self.col + 1) % COLS
                    elif ev.key in (pygame.K_w, pygame.K_UP):
                        self.row = (self.row - 1) % ROWS
                    elif ev.key in (pygame.K_s, pygame.K_DOWN):
                        self.row = (self.row + 1) % ROWS
                    elif ev.key == pygame.K_SPACE:
                        self.place(self.col, self.row)
                    elif ev.key == pygame.K_r:
                        self.reset()
            self.step()
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frame = pygame.Surface((W, H))
        try:
            for _ in range(FPS * SECS):
                self.step()
                self.draw(frame)
                proc.stdin.write(pygame.image.tobytes(frame, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        pygame.quit()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)


def main():
    g = Game()
    if RECORD:
        g.record()
    else:
        g.play()


if __name__ == "__main__":
    main()
