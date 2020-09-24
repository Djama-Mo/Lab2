import random


def main():
    r = Robot(0, 0, [])
    r.surroundings('WALL')


cells = {
    ' ': 'EMPTY',
    'F': 'EXIT',
    '#': 'WALL'
}


class Cell(object):
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'


# noinspection DuplicatedCode
class Robot(object):
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self.angle = 0
        self.map = map

    def __repr__(self):
        return f'\n x = {self.x}\n y = {self.y}\n angle: {str(self.angle)}'

    def show(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if i == self.y and j == self.x:
                    print("\033[31m {}\033[0m" .format('ROBOT'), end=' ')
                else:
                    print(self.map[i][j].type, end='  ')
            print()

    def rotate(self, angle):
        if angle % 60 == 0:
            self.angle = angle
        else:
            print('choose da correct angle')

    def wall(self):
        count = 1
        if self.angle % 360 == 0:
            while self.map[self.y - count][self.x].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 60 and self.x % 2 == 1:
            while self.map[self.y - count][self.x + count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 60 and self.x % 2 == 0:
            while self.map[self.y][self.x + count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 120 and self.x % 2 == 1:
            while self.map[self.y][self.x + count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 120 and self.x % 2 == 0:
            while self.map[self.y + count][self.x + count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 180:
            while self.map[self.y + count][self.x].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 240 and self.x % 2 == 1:
            while self.map[self.y][self.x - count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 240 and self.x % 2 == 0:
            while self.map[self.y + count][self.x - count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 300 and self.x % 2 == 1:
            while self.map[self.y - count][self.x - count].type == 'EMPTY':
                count += 1
        elif self.angle % 360 == 300 and self.x % 2 == 1:
            while self.map[self.y][self.x - count].type == 'EMPTY':
                count += 1
        return count - 1

    def move(self, _dist):
        distance = self.wall()
        if _dist > distance:
            return False
        dist = 0
        while dist != _dist:
            dist += 1
            if self.angle % 360 == 0:
                self.y += dist
            elif self.angle % 360 == 60 and self.x % 2 == 1:
                self.x -= dist
            elif self.angle % 360 == 60 and self.x % 2 == 0:
                self.x -= dist
                self.y += dist
            elif self.angle % 360 == 120 and self.x % 2 == 1:
                self.x -= dist
                self.y -= dist
            elif self.angle % 360 == 120 and self.x % 2 == 0:
                self.x -= dist
            elif self.angle % 360 == 180:
                self.y -= dist
            elif self.angle % 360 == 240 and self.x % 2 == 1:
                self.x += dist
                self.y -= dist
            elif self.angle % 360 == 240 and self.x % 2 == 0:
                self.x += dist
            elif self.angle % 360 == 300 and self.x % 2 == 1:
                self.x += dist
            elif self.angle % 360 == 300 and self.x % 2 == 0:
                self.x += dist
                self.y += dist
            else:
                print('Enter da correct angle!')
        return True

    def surroundings(self, type):
        x = self.x
        y = self.y
        wall = []
        exit = []
        # dest = self.wall()
        count = 0
        end = random.randint(1, 2)

        if self.angle % 360 == 0:
            while count != end:
                count += 1
                if self.map[y + count][x].type == 'WALL':
                    wall.append(x)
                    wall.append(y + count)
                    break
                elif self.map[y + count][x].type == 'EXIT':
                    exit.append(x)
                    exit.append(y + count)
                    break

        elif self.angle % 360 == 60 and self.x % 2 == 1:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if count == 1:
                    if self.map[y][x - count].type == 'WALL':
                        wall.append(x - count)
                        wall.append(y)
                        break
                    elif self.map[y][x - count].type == 'EXIT':
                        exit.append(x - count)
                        exit.append(y)
                        break
                elif count == 2:
                        if self.map[y + 1][x - count].type == 'WALL':
                            wall.append(x - count)
                            wall.append(y + 1)
                            break
                        elif self.map[y + 1][x - count].type == 'EXIT':
                            exit.append(x - count)
                            exit.append(y + 1)
                            break

        elif self.angle % 360 == 60 and self.x % 2 == 0:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if self.map[y + 1][x - count].type == 'WALL':
                    wall.append(x - count)
                    wall.append(y + 1)
                    break
                elif self.map[y + 1][x - count].type == 'EXIT':
                    exit.append(x - count)
                    exit.append(y + 1)
                    break

        elif self.angle % 360 == 120 and self.x % 2 == 1:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if self.map[y - 1][x - count].type == 'WALL':
                    wall.append(x - count)
                    wall.append(y - 1)
                    break
                elif self.map[y - 1][x - count].type == 'EXIT':
                    exit.append(x - count)
                    exit.append(y - 1)
                    break

        elif self.angle % 360 == 120 and self.x % 2 == 0:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if count == 1:
                    if self.map[y][x - count].type == 'WALL':
                        wall.append(x - count)
                        wall.append(y)
                        break
                    elif self.map[y][x - count].type == 'EXIT':
                        exit.append(x - count)
                        exit.append(y)
                        break
                elif count == 2:
                    if self.map[y - 1][x - count].type == 'WALL':
                        wall.append(x - count)
                        wall.append(y - 1)
                        break
                    elif self.map[y - 1][x - count].type == 'EXIT':
                        exit.append(x - count)
                        exit.append(y - 1)
                        break

        elif self.angle % 360 == 180:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if self.map[y - count][x].type == 'WALL':
                    wall.append(x)
                    wall.append(y - count)
                    break
                elif self.map[y - count][x].type == 'EXIT':
                    exit.append(x)
                    exit.append(y - count)
                    break

        elif self.angle % 360 == 240 and self.x % 2 == 1:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if self.map[y - 1][x + count].type == 'WALL':
                    wall.append(x + count)
                    wall.append(y - 1)
                    break
                elif self.map[y - 1][x + count].type == 'EXIT':
                    exit.append(x + count)
                    exit.append(y - 1)
                    break

        elif self.angle % 360 == 240 and self.x % 2 == 0:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if count == 1:
                    if self.map[y][x + count].type == 'WALL':
                        wall.append(x + count)
                        wall.append(y)
                        break
                    elif self.map[y][x + count].type == 'EXIT':
                        exit.append(x + count)
                        exit.append(y)
                        break
                elif count == 2:
                    if self.map[y - 1][x + count].type == 'WALL':
                        wall.append(x + count)
                        wall.append(y - 1)
                        break
                    elif self.map[y - 1][x + count].type == 'EXIT':
                        exit.append(x + count)
                        exit.append(y - 1)
                        break

        elif self.angle % 360 == 300 and self.x % 2 == 1:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if count == 1:
                    if self.map[y][x + count].type == 'WALL':
                        wall.append(x + count)
                        wall.append(y)
                        break
                    elif self.map[y][x + count].type == 'EXIT':
                        exit.append(x + count)
                        exit.append(y)
                        break
                elif count == 2:
                    if self.map[y + 1][x + count].type == 'WALL':
                        wall.append(x + count)
                        wall.append(y + 1)
                        break
                    elif self.map[y + 1][x + count].type == 'EXIT':
                        exit.append(x + count)
                        exit.append(y + 1)
                        break

        elif self.angle % 360 == 300 and self.x % 2 == 0:
            count = 0
            end = random.randint(1, 2)
            while count != end:
                count += 1
                if self.map[y + 1][x + count].type == 'WALL':
                    wall.append(x + count)
                    wall.append(y + 1)
                    break
                elif self.map[y + 1][x + count].type == 'EXIT':
                    exit.append(x + count)
                    exit.append(y + 1)
                    break

        if len(wall) == 0:
            wall.append(-1)
            wall.append(-1)
        if len(exit) == 0:
            exit.append(-1)
            exit.append(-1)
        wall.append(1)
        exit.append(2)

        if type.value == 1:
            return wall
        else:
            return exit

    def exit(self):
        if self.map[self.y][self.x].type == 'EXIT':
            return True
        return False


if __name__ == '__main__':
    main()
