import pika
import sys
from threading import Thread
import pygame
import colorsys
import json
import random
import math
name = 'Meyrambek'

connection = pika.BlockingConnection(pika.ConnectionParameters('142.93.107.56'))
prodchennel = connection.channel()
speed = 2

pygame.init()

font = pygame.font.SysFont('Arial', 14)
fonterer = pygame.font.SysFont('Times new roman', 32)

Grad = math.pi/180
class Tank():
    def __init__(self, namae, color = (0, 255, 0)):
        self.x, self.y = 100, 100
        self.color= color
        self.speed = 2
        self.degreeTank = 0
        self.degreeCannon = 0
        self.namae = namae
        self.attack = False
        self.attacktime = 0
        self.hp = 3
        self.score = 0
        self.coordinate =[[15*math.cos((45+self.degreeTank)*Grad)+self.x, 15*math.sin((45+self.degreeTank)*Grad)+self.y], [15*math.cos((self.degreeTank+135)*Grad)+self.x, 15*math.sin((self.degreeTank+135)*Grad)+self.y], [15*math.cos((self.degreeTank+225)*Grad)+self.x, 15*math.sin((self.degreeTank+225)*Grad)+self.y], [15*math.cos((self.degreeTank+315)*Grad)+self.x, 15*math.sin((self.degreeTank+315)*Grad)+self.y]]
    def draw(self):
        self.coordinate =[[15*math.cos((45+self.degreeTank)*Grad)+self.x, 15*math.sin((45+self.degreeTank)*Grad)+self.y], [15*math.cos((self.degreeTank+135)*Grad)+self.x, 15*math.sin((self.degreeTank+135)*Grad)+self.y], [15*math.cos((self.degreeTank+225)*Grad)+self.x, 15*math.sin((self.degreeTank+225)*Grad)+self.y], [15*math.cos((self.degreeTank+315)*Grad)+self.x, 15*math.sin((self.degreeTank+315)*Grad)+self.y]]
        pygame.draw.polygon(screen, self.color, [(int(self.coordinate[0][0]),int(self.coordinate[0][1])), (int(self.coordinate[1][0]),int(self.coordinate[1][1])),(int(self.coordinate[2][0]),int(self.coordinate[2][1])),(int(self.coordinate[3][0]),int(self.coordinate[3][1]))], 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 8)
        pygame.draw.line(screen, self.color, (int(self.x), int(self.y)), (int(self.x+ 25*math.cos(self.degreeCannon*Grad)), int(self.y+ 25*math.sin(self.degreeCannon*Grad))), 3)
        nametext = font.render(self.namae, True, self.color)
        #screen.blit(nametext, (int(self.x), int(self.y-20)))
        textRect = nametext.get_rect() 
        textRect.center = (int(self.x), int(self.y-22))
        screen.blit(nametext, textRect)
    def MoveUP(self):
        self.x+=self.speed*math.cos(self.degreeTank*Grad)
        self.y+=self.speed*math.sin(self.degreeTank*Grad)
    def MoveDown(self):
        self.x-=self.speed*math.cos(self.degreeTank*Grad)        
        self.y-=self.speed*math.sin(self.degreeTank*Grad)
    def MoveRight(self):
        self.degreeCannon +=1
        self.degreeTank +=1
    def MoveLeft(self):
        self.degreeTank -= 1
        self.degreeCannon -= 1
    def RoatCannonLeft(self):
        self.degreeCannon -= 2
    def RoatCannonRight(self):
        self.degreeCannon += 2

bullets = []

class Bullet():
    def __init__(self, x, y, a, color, tank):
        self.x = x
        self.y = y
        self.tank = tank
        self.degree = a
        self.time = 3
        self.color = color
        self.radius = 3
    def move(self):
        self.x+=4*math.cos(self.degree*Grad)
        self.y+=4*math.sin(self.degree*Grad)
        self.draw()
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)







players = {}
myplayer = Tank(name)
players[name] = myplayer
class Producer(Thread):
        
    def run(self):
        prodchennel.exchange_declare(exchange='logs',exchange_type='fanout')

    def sendmessage(self,message):
        prodchennel.basic_publish(exchange='logs',routing_key='',body=message)

    def close(self):
        prodchennel.close()


