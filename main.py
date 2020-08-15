import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.graphics import Color
from random import randint
from copy import deepcopy

#Window.size = (720, 1280) #JUST FOR TESTING, REMOVE WHEN BUILDING FOR ANDROID
Window.clearcolor = (0.09, 0.024, 0.204, 1)

class MyGrid(Widget):
    label_score = StringProperty()
    label_highscore = StringProperty()

    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.window_width, self.window_height = Window.size
        self.scale_ratio = 2048 / self.window_width
        self.canvas_pos = (0, 200)
        self.cell_width = 472 / self.scale_ratio
        self.cell_padding = 32 / self.scale_ratio
        self.canvas_x = self.cell_padding
        self.canvas_y = 200 + self.window_width - self.cell_padding - self.cell_width
        self.grid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_temp = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_animate_1 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_animate_2 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_animate_3 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.gesture_start = (0, 0)
        self.gesture_end = (0, 0)
        self.gesture_dir = ""
        self.drawn_tiles = []
        self.score = 0
        self.label_score = "0"
        self.label_highscore = "0"
        self.anim_frame = -1
        self.popup = False

        #init game grid
        self.place_start_tiles()
        with self.canvas:
            self.size = (500, 500)
            self.rect = Rectangle(source='./images/grid.png', pos = self.canvas_pos, size = (self.window_width, self.window_width))
        self.draw_grid()

        self.update_score()

    def place_start_tiles(self):
        ran_1_x = randint(0,3)
        ran_1_y = randint(0,3)
        ran_2_x = randint(0,3)
        ran_2_y = randint(0,3)
        while ran_1_x == ran_2_x and ran_1_y == ran_2_y:
            ran_2_x = randint(0,3)
            ran_2_y = randint(0,3)
        self.grid[ran_1_y][ran_1_x] = randint(1,2) * 2
        self.grid[ran_2_y][ran_2_x] = randint(1,2) * 2

    def clear_drawn_tiles(self):
        for tile in self.drawn_tiles:
            self.canvas.remove(tile)
        self.drawn_tiles = []

    def draw_grid(self):
        self.clear_drawn_tiles()
        for i in range(4):
            for j in range(4):
                cell_value = self.grid[i][j]
                if cell_value > 0:
                    with self.canvas:
                        image_file = './images/tile_' + str(cell_value) + '.png'
                        offset_x = self.canvas_x + (self.cell_padding + self.cell_width) * j
                        offset_y = self.canvas_y - (self.cell_padding + self.cell_width) * i
                        self.drawn_tiles.append(Rectangle(source = image_file, pos = (offset_x, offset_y), size = (self.cell_width, self.cell_width)))

    def get_gesture_dir(self, start, end):
        start_x, start_y = start
        end_x, end_y = end
        length_x = end_x - start_x
        length_y = end_y - start_y
        
        if abs(length_x) > abs(length_y):
            if length_x > 100:
                self.gesture_dir = "right"
            else:
                self.gesture_dir = "left"
        else:
            if length_y > 100:
                self.gesture_dir = "up"
            elif length_y < -100:
                self.gesture_dir = "down"
            else:
                self.gesture_dir = "click"
                return False
        return True

    def init_grid_temp(self):
        self.grid_temp = deepcopy(self.grid)
        self.grid_animate_1 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_animate_2 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.grid_animate_3 = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    def move_tiles(self, grid_animate):
        if self.gesture_dir == "left":
            for i in range(4):
                count = 0
                for j in range(4):
                    if self.grid_temp[i][j] != 0:
                        self.grid_temp[i][count] = self.grid_temp[i][j]
                        count += 1
                        grid_animate[i][j] -= j - count+1
                while count < 4:
                    self.grid_temp[i][count] = 0
                    count += 1
        if self.gesture_dir == "right":
            for i in range(4):
                count = 0
                for j in range(4):
                    if self.grid_temp[-i-1][-j-1] != 0:
                        self.grid_temp[-i-1][-count-1] = self.grid_temp[-i-1][-j-1]
                        count += 1
                        grid_animate[-i-1][-j-1] += j - count+1
                while count < 4:
                    self.grid_temp[-i-1][-count-1] = 0
                    count += 1
        if self.gesture_dir == "up":
            for j in range(4):
                count = 0
                for i in range(4):
                    if self.grid_temp[i][j] != 0:
                        self.grid_temp[count][j] = self.grid_temp[i][j]
                        count += 1
                        grid_animate[i][j] -= i - count+1
                while count < 4:
                    self.grid_temp[count][j] = 0
                    count += 1
        if self.gesture_dir == "down":
            for j in range(4):
                count = 0
                for i in range(4):
                    if self.grid_temp[-i-1][-j-1] != 0:
                        self.grid_temp[-count-1][-j-1] = self.grid_temp[-i-1][-j-1]
                        count += 1
                        grid_animate[-i-1][-j-1] += i - count+1
                while count < 4:
                    self.grid_temp[-count-1][-j-1] = 0
                    count += 1

    def merge_tiles(self):
        if self.gesture_dir == "left":
            for i in range(4):
                cursor = 0
                while cursor < 3:
                    if self.grid_temp[i][cursor] == self.grid_temp[i][cursor+1] and self.grid_temp[i][cursor] != 0:
                        self.grid_temp[i][cursor] = self.grid_temp[i][cursor] * 2
                        self.score += self.grid_temp[i][cursor]
                        self.grid_temp[i][cursor+1] = 0
                        self.grid_animate_2[i][cursor+1] = -1 
                        cursor += 2
                    else:
                        cursor += 1
        if self.gesture_dir == "right":
            for i in range(4):
                cursor = 1
                while cursor < 4:
                    if self.grid_temp[i][-cursor] == self.grid_temp[i][-cursor-1] and self.grid_temp[i][-cursor] != 0:
                        self.grid_temp[i][-cursor] = self.grid_temp[i][-cursor] * 2
                        self.score += self.grid_temp[i][-cursor]
                        self.grid_temp[i][-cursor-1] = 0
                        self.grid_animate_2[i][-cursor-1] = 1
                        cursor += 2
                    else:
                        cursor += 1
        if self.gesture_dir == "up":
            for j in range(4):
                cursor = 0
                while cursor < 3:
                    if self.grid_temp[cursor][j] == self.grid_temp[cursor+1][j] and self.grid_temp[cursor][j] != 0:
                        self.grid_temp[cursor][j] = self.grid_temp[cursor][j] * 2
                        self.score += self.grid_temp[cursor][j]
                        self.grid_temp[cursor+1][j] = 0
                        self.grid_animate_2[cursor+1][j] = -1
                        cursor += 2
                    else:
                        cursor += 1
        if self.gesture_dir == "down":
            for j in range(4):
                cursor = 1
                while cursor < 4:
                    if self.grid_temp[-cursor][j] == self.grid_temp[-cursor-1][j] and self.grid_temp[-cursor][j] != 0:
                        self.grid_temp[-cursor][j] = self.grid_temp[-cursor][j] * 2
                        self.score += self.grid_temp[-cursor][j]
                        self.grid_temp[-cursor-1][j] = 0
                        self.grid_animate_2[-cursor-1][j] = 1
                        cursor += 2
                    else:
                        cursor += 1
    
    def animate_move(self, clockneedsthisforsomereason):
        if self.anim_frame > 0:
            # Animate 1
            count = 0
            if self.gesture_dir == "left" or self.gesture_dir == "right":
                for i in range(4):
                    for j in range(4):
                        if self.grid[i][j] != 0:
                            anim_offset_1 = self.grid_animate_1[i][j]
                            anim_offset_2 = self.grid_animate_2[i][j + anim_offset_1]
                            anim_offset_3 = self.grid_animate_3[i][j + anim_offset_2]
                            offset = anim_offset_1 + anim_offset_2 + anim_offset_3
                            self.drawn_tiles[count].pos = (self.drawn_tiles[count].pos[0] + offset * (self.cell_width/20), self.drawn_tiles[count].pos[1])
                            count += 1
            if self.gesture_dir == "up" or self.gesture_dir == "down":
                for i in range(4):
                    for j in range(4):
                        if self.grid[i][j] != 0:
                            anim_offset_1 = self.grid_animate_1[i][j]
                            anim_offset_2 = self.grid_animate_2[i + anim_offset_1][j] 
                            anim_offset_3 = self.grid_animate_3[i + anim_offset_2][j]
                            offset = anim_offset_1 + anim_offset_2 + anim_offset_3
                            self.drawn_tiles[count].pos = (self.drawn_tiles[count].pos[0], self.drawn_tiles[count].pos[1] - offset * (self.cell_width/20))
                            count += 1
            self.anim_frame -= 1
        if self.anim_frame == 0:
            self.grid = self.grid_temp
            if self.empty_cell():
                    self.add_new_tile()
            self.check_game_over()
            self.anim_frame = -1
        if self.anim_frame == -1:
            self.draw_grid()

    def add_new_tile(self):
        tile_placed = False
        while tile_placed == False:
            ran_x = randint(0,3)
            ran_y = randint(0,3)
            if self.grid[ran_y][ran_x] == 0:
                self.grid[ran_y][ran_x] = randint(1,2) * 2
                tile_placed = True

    def empty_cell(self):
        empty_cell = False
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    empty_cell = True
        return empty_cell

    def update_score(self):
        score_file = open("./score.txt","r+")
        saved_score = int(score_file.read())
        score_file.close()
        if saved_score < self.score:
            score_file = open("./score.txt","w+")
            score_file.write(str(self.score))
            saved_score = self.score
            score_file.close()
        self.label_score = str(self.score)
        self.label_highscore = str(saved_score)

    def check_game_over(self):
        possible_move = False
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    possible_move = True
                if i < 3:
                    if self.grid[i][j] == self.grid[i+1][j]:
                        possible_move = True
                if j < 3:
                    if self.grid[i][j] == self.grid[i][j+1]:
                        possible_move = True
        if not possible_move:
            self.show_popup()

    def show_popup(self):
        self.popup = True
        show = P()
        popup_window = Popup(title="Game Over!", title_size=self.window_width*0.07, content=show, size_hint=(None, None), size=(self.window_width*0.5,self.window_width*0.3))
        popup_window.open()


    def restart_game(self):
        self.grid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.score = 0
        self.update_score()
        self.place_start_tiles()

    def on_touch_down(self, touch):
        self.gesture_start = touch.pos

    def on_touch_move(self, touch):
        pass

    def on_touch_up(self, touch):
        self.gesture_end = touch.pos
        if self.get_gesture_dir(self.gesture_start, self.gesture_end) and self.anim_frame == -1:
            self.init_grid_temp()
            self.move_tiles(self.grid_animate_1)
            self.merge_tiles()
            self.move_tiles(self.grid_animate_3)
            if self.grid != self.grid_temp:
                self.anim_frame = 20
        else:
            if self.popup == True:
                self.restart_game()
                self.popup = False
        self.update_score()

class P(FloatLayout):
    pass

class MyApp(App):
    def build(self):
        self.icon = './images/tile_2048.png'
        game = MyGrid()
        Clock.schedule_interval(game.animate_move, 1.0 / 60.0)
        return game

if __name__ == "__main__":
    MyApp().run()