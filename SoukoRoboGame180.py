import pyxel


class App():
    def __init__(self):
        pyxel.init(180,180,title="倉庫ロボ",fps=24)
        pyxel.load("souko.pyxres")
        self.define_values()
        self.stage_num = 0  # stage_num=0 がステージ1
        self.init_stage()
        pyxel.run(self.update,self.draw)

    def define_values(self):
        ### 定数として使用する変数を定義
        self.MAX_STAGE = 18      # 最終ステージ番号
        self.FLOOR = (0,0)       # 床
        self.GOAL = (1,0)        # ゴール地点
        self.PACK = (0,2)        # 荷物
        self.PACKONGOAL = (1,2)  # ゴール地点上の荷物
        self.ROBO = [(0,3),(1,3),(2,3),(3,3)]  # 下、上、左、右
        self.KEY = [pyxel.KEY_DOWN,pyxel.KEY_UP,pyxel.KEY_LEFT,pyxel.KEY_RIGHT]
        self.DPAD = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,pyxel.GAMEPAD1_BUTTON_DPAD_UP,\
                      pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT]
        self.D = [[0,1],[0,-1],[-1,0],[1,0]]   # 方向に対する増減値

    def init_stage(self):
        self.stage_tiles = []
        self.goal_num = 0
        start_tile_x = self.stage_num%16*16
        start_tile_y = int(self.stage_num/16)*16
        #print("{},{}".format(start_tile_x,start_tile_y))
        for y in range(16):
            for x in range(16):
                cell = pyxel.tilemaps[0].pget(start_tile_x + x,start_tile_y + y)
                self.stage_tiles.append(cell)
                if cell == self.ROBO[0]:
                    self.robo_pos = [start_tile_x + x,start_tile_y + y]
                elif cell == self.GOAL:
                    self.goal_num += 1
        self.is_robo_on_goal = False  # ゴールの上にいるフラグ
        self.is_stage_clear = False  # ステージクリアしたフラグ

    def restart_stage(self):
        self.goal_num = 0
        start_tile_x = self.stage_num%16*16
        start_tile_y = int(self.stage_num/16)*16
        for y in range(16):
            for x in range(16):
                cell = self.stage_tiles[ y * 16 + x ]
                pyxel.tilemaps[0].pset(start_tile_x + x,start_tile_y + y,cell)
                if cell == self.ROBO[0]:
                    self.robo_pos = [start_tile_x + x,start_tile_y + y]
                elif cell == self.GOAL:
                    self.goal_num += 1
        self.is_robo_on_goal = False  # ゴールの上にいるフラグ
        self.is_stage_clear = False  # ステージクリアしたフラグ

    def update(self):
        #n = self.stage_num

        ### ステージクリア表示中！　スペースキーで次の面に進みます
        if self.is_stage_clear:
            if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)) and self.stage_num < self.MAX_STAGE:
                self.is_stage_clear = False
                self.stage_num += 1
                self.init_stage()
            return
        ### ステージクリアの判定
        elif self.goal_num == 0 or pyxel.btnp(pyxel.KEY_7):
            self.is_stage_clear = True
            return

        ### ステージをREST@RTするか？
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            self.restart_stage()
            return

        ### ロボの操作（カーソルキー入力と移動可否の判定）
        #for i,k in enumerate(self.KEY):
        for i in range(4):
            if pyxel.btnp(self.KEY[i]) or pyxel.btnp(self.DPAD[i]):
                robo_x = self.robo_pos[0]
                robo_y = self.robo_pos[1]
                tile_fx = robo_x + self.D[i][0]
                tile_fy = robo_y + self.D[i][1]
                tile_fx2 = robo_x + self.D[i][0]*2
                tile_fy2 = robo_y + self.D[i][1]*2
                tile_fwd = pyxel.tilemaps[0].pget(tile_fx,tile_fy)
                tile_fwd2 = pyxel.tilemaps[0].pget(tile_fx2,tile_fy2)

                ### 進行方向が床だったら、ロボが進むよ
                if tile_fwd == self.FLOOR:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = False

                ### 進行方向がゴール地点だったら、フラグを立ててロボが進むよ
                elif tile_fwd == self.GOAL:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = True
                    
                ### 進行方向が荷物でその先が床だったら、荷物を押してロボが進むよ
                elif tile_fwd == self.PACK and tile_fwd2 == self.FLOOR:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # 荷物を移動
                    pyxel.tilemaps[0].pset(tile_fx2,tile_fy2,self.PACK)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = False

                ### 進行方向が荷物でその先がゴール地点だったら～～～
                elif tile_fwd == self.PACK and tile_fwd2 == self.GOAL:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # 荷物を移動　※ゴール上の荷物にChange！
                    pyxel.tilemaps[0].pset(tile_fx2,tile_fy2,self.PACKONGOAL)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = False
                    # ゴールすべきノルマを1減らす
                    self.goal_num -= 1

                ### 進行方向がゴール上の荷物でその先が床だったら～～～
                elif tile_fwd == self.PACKONGOAL and tile_fwd2 == self.FLOOR:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # ゴール上の荷物を移動　※普通の荷物にChange！
                    pyxel.tilemaps[0].pset(tile_fx2,tile_fy2,self.PACK)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = True
                    # ゴールすべきノルマを1増やす
                    self.goal_num += 1

                ### 進行方向がゴール上の荷物でその先がゴールだったら～～～
                elif tile_fwd == self.PACKONGOAL and tile_fwd2 == self.GOAL:
                    if self.is_robo_on_goal: # ゴール地点の上にいたならば、
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.GOAL)
                    else: # ゴール地点の上にいなかったら床の上でしたね
                        pyxel.tilemaps[0].pset(robo_x,robo_y,self.FLOOR)
                    # ゴール上の荷物を移動　※そのままゴール上の荷物
                    pyxel.tilemaps[0].pset(tile_fx2,tile_fy2,self.PACKONGOAL)
                    # ロボを移動
                    pyxel.tilemaps[0].pset(tile_fx,tile_fy,self.ROBO[i])
                    self.robo_pos = [tile_fx,tile_fy]
                    # 床の上かゴール地点の上かをフラグで管理
                    self.is_robo_on_goal = True



    def draw(self):
        ### ステージの表示
        start_tile_x = self.stage_num%16*128
        start_tile_y = int(self.stage_num/16)*128
        pyxel.cls(7)
        pyxel.bltm(0,0,0,start_tile_x,start_tile_y,128,128,7)
        pyxel.text(6,132,"Stage {}".format(self.stage_num+1),0)

        ### ステージクリアしている時のメッセージ表示
        if self.is_stage_clear:
            if self.stage_num < self.MAX_STAGE:
                pyxel.text(44,142,"Stage Clear!",pyxel.frame_count%15+1)
                pyxel.text(41,160,"Hit SpaceKey / A-Button\n to Next Stage",8)
            else:
                pyxel.text(24,140,"Cleared all stages.",pyxel.frame_count%15+1)
                pyxel.text(24,148,"Congratulations!",(pyxel.frame_count+8)%15+1)
        ### ステージクリアしていない時のメッセージ表示
        else:
            pyxel.text(44,132,"Move  :UP,DOWN,RIGHT,LEFT",0)
            pyxel.text(44,140,"ReSet :Enter Key / X-Button",0)

App()