class Consumer(Thread):
    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('142.93.107.56'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='logs',exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='logs', queue=queue_name)
        
        def callback(ch,method,properties,body):
            parsedjs = json.loads(body)
            pl = parsedjs
            for k in pl:
                if(k != name):
                    if k in players: 
                        players[k].x = pl[k]['x']
                        players[k].y = pl[k]['y']
                        players[k].degreeTank = pl[k]['tankdeg']
                        players[k].degreeCannon = pl[k]['candeg']
                        players[k].hp = pl[k]['hp']
                        players[k].color = (255, 0, 0)
                        players[k].namae = k
                        if pl[k]['attack'] == True:
                            bullets.append(Bullet(int(players[k].x+ 25*math.cos(players[k].degreeCannon*Grad)), int(players[k].y+ 25*math.sin(players[k].degreeCannon*Grad)), players[k].degreeCannon, players[k].color, players[k]))
                        # players[k].a = pl[k]['a']
                    else:
                        newp = Tank((255, 0, 0), str(k))
                        players[k] = newp
                        print(k+' Joined the game')
                        print('', end = '')

        self.channel.basic_consume(queue=queue_name,on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
    
    def close(self):
        self.channel.close()

prd = Producer()
prd.start()
con = Consumer()
con.start()

screen_x = 800
screen_y = 600
screen = pygame.display.set_mode((screen_x, screen_y))
def selfinfo():
    scoretext = fonterer.render('S C O R E:'+str(myplayer.score), True, myplayer.color)
    hptext = fonterer.render('H P:'+str(myplayer.hp), True, myplayer.color)
    screen.blit(scoretext, (10, 10))
    screen.blit(hptext, (10, 40))

clock = pygame.time.Clock()
FPS = 60

while True:
    ms = clock.tick(FPS)
    sec = ms/1000
    myplayer.attacktime-=sec
    pressed = pygame.key.get_pressed()
    for event in pygame.event.get(): # this empties the event queue. 
        if event.type == pygame.QUIT: 
            prd.close()
            con.close()
            break
    if pressed[pygame.K_w] == True: 
        myplayer.MoveUP()
    if pressed[pygame.K_s] == True:
        myplayer.MoveDown()
    if pressed[pygame.K_d] == True:
        myplayer.MoveRight()
    if pressed[pygame.K_a] == True:
        myplayer.MoveLeft()
    if pressed[pygame.K_SPACE] == True:
        if myplayer.attacktime<=0:
            myplayer.attack = True
            myplayer.attacktime = 2
            bullets.append(Bullet(int(myplayer.x+ 25*math.cos(myplayer.degreeCannon*Grad)), int(myplayer.y+ 25*math.sin(myplayer.degreeCannon*Grad)), myplayer.degreeCannon, myplayer.color, myplayer))
    if pressed[pygame.K_KP1]: myplayer.RoatCannonLeft()
    if pressed[pygame.K_KP2]: myplayer.RoatCannonRight()

    players[name] = myplayer
    screen.fill((0,0,0))

    playerstatic = players.values() #need this so ammount of players doen't not change while in a loop

    for p in playerstatic:
        p.draw()
    for b in bullets:
        b.move()
        b.time -= sec
    
    for i in range(len(bullets)):
        for p in playerstatic:
            if (bullets[i].x-p.x)**2+(bullets[i].y-p.y)**2<=550:
                bullets[i].time=0
                p.hp-=1
                bullets[i].tank.score+=1
    try:
        for i in range(len(bullets)):
            if bullets[i].time<=0:
                bullets.pop(i)
        for p in playerstatic:
            if p.hp<=0:
                print('',end='')
    except IndexError:
        print('', end='')
    localplayergame = {name:{'x':myplayer.x,'y':myplayer.y,'tankdeg':myplayer.degreeTank, 'candeg':myplayer.degreeCannon, 'attack':myplayer.attack, 'hp':myplayer.hp}}
    myplayer.attack = False
    prd.sendmessage(json.dumps(localplayergame))
    selfinfo()
    pygame.display.flip()