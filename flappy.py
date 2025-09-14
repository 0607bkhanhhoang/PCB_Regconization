"""
Flappy Bird - single-file PyQt5 implementation (fixed for fillRect int requirement)
Save as: flappy_qt.py
Run: python flappy_qt.py
Requires: PyQt5

Controls:
 - Space or Mouse Click: flap (jump)
 - R: restart after game over

"""

import sys
import random
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QApplication, QWidget

# Game constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60
PIPE_WIDTH = 60
GAP_HEIGHT = 160
PIPE_SPACING = 220
BIRD_SIZE = 28
GRAVITY = 900.0
FLAP_VELOCITY = -320.0
PIPE_SPEED = 140.0

class Bird:
    def __init__(self, x, y):
        self.pos = QPointF(x, y)
        self.vel = 0.0
        self.size = BIRD_SIZE
        self.alive = True

    def rect(self):
        s = self.size
        return QRectF(self.pos.x() - s/2, self.pos.y() - s/2, s, s)

    def update(self, dt):
        if not self.alive:
            return
        self.vel += GRAVITY * dt
        self.pos.setY(self.pos.y() + self.vel * dt)

    def flap(self):
        self.vel = FLAP_VELOCITY

class PipePair:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.passed = False

    def top_rect(self):
        return QRectF(self.x, 0, PIPE_WIDTH, self.gap_y - GAP_HEIGHT/2)

    def bottom_rect(self):
        return QRectF(self.x, self.gap_y + GAP_HEIGHT/2, PIPE_WIDTH, WINDOW_HEIGHT - (self.gap_y + GAP_HEIGHT/2))

    def update(self, dt):
        self.x -= PIPE_SPEED * dt

class FlappyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Flappy Bird - PyQt5')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000 // FPS)

        self.reset_game()

    def reset_game(self):
        self.bird = Bird(WINDOW_WIDTH*0.25, WINDOW_HEIGHT/2)
        self.pipes = []
        self.spawn_x = WINDOW_WIDTH + 40
        self.score = 0
        self.game_over = False
        self.started = False

        for i in range(3):
            x = self.spawn_x + i * PIPE_SPACING
            gap_y = random.randint(120, WINDOW_HEIGHT - 120)
            self.pipes.append(PipePair(x, gap_y))

    def start_game(self):
        self.started = True
        self.bird.alive = True
        self.bird.pos = QPointF(WINDOW_WIDTH*0.25, WINDOW_HEIGHT/2)
        self.bird.vel = 0.0
        self.score = 0
        for p in self.pipes:
            p.passed = False

    def tick(self):
        dt = 1.0 / FPS

        if self.started and not self.game_over:
            self.bird.update(dt)
            for pipe in self.pipes:
                pipe.update(dt)

            if len(self.pipes) == 0 or (self.pipes[-1].x < WINDOW_WIDTH - PIPE_SPACING):
                x = (self.pipes[-1].x + PIPE_SPACING) if self.pipes else self.spawn_x
                gap_y = random.randint(120, WINDOW_HEIGHT - 120)
                self.pipes.append(PipePair(x + PIPE_SPACING, gap_y))

            if self.pipes and self.pipes[0].x + PIPE_WIDTH < -50:
                self.pipes.pop(0)

            bird_rect = self.bird.rect()
            for pipe in self.pipes:
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.pos.x():
                    pipe.passed = True
                    self.score += 1
                if bird_rect.intersects(pipe.top_rect()) or bird_rect.intersects(pipe.bottom_rect()):
                    self.end_game()

            if self.bird.pos.y() - self.bird.size/2 < 0 or self.bird.pos.y() + self.bird.size/2 > WINDOW_HEIGHT:
                self.end_game()

        self.update()

    def end_game(self):
        self.game_over = True
        self.bird.alive = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(int(0), int(0), int(WINDOW_WIDTH), int(WINDOW_HEIGHT), QColor(135, 206, 235))

        ground_h = 90
        painter.fillRect(int(0), int(WINDOW_HEIGHT - ground_h), int(WINDOW_WIDTH), int(ground_h), QColor(222, 184, 135))

        for pipe in self.pipes:
            painter.fillRect(pipe.top_rect().toRect(), QColor(34, 139, 34))
            painter.fillRect(pipe.bottom_rect().toRect(), QColor(34, 139, 34))
            rim_w = 6
            tr = pipe.top_rect().toRect()
            br = pipe.bottom_rect().toRect()
            painter.fillRect(tr.x(), tr.height() - rim_w, tr.width(), rim_w, QColor(0, 100, 0))
            painter.fillRect(br.x(), br.y(), br.width(), rim_w, QColor(0, 100, 0))

        br = self.bird.rect().toRect()
        painter.save()
        angle = max(-45, min(45, int(self.bird.vel / 8)))
        painter.translate(br.center())
        painter.rotate(angle)
        painter.translate(-br.center())
        painter.setBrush(QColor(255, 215, 0))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(br)
        painter.restore()

        painter.setPen(QColor(255, 255, 255))
        font = QFont('Arial', 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 40, f"Score: {self.score}")

        if not self.started:
            painter.setPen(QColor(0, 0, 0))
            font2 = QFont('Arial', 20)
            painter.setFont(font2)
            painter.drawText(self.rect(), Qt.AlignCenter, "Press Space or Click to Start")
        elif self.game_over:
            painter.setPen(QColor(200, 30, 30))
            font3 = QFont('Arial', 32, QFont.Bold)
            painter.setFont(font3)
            painter.drawText(self.rect(), Qt.AlignCenter, f"Game Over\nScore: {self.score}\nPress R to Restart")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.on_flap()
        elif event.key() == Qt.Key_R:
            if self.game_over:
                self.reset_game()
                self.started = False
                self.game_over = False
        event.accept()

    def mousePressEvent(self, event):
        self.on_flap()

    def on_flap(self):
        if not self.started:
            self.start_game()
        if not self.game_over:
            self.bird.flap()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = FlappyWidget()
    w.show()
    sys.exit(app.exec_())