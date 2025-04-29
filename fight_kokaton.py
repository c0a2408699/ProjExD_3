import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.center = bird.rct.center
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
    #     """
    #     ビームを速度ベクトルself.vx, self.vyに基づき移動させる
    #     引数 screen：画面Surface
    #     """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)
        
class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.rad=rad
        self.img = pg.Surface((2*rad, 2*rad))
        self.color=(255, 200, 0)
        pg.draw.circle(self.img, self.color, (rad, rad), rad)       
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +3, +3
        self.hp=3
    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.img = pg.Surface((2*self.rad, 2*self.rad))
        #色の変化を反映
        pg.draw.circle(self.img, self.color, (self.rad, self.rad),  self.rad)
        self.img.set_colorkey((0, 0, 0))
        yoko, tate = check_bound(self.rct) 
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)
    """
    体力処理
    """
    def damage(self,damage,life):
        #無敵時間じゃなかったら
        if life<=0:
            #hpからダメージを引く
            self.hp-=int(damage)
            #ダメージを受けるたびに1.7倍加速
            self.vx *= 1.7
            self.vy *= 1.7
            #色設定
            if self.hp==2:
                self.color=(255, 100, 0)
            if self.hp==1:
                self.color=(255, 0, 0)
    def get_hp(self): 
        return int(self.hp)
  

class Score:
    """
    スコア表示クラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)    
    def update(self,playscore,screen):
            self.txt = self.fonto.render("スコア："+str(playscore), False, (0, 0, 255))
            screen.blit(self.txt, [100, screen.get_height()-50])


class Explosion:
    """
    爆発エフェクト
    """
    def __init__ (self):
         self.img = pg.image.load(f"fig/explosion.gif")
         self.imgs=[self.img,pg.transform.flip(self.img, True, True)]
         self.rct = self.img.get_rect()
         self.i=0
    def update(self,screen,bomb,life):
        if life>0:
            self.i=(life/8)%2
            self.rct.center = bomb.rct.center
            screen.blit(self.imgs[int(self.i)], self.rct)
       
            
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    NUM_OF_BOMS=5
    bombs=[]
    clock = pg.time.Clock() 
    tmr = 0
    score=Score()
    playscore=0
    explosion=Explosion()  
    life=0
    beams=[]
    for i in range (0,NUM_OF_BOMS):
        bombs.append(Bomb(20))


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            # スペースキーでBeamクラスのインスタンス生成
                beams.append(Beam(bird)) 
        screen.blit(bg_img, [0, 0])
        for bomb in bombs:  
            #爆弾の数だけ判定を追加
            if bird.rct.colliderect(bomb.rct):
            #ゲームオーバー画面    
            # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80) 
                txt = fonto.render("Game Over", True, (255, 0, 0)) 
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                return
        for bomb in bombs:     
            for beam in beams:
                if beam != None and bomb!=None:  
                    if beam.rct.colliderect(bomb.rct):
                    # ビームで撃ち落とす
                    #爆発座標取得    
                        explode_bomb=bomb
                    #ビーム削除  
                        beams.remove(beam)
                    #lifeが0以下でダメージ判定
                        bomb.damage(1,life)
                    #玉の無敵時間と爆発エフェクトの表示時間
                        if bomb.get_hp()==0 and life<=0:   
                            bombs.remove(bomb)
                        life=50
                        playscore+=1
                        bird.change_img(6, screen)  
                    #ヒットストップ
                        pg.display.update() 
        for beam in beams:
            yoko, tate = check_bound(beam.rct)
            if not yoko and not tate:
                beams.remove   
            if beam is not None:
                beam.update(screen)
        for bomb in bombs:
            if bomb is not None:
                bomb.update(screen)
                #着弾判定
                if life>0:
                    explosion.update(screen,explode_bomb,life)
                    life-=1
        key_lst = pg.key.get_pressed()
        score.update(playscore,screen)
        bird.update(key_lst, screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
