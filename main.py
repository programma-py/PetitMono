import pyxel

# ======================
# キャラクターごとの画像データ
# green / yellow / pink は「キャラクターの名前」
# sprites は　state(状態)ごとの画像のデータ
# 　(イメージバンク番号, X座標, Y座標, 幅, 高さ, 透明色)
# ======================

CHARACTER_DATA = {
    "green": {
        "sprites": {
            "IDLE": [(0, 32, 0, 16, 16, 2),
                     (0, 48, 0, 16, 16, 2)],
            "RUN":  [(0, 32, 16, 16, 16, 2),
                     (0, 48, 16, 16, 16, 2)],
            "JUMP": [(0, 32, 32, 16, 16, 2),
                     (0, 48, 32, 16, 16, 2)],
            "DOWN": [(0, 32, 48, 16, 16, 2),
                     (0, 48, 48, 16, 16, 2)],
        },
        "state_to_sprite": {
            "idle": "IDLE",
            "run": "RUN",
            "jump": "JUMP",
            "runj": "RUN",
            "down": "DOWN",
        }
    },

    "yellow": {
        "sprites": {
            "IDLE": [(0, 0, 0, 16, 16, 2),
                     (0, 16, 0, 16, 16, 2)],
        },
        "state_to_sprite": {
            "idle": "IDLE",
        }
    },

    "pink": {
        "sprites": {
            "IDLE": [(0, 64, 0, 16, 16, 2),
                     (0, 80, 0, 16, 16, 2)],
        },
        "state_to_sprite": {
            "idle": "IDLE",
        }
    },
}

ENEMY_DATA = {
    "sprites": {
        "MOVE":  [(0, 0, 64, 11, 11, 2),
                  (0, 16, 64, 11, 11, 2)],
        "BLAST": [(0, 0, 80, 11, 11, 2),
                  (0, 16, 80, 11, 11, 2)],
    },
    "state_to_sprite": {
        "move": "MOVE",
        "blast": "BLAST",
    }
}

def get_sprite_size(data, state):
    sprite_name = data["state_to_sprite"][state]
    _, _, _, width, height, _ = data["sprites"][sprite_name][0]
    return width, height

class Character:
    def __init__(self, character_name, x, y, state="idle"):
        self.character_name = character_name
        self.data = CHARACTER_DATA[character_name]

        self.state = state
        self.width, self.height = get_sprite_size(self.data, self.state)

        self.x = x
        self.y = y

    def draw(self):
        sprite_name = self.data["state_to_sprite"][self.state]
        sprites = self.data["sprites"]

        frame = (pyxel.frame_count // 20) % 2
        pyxel.blt(self.x, self.y, *sprites[sprite_name][frame])

class Player(Character):
    def __init__(self):
        super().__init__("green", 0, 0, "idle")

        self.x = pyxel.width // 2 - self.width // 2
        self.y = pyxel.height // 2 - self.height // 2

        self.speed = 0
        self.run_speed = 1
        self.jump_timer = 0
        self.jump_duration = 32

    def update(self):
        previous_state = self.state

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.state == "idle":
                self.state = "run"
                self.jump_timer = 0
            elif self.state == "run":
                self.state = "jump"
                self.jump_timer = self.jump_duration
            elif self.state == "down":
                self.state = "runj"
                self.jump_timer = self.jump_duration

        if self.state in ("jump", "runj"):
            if self.jump_timer > 0:
                self.jump_timer -= 1
            if self.jump_timer == 0:
                self.state = "run"

        if self.state != previous_state:
            self.width, self.height = get_sprite_size(self.data, self.state)

        if self.state in ("run", "runj", "jump"):
            self.speed = self.run_speed
            self.x += self.speed
            if self.x >= pyxel.width:
                self.x = -self.width
        else:
            self.speed = 0

    def draw(self):
        costume = self.data["state_to_sprite"][self.state]
        image_data = self.data["sprites"]

        if costume == "IDLE":
            frame = (pyxel.frame_count // 20) % 2
            pyxel.blt(self.x, self.y, *image_data[costume][frame])

        elif costume == "RUN":
            frame = (pyxel.frame_count // 8) % 2
            pyxel.blt(self.x, self.y, *image_data[costume][frame])

        elif costume == "JUMP":
            frame = (pyxel.frame_count // 4) % 2
            pyxel.blt(
                self.x,
                self.y - self.jump_timer,
                *image_data[costume][frame]
            )

        elif costume == "DOWN":
            frame = (pyxel.frame_count // 20) % 2
            pyxel.blt(self.x, self.y, *image_data[costume][frame])


class Enemy:
    def __init__(self):
        self.data = ENEMY_DATA

        self.state = "move"
        self.width, self.height = get_sprite_size(self.data, self.state)

        self.x = 10
        self.y = 60
        self.speed = -1.5

    def update(self):
        self.x += self.speed
        """
        if self.x <= 0 or self.x + self.width >= pyxel.width:
            self.speed = -self.speed
        """
        if self.x <0:
            self.x = pyxel.width

    def draw(self):
        costume = self.data["state_to_sprite"][self.state]
        image_data = self.data["sprites"]

        frame = (pyxel.frame_count // 8) % 2
        pyxel.blt(self.x, self.y, *image_data[costume][frame])


class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("my_resource.pyxres")

        self.player = Player()

        self.friends = [
            Character("yellow", 10, 10),
            Character("pink" , 130, 10),
        ]

        self.enemies = [
            Enemy()
        ]

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.player.update()

        if self.player.state == "run":
            for enemy in self.enemies:
                if self.check_collision(self.player, enemy):
                    self.player.state = "down"
                    break

        if self.player.state in ("run", "runj", "jump"):
            for enemy in self.enemies:
                enemy.update()

    def check_collision(self, player, enemy):
        return (
            player.x < enemy.x + enemy.width
            and enemy.x < player.x + player.width
            and player.y < enemy.y + enemy.height
            and enemy.y < player.y + player.height
        )

    def text_draw(self, text, x, y, color1, color2):
        pyxel.rect(x - 2, y - 2, len(text) * 4 + 4, 8, color2)
        pyxel.text(x, y, text, color1)

    def draw(self):
        pyxel.cls(1)

        self.player.draw()

        for friend in self.friends:
            friend.draw()

        if self.player.state in ("run", "runj", "jump"):
            for enemy in self.enemies:
                enemy.draw()

        text = "PUTIT MONO"
        text_x = (pyxel.width - len(text) * 4) // 2
        self.text_draw(text, text_x, 10, 10, 1)

        if self.player.state in ("idle", "down"):
            text = "CLICK OR TAP TO START"
            text_x = (pyxel.width - len(text) * 4) // 2
            text_y = pyxel.height - 16
            self.text_draw(text, text_x, text_y, 3, 7)

        elif self.player.state in ("run", "jump"):
            text = "CLICK OR TAP TO JUMP"
            text_x = (pyxel.width - len(text) * 4) // 2
            text_y = pyxel.height - 16           
            self.text_draw(text, text_x, text_y, 9, 7)


App()