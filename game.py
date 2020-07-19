import ui
from levels import levels
from pygame import *
import os
from math import copysign, sqrt
from random import random

view = sprite.Group()
room = None

running = True

instructions = (
	"You're trying to escape a house",
	"filled with zombies",
	"(don't ask how did you get there)",
	"but your legs are",
	"out of your control.",
	"the only thing you can do is shoot",
	"at the zombies (with left-click).",
)

credits = (
	"Game made by K-39",
	"for the GMTK's Game Jam of 2020.",
	"the theme was :",
	"out of control",
)

bgroom = ( # background for the menus
	"....................",
	".b44444444444444448.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700000000000000005.",
	".700120000000000005.",
	".700000000000000005.",
	".a66666666666666669.",
)

def direction(relx, rely): # get the direction from a point to another, huge mess
	if relx > 0:
		a = abs(rely/relx)
		if rely > 0:
			if a < 0.41421:
				return 2
			elif a < 2.41421:
				return 1
			else:
				return 0
		else:
			if a < 0.41421:
				return 2
			elif a < 2.41421:
				return 3
			else:
				return 4
	elif relx < 0:
		a = abs(rely/relx)
		if rely > 0:
			if a < 0.41421:
				return 6
			elif a < 2.41421:
				return 7
			else:
				return 0
		else:
			if a < 0.41421:
				return 6
			elif a < 2.41421:
				return 5
			else:
				return 4
	else:
		if rely > 0:
			return 0
		else:
			return 4

