import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256

FPS = 30
NUM_INITIAL_TRIANGLES = 5
NUM_INITIAL_CIRCLES = 5


# 円の位置構造体
class Pos2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# 三角形の位置構造体
class Pos3(Pos2):
    def __init__(self,x:float,y:float, r:float):

        super().__init__(x,y)
        # 頂点
        self.tripos1 = Pos2(x, y - r)
        # 左下
        self.tripos2 = Pos2(x - (r * pyxel.sin(60)),y + (r * pyxel.cos(60)))
        # 右下
        self.tripos3 = Pos2(x + (r * pyxel.sin(60)),y + (r * pyxel.cos(60)))

class Circle:
    def __init__(self):

        #半径をランダムで設定
        self.r = pyxel.rndf(10, 20)

        #半径 ~ 境界線 - 半径 の範囲で位置を設定
        self.pos = Pos2(
            pyxel.rndf(self.r, SCREEN_WIDTH - self.r),
            pyxel.rndf(self.r, SCREEN_HEIGHT - self.r),
        )
        
        #色を設定
        self.color = pyxel.rndi(1, 15)

    def update(self):
        pass


class Triangle(Circle):
    def __init__(self):
        super().__init__()
        self.tripos = Pos3(self.pos.x,self.pos.y,self.r)
    def update(self):
        self.tripos = Pos3(self.pos.x,self.pos.y,self.r)


class App:
    def __init__(self):
        self.is_completed = False
        self.is_gameover = False
        self.is_gamestop = False
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Click Circle!!", capture_scale=1,fps=FPS)
        pyxel.mouse(True)
        pyxel.load('sound.pyxres')
        self.is_firstclicked = False
        # 設定値分　図形を作成する
        self.shapes = [Circle() for _ in range(NUM_INITIAL_CIRCLES)]
        self.shapes += [Triangle() for _ in range(NUM_INITIAL_TRIANGLES)]

        pyxel.run(self.update, self.draw)

    def __gen_scorestr(self):
        sec_passed = pyxel.frame_count / FPS
        #秒数に応じてスコアを変える
        if sec_passed < 5:
            res_str = 'Congratulations!'
            self.endsound = 3
        elif sec_passed < 7:
            res_str = 'Great!'
            self.endsound = 2
        elif sec_passed <= 10:
            res_str = 'Clear'
            self.endsound = 2
        elif sec_passed > 10:
            res_str = 'GameOver....'
            self.is_gameover =  True
        return res_str

    def update(self):
        #ゲームが終了していたら以下の処理は行わない
        if self.is_gamestop:

            return

        #Qボタンでゲーム終了する
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        num_shapes = len(self.shapes)

        #左クリックしたときの処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i in range(num_shapes):
                shape = self.shapes[i]
                # shapeのx座標とy座標からマウスのx座標とy座標の差を求め
                dx = shape.pos.x - pyxel.mouse_x
                dy = shape.pos.y - pyxel.mouse_y

                # 3平方の定理から、クリックが円の範囲内かどうかを判定する
                if dx * dx + dy * dy < shape.r * shape.r:
                    self.is_firstclicked = True

                    #クリック音の再生
                    
                    pyxel.play(0,0,False)

                    #三角をくりっくしたら、ゲームオーバーにする
                    if shape.__class__.__name__ == 'Triangle':
                        self.is_gameover = True

                    #クリックした図形を削除
                    del self.shapes[i]
                    break

        num_shapes = len(self.shapes)

        #図形同士の位置関係を確認
        for i in range(num_shapes - 1, -1, -1):
            bi = self.shapes[i]

            bi.update()

            #別のshapeと位置関係を比較
            for j in range(i - 1, -1, -1):
                bj = self.shapes[j]
                dx = bi.pos.x - bj.pos.x
                dy = bi.pos.y - bj.pos.y
                total_r = bi.r + bj.r
                #接触した場合
                if dx * dx + dy * dy < total_r * total_r:
                    
                    # 番号が後ろのShapeの位置を右下にずらす
                    bj.pos.x += bj.r / 5
                    bj.pos.y += bj.r / 5

                    # 番号が前のShapeの位置を左上にずらす
                    bj.pos.x += bj.r / 5
                    bj.pos.y += bj.r / 5


    def draw(self):

        pyxel.cls(0)
        #終了フラグをたてる
        self.is_completed = True

        for shape in self.shapes:
            if shape.__class__.__name__ == 'Circle':
                # 円の描画
                pyxel.circ(shape.pos.x, shape.pos.y, shape.r, shape.color)
                # 円が残っていたら終了にしない
                self.is_completed = False
            elif shape.__class__.__name__ == 'Triangle':
                # 三角形の描画
                pyxel.tri(shape.tripos.tripos1.x, shape.tripos.tripos1.y, shape.tripos.tripos2.x, shape.tripos.tripos2.y, shape.tripos.tripos3.x, shape.tripos.tripos3.y, shape.color)
            else:
                pass

        # ゲームが開始されるまで、案内文字列を点滅させる
        if not self.is_firstclicked and pyxel.frame_count % 20 < 10:
            pyxel.text(96, 50, "Click  Circle", pyxel.frame_count % 15 + 1)

        #現在のスコアを計算
        if self.is_gamestop is False:
            self.res_str = self.__gen_scorestr()

        #ゲームオーバーフラグの処理
        if self.is_gameover:
            s = 'GameOver...'
            pyxel.text(110, 100, s,7)
            #1回だけサウンド再生
            if self.is_gamestop is False:
                self.endsound = 1
                pyxel.play(0,self.endsound,False)
            self.is_gamestop = True
        elif self.is_completed:
            s = self.res_str
            pyxel.text(110, 100, s,7)
            #1回だけサウンド再生
            if self.is_gamestop is False:
                pyxel.play(0,self.endsound,False)
            self.is_gamestop = True

App()
