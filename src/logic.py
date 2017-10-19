#! python2
import random
import os
import sys

from constants import ColourScheme

# These are the settings for pyinstaller
if getattr(sys, 'frozen', False):
    # we are running in a bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = '.'


class Ball:
    def __init__(self, colour=None):
        self.colour = colour


class Square:
    def __init__(self, colour, position):
        self.colour = colour
        self.position = position


class Board:
    def __init__(self, width=20, height=16, BallColours=ColourScheme.MONFAVORITE):
        self.width = width
        self.height = height
        self.balls = [[Ball() for i in range(self.height)]
                      for j in range(self.width)]
        self.nballsleft = width * height
        self.nmoves = 0
        self.score = 0
        self.currentScore = 0
        self.highScore = self.getHighScore()
        self.BallColours = BallColours
        self._initBoard()

    # helper Functions. private, prefixed by _underscore
    def _initBoard(self):
        "Randomly give each ball a colour"
        for i in range(self.width):
            for j in range(self.height):
                self.balls[i][j].colour = self.BallColours[random.choice([0, 1, 2, 3, 4])]

    def _adjacent(self, position):
        "returns the list of balls of the same colour adjacent to the ball at position"
        x, y = position
        AdjacentSameBalls = []
        for m, n in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if 0 <= x + m < self.width and 0 <= y + n < self.height:
                if self.balls[x][y] and self.balls[x + m][y + n]:
                    if self.balls[x][y].colour == self.balls[x + m][y + n].colour:
                        AdjacentSameBalls.append((x + m, y + n))
        return AdjacentSameBalls

    def _markBalls(self, position):
        "Mark the balls that need to be deleted"
        connectedballs = self._findAdjacentBalls(position)
        if len(connectedballs) == 1:  # means that it has no similarly coloured balls as neighbors
            return
        self.score += self.get_score(position)
        self.nmoves += 1
        for ballposition in connectedballs:
            x, y = ballposition
            self.balls[x][y] = None
            self.nballsleft -= 1

    def _clearBalls(self):
        "delete the balls and let them fall into space vacated by removed balls"
        for i in range(self.width):
            for j in range(self.height):
                if self.balls[i][j] is None:
                    for k in reversed(range(j)):
                        self.balls[i][k + 1] = self.balls[i][k]
                    self.balls[i][0] = None
        # shift to the left when the last row has an empty column
        for i in reversed(range(self.width)):  # through columns
            if self.balls[i][-1] is None:
                for j in range(self.height):
                    for k in (range(i, self.width - 1)):
                        self.balls[k][j] = self.balls[k + 1][j]
                    self.balls[-1][j] = None
        if self.score > self.highScore:
            self.highScore = self.score

    def _findAdjacentBalls(self, ballposition):
        """returns a list of all the balls in the same group as the ball in position"""
        x, y = ballposition
        stack = [ballposition]
        visited = [[False for i in range(self.height)]
                   for j in range(self.width)]
        # basically a breadth first search.
        visited[x][y] = True
        connectedballs = [ballposition]
        while stack:
            ballposition = stack.pop()
            for position in self._adjacent(ballposition):
                x1, y1 = position
                if not visited[x1][y1]:
                    stack.append(position)
                    connectedballs.append(position)
                    visited[x1][y1] = True

        return connectedballs

    # Public Interface

    def joiningSquares(self):
        "Squares between each ball that's adjacent and of the same colour "
        squareballs = set()
        for x in range(self.width):
            for y in range(self.height):
                for m, n in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if 0 <= x + m < self.width and 0 <= y + n < self.height:
                        # if there is a ball in both positions
                        if self.balls[x][y] and self.balls[x + m][y + n]:
                            if self.balls[x][y].colour == self.balls[x + m][y + n].colour:
                                square = Square(
                                    self.balls[x][y].colour, (x + m / 2.0, y + n / 2.0))
                                squareballs.add(square)

        return squareballs

    def remove_balls(self, position):
        "Mark the balls and remove the marked balls"
        self._markBalls(position)
        self._clearBalls()

    def get_score(self, position):
        "get the score if you remove all the balls connected to the ball at position"
        return len(self._findAdjacentBalls(position))**2

    def getHighScore(self):
        with open(basedir + os.sep + 'TopScores.txt', 'r') as f:
            score = f.readline()
            if len(score) > 0:
                return int(score)
            else:
                return 0

    def updateHighScore(self):
        if self.score >= self.highScore:
            self.highScore = self.score
            with open('TopScores.txt', 'w') as f:
                score = f.write(str(self.score))

    def isGameOver(self):
        "Returns True if the Game is over and False otherwise"
        for x in range(self.width):
            for y in range(self.height):
                if len(self._adjacent((x, y))) > 0:
                    return False
        self.updateHighScore()
        return True