class Player(sprite.Sprite): # player sprite
	def __init__(self, *_, pos=(0, 0), path=[]):
		sprite.Sprite.__init__(self)

		self.image = Surface((48, 48)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		self.image.blit(playertexture, (0, 0))
		self.rect = self.image.get_rect()

		self.pos = pos

		self.prevd = 0

		self.speed = 4

		self.path = path

		self.shoot = 0
		self.reloading = False

		self.hp = 2
		self.damage = 0

		self.startdelay = 1.5

	def update(self, delta):
		if self.startdelay>0:
			self.startdelay -= delta
		else:
			if self.path:
				vx = delta*self.speed
				vy = vx*.8
				dx, dy = self.path[0]
				if self.pos[0]<dx:
					self.pos = min(self.pos[0]+vx, dx), self.pos[1]
				elif self.pos[0]>dx:
					self.pos = max(self.pos[0]-vx, dx), self.pos[1]
				elif self.pos[1]<dy:
					self.pos = self.pos[0], min(self.pos[1]+vy, dy)
				elif self.pos[1]>dy:
					self.pos = self.pos[0], max(self.pos[1]-vy, dy)
				else:
					self.path = self.path[1:]
			else:
				nextlevel()

		self.rect.x, self.rect.y = int(self.pos[0]*48), int(56 + self.pos[1]*24)

		mousex, mousey = mouse.get_pos()
		relx, rely = mousex-(self.rect.x+24), mousey-(self.rect.y+48)
		d = direction(relx, rely)
		if d != self.prevd:
			self.prevd = d
			self.image.fill((0, 0, 0, 0))
			self.image.blit(playertexture, (-48*self.prevd, -48 if self.damage else 0))

		if self.startdelay <= 0:
			if self.shoot:
				if self.reloading:
					self.shoot = max(self.shoot-delta, 0)
				elif not mouse.get_pressed()[0]:
					self.reloading = True
			else:
				self.reloading = False
				if mouse.get_pressed()[0] and 60 < mousey < 480:
					self.shoot = .3
					gunchannel.play(sfx['gunshot'])
					self.groups()[0].fire_at(self.rect.x+24, self.rect.y+24, mousex, mousey, self.prevd)

		self.damage = max(self.damage-delta, 0)
		if not (self.hp or self.damage):
			self.kill()
			deathscreen()

		if not self.damage and self.alive():
			for enemy in self.groups()[0].enemies:
				if enemy.alive() and not enemy.damage:
					if sprite.collide_rect(self, enemy):
						self.hit()

	def hit(self):
		self.hp -= 1
		self.damage = .5


class Enemy(sprite.Sprite): # enemy sprite
	def __init__(self, *_, pos=(0, 0)):
		sprite.Sprite.__init__(self)

		self.image = Surface((48, 48)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		self.image.blit(enemytexture, (0, 0))
		self.rect = self.image.get_rect()

		self.pos = pos

		self.looking = 0

		self.target = self.pos

		self.speed = 3

		self.hp = 3
		self.damage = 0

		self.startdelay = 1.5

	def update(self, delta):
		px, py = self.groups()[0].player.pos
		relx, rely = px-self.pos[0], py-self.pos[1]

		if self.startdelay>0:
			self.startdelay -= delta
		else:
			vx = delta*self.speed
			vy = vx*.8
			dx, dy = self.target
			if self.pos[0]<dx:
				self.pos = min(self.pos[0]+vx, dx), self.pos[1]
			elif self.pos[0]>dx:
				self.pos = max(self.pos[0]-vx, dx), self.pos[1]
			elif self.pos[1]<dy:
				self.pos = self.pos[0], min(self.pos[1]+vy, dy)
			elif self.pos[1]>dy:
				self.pos = self.pos[0], max(self.pos[1]-vy, dy)
			else:
				room = self.groups()[0].strmap
				if abs(relx) > abs(rely):
					tx, ty = int(self.target[0]+copysign(1, relx)), int(self.target[1])
					if room[ty][tx] != '0':
						ty = int(self.target[1]+copysign(1, rely))
						if room[tx][ty] != '0':
							ty = int(self.target[1]-copysign(2, rely))
						self.target = int(self.target[0]), ty
					else:
						self.target = tx, ty
				else:
					tx, ty = int(self.target[0]), int(self.target[1]+copysign(1, rely))
					if room[ty][tx] != '0':
						tx = int(self.target[0]+copysign(1, relx))
						if room[tx][ty] != '0':
							tx = int(self.target[0]-copysign(2, relx))
						self.target = tx, int(self.target[1])
					else:
						self.target = tx, ty

		self.rect.x, self.rect.y = int(self.pos[0]*48), int(56 + self.pos[1]*24)

		self.damage = max(self.damage-delta, 0)
		d = direction(relx, rely)
		if d != self.looking:
			self.prevd = d
			self.image.fill((0, 0, 0, 0))
			self.image.blit(enemytexture, (-48*self.prevd, -48 if self.damage else 0))

		if not (self.hp or self.damage):
			self.kill()

	def hit(self):
		self.hp = max(self.hp-1, 0)
		self.damage = .2


class Bullet(sprite.Sprite): # bullets
	def __init__(self, origin, direction, orient):
		sprite.Sprite.__init__(self)

		self.pos, self.d = origin, direction
		self.s = 700

		self.t = 0

		self.image = Surface((9, 9)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		self.image.blit(bullettexture, (-9*orient, 0))

		self.w, self.h = self.image.get_size()

		self.rect = self.image.get_rect()

	def update(self, delta):
		self.rect.x = self.pos[0]-self.w/2
		self.rect.y = self.pos[1]-self.h/2

		self.pos = self.pos[0] + self.d[0]*self.s*delta, self.pos[1] + self.d[1]*self.s*delta

		self.t += self.s*delta

		for enemy in self.groups()[0].enemies:
			if enemy.alive():
				if sprite.collide_rect(self, enemy):
					n = random()
					if n < .1:
						enemieschannel.play(sfx['zombie1'])
					elif n < .3:
						enemieschannel.play(sfx['zombie2'])
					enemy.hit()
					self.kill()

		if self.t > 960:
			self.kill()
		

class Room(sprite.LayeredUpdates): # room scene
	def __init__(self, n, strmap, spawn, path, enemies):
		sprite.LayeredUpdates.__init__(self)
		self.paused = False
		self.neverpaused = []

		self.strmap = strmap.split('\n')[1:]

		lbl = ui.Label(pos=(40, 40), anchor='nw')
		lbl.display("ROOM %d" %(n+1))
		self.add(lbl, layer=50)

		self.pausebtn = ui.Button(pos=(911, 31), anchor='ne', command=pause, width=170)
		self.pausebtn.display("PAUSE")
		self.add(self.pausebtn, layer=50)
		self.neverpaused.append(self.pausebtn)

		self.homebtn = ui.Button(pos=(911, 85), anchor='ne', command=homemenu, width=170)
		self.homebtn.display("HOME")
		self.neverpaused.append(self.homebtn)

		self.room = []

		self.player = Player(pos=spawn, path=path)
		self.add(self.player)

		self.enemies = [Enemy(pos=e) for e in enemies]
		for enemy in self.enemies:
			self.add(enemy)

			
		for j, row in enumerate(self.strmap): # room rendering from string
			y = 60 + j*24

			line = sprite.Sprite()
			line.image = Surface((960, 48)).convert_alpha()
			line.image.fill((0, 0, 0, 0))

			for i, tile in enumerate(row):
				x = i*48

				line.image.blit(roomtexture, (x, 0), area=ui.tilemask.get(tile, (-1, -1, 1, 1)))
		
			line.rect = line.image.get_rect()
			line.rect.x = 0
			line.rect.y = y

			self.room.append(row)
			self.add(line, layer=j)

	def update(self, delta):
		if self.paused:
			for spr in self.neverpaused:
				if spr.alive():
					spr.update(delta)
		else:
			if self.player.alive():
				self.change_layer(self.player, int(self.player.pos[1])+1)
			for enemy in self.enemies:
				if enemy.alive():
					self.change_layer(enemy, int(enemy.pos[1])+int(enemy.target[1]!=enemy.pos[1]))
			sprite.LayeredUpdates.update(self, delta)

	def fire_at(self, sx, sy, tx, ty, o):
		d = sqrt((sx-tx)**2 + (sy-ty)**2)
		bullet = Bullet(origin=(sx, sy), direction=((tx-sx)/d, (ty-sy)/d), orient=o)
		self.add(bullet, layer=30)

progress = 0

def play():
	play_level(progress)

def nextlevel():
	global progress
	progress += 1
	if progress < 3:
		play_level(progress)
	else:
		progress = 0
		complete()

def setupmenus():
	global HomeMenu, DeathScreen, WinScreen, HowTo, Credits

	bg = sprite.Sprite()
	bg.image = Surface((960, 480))
	for j, row in enumerate(bgroom):
		y = j*24
		for i, tile in enumerate(row):
			x = i*48
			bg.image.blit(roomtexture, (x, y), area=ui.tilemask.get(tile, (-1, -1, 1, 1)))
	bg.rect = bg.image.get_rect()
	bg.rect.y = 60

	HomeMenu = sprite.Group()
	HomeMenu.add(bg)
	HomeMenu.add(ui.Label(text="- GET OUT -", pos=(480, 100)))
	HomeMenu.add(ui.Button(text="PLAY", command=play, pos=(480, 240), anchor='s', width=200))
	HomeMenu.add(ui.Button(text="HOW TO", command=showhowto, pos=(480, 300), anchor='c', width=200))
	HomeMenu.add(ui.Button(text="CREDITS", command=showcredits, pos=(480, 360), anchor='n', width=200))

	DeathScreen = sprite.Group()
	img = sprite.Sprite()
	img.image = tombstone
	img.rect = img.image.get_rect()
	img.rect.x = 480 - img.rect.w/2
	img.rect.y = 150
	DeathScreen.add(img)
	DeathScreen.add(ui.Label(text="YOU DIED", pos=(480, 40)))
	DeathScreen.add(ui.Button(text="TRY AGAIN", command=play, pos=(480, 300), anchor='c', width=220))
	DeathScreen.add(ui.Button(text="HOME", command=homemenu, pos=(480, 360), anchor='c', width=220))

	WinScreen = sprite.Group()
	img = sprite.Sprite()
	img.image = outside
	img.rect = img.image.get_rect()
	img.rect.x = 480 - img.rect.w/2
	img.rect.y = 150
	WinScreen.add(img)
	WinScreen.add(ui.Label(text="YOU'RE OUT !", pos=(480, 40)))
	WinScreen.add(ui.Button(text="QUIT", command=close, pos=(480, 300), anchor='c', width=220))
	WinScreen.add(ui.Button(text="HOME", command=homemenu, pos=(480, 360), anchor='c', width=220))

	HowTo = sprite.Group()
	HowTo.add(bg)
	HowTo.add(ui.Button(text="BACK", command=homemenu, pos=(30, 30), anchor='nw'))
	for i, line in enumerate(instructions):
		HowTo.add(ui.Label(text=line, pos=(480, 120+i*36)))

	Credits = sprite.Group()
	Credits.add(bg)
	Credits.add(ui.Button(text="BACK", command=homemenu, pos=(30, 30), anchor='nw'))
	for i, line in enumerate(credits):
		Credits.add(ui.Label(text=line, pos=(480, 120+i*36)))

def loadtextures():
	global roomtexture, playertexture, enemytexture, bullettexture, tombstone, outside
	roomtexture =   ui.scale3x(image.load(ui.get_rsc_path('rooms.png')))
	playertexture = ui.scale3x(image.load(ui.get_rsc_path('player.png')))
	enemytexture =  ui.scale3x(image.load(ui.get_rsc_path('enemy.png')))
	bullettexture = ui.scale3x(image.load(ui.get_rsc_path('bullet.png')))
	tombstone =     ui.scale3x(image.load(ui.get_rsc_path('tombstone.png')))
	outside =       ui.scale3x(image.load(ui.get_rsc_path('outside.png')))

def loadsounds():
	global uichannel, gunchannel, enemieschannel, sfx
	sfx = {}
	gunchannel = mixer.Channel(0)
	gunchannel.set_volume(20)
	uichannel = mixer.Channel(1)
	enemieschannel = mixer.Channel(2)
	enemieschannel.set_volume(50)
	sfx['gunshot'] = mixer.Sound(ui.get_rsc_path('gunshot.wav'))
	sfx['zombie1'] = mixer.Sound(ui.get_rsc_path('zombie1.wav'))
	sfx['zombie2'] = mixer.Sound(ui.get_rsc_path('zombie2.wav'))
	sfx['click']   = mixer.Sound(ui.get_rsc_path('click.wav'))
	ui.setupsound(lambda: uichannel.play(sfx['click']))
	mixer.music.load(ui.get_rsc_path('music.wav'))
	mixer.music.set_volume(20)

def play_level(n):
	global view
	room = Room(n, *levels[n])
	view = room

def pause():
	global view
	if type(view) is Room:
		if view.paused:
			view.paused = False
			view.pausebtn.display("PAUSE")
			view.homebtn.kill()
		else:
			view.paused = True
			view.pausebtn.display("RESUME")
			view.add(view.homebtn, layer=50)

def homemenu():
	global view
	view = HomeMenu

def deathscreen():
	global view
	view = DeathScreen

def complete():
	global view
	view = WinScreen

def showhowto():
	global view
	view = HowTo

def showcredits():
	global view
	view = Credits

def close():
	global running
	running = False
