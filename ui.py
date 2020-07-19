from pygame import *
import os, sys

def get_rsc_path(name):
	return os.path.join(os.path.dirname(__file__), 'resources/'+name)

def setupsound(f):
	global playsfx
	playsfx = f

class Grid:
	def __init__(self, w, h, c):
		self.w, self.h, self.c = w, h, c

	def get(self, t, default=None):
		try:
			i = int(t, base=36)
			return (self.w*(i%self.c), self.h*(i//self.c), self.w, self.h)
		except:
			return default

def scale3x(surface):
	w, h = surface.get_size()
	return transform.scale(surface, (w*3, h*3))


tilemask = Grid(48, 48, 4)

font = scale3x(image.load(get_rsc_path("font.png")))
btnbg = scale3x(image.load(get_rsc_path("button.png")))

anchors = {
	'n' : (.5,  0),
	'w' : ( 1, .5),
	's' : (.5,  1),
	'e' : ( 0, .5),
	'c' : (.5, .5),
	'nw': ( 0,  0),
	'ne': ( 1,  0),
	'sw': ( 1,  1),
	'se': ( 0,  1),
}

charset = {
	'0': (0, 0), '1': (1, 0), '2': (2, 0), '3': (3, 0), '4': (4, 0),
	'5': (5, 0), '6': (6, 0), '7': (7, 0), '8': (8, 0), '9': (9, 0),
	'A': (0, 1), 'B': (1, 1), 'C': (2, 1), 'D': (3, 1), 'E': (4, 1),
	'F': (5, 1), 'G': (6, 1), 'H': (7, 1), 'I': (8, 1), 'J': (9, 1),
	'K': (0, 2), 'L': (1, 2), 'M': (2, 2), 'N': (3, 2), 'O': (4, 2),
	'P': (5, 2), 'Q': (6, 2), 'R': (7, 2), 'S': (8, 2), 'T': (9, 2),
	'U': (0, 3), 'V': (1, 3), 'W': (2, 3), 'X': (3, 3), 'Y': (4, 3),
	'Z': (5, 3), '-': (6, 3), '.': (7, 3), ',': (8, 3), "'": (9, 3),
	'!': (0, 4), '?': (1, 4), '(': (2, 4), ')': (3, 4), ":": (4, 4),
}

class Label(sprite.Sprite):
	def __init__(self, *_, pos=(0, 0), anchor='n', text=None):
		sprite.Sprite.__init__(self)
		
		self.image = Surface((1, 1)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		
		self.anchor = anchors.get(anchor, (.5, 0))
		self.pos = pos
		
		self.rect = self.image.get_rect()

		if text:
			self.display(text)
	
	def display(self, text):
		text = text.replace('\n', '\\n').replace('\t', '  ').upper()
		
		w = len(text)*21
		
		self.image = Surface((w, 30)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		
		for i, char in enumerate(text):
			x = i*21
			j, k = charset.get(char, (-1, 0))
			self.image.blit(font, (x, 0), area=(j*21, k*30, 21, 30))
		
		self.rect = self.image.get_rect()
		self.rect.x = self.pos[0] - self.anchor[0]*w
		self.rect.y = self.pos[1] - self.anchor[1]*15

class Button(sprite.Sprite):
	def __init__(self, *_, pos=(0, 0), anchor='n', command=lambda: None, width=0, text=None):
		sprite.Sprite.__init__(self)
		
		self.image = Surface((1, 1)).convert_alpha()
		self.image.fill((0, 0, 0, 0))
		
		self.anchor = anchors.get(anchor, (.5, 0))
		self.pos = pos
		
		self.rect = self.image.get_rect()
		self.maxw = width

		self.command = command

		self.pressed = False

		if text:
			self.display(text)
	
	def display(self, text):
		text = text.replace('\n', '\\n').replace('\t', '  ').upper()
		
		self.minw = len(text)*21
		
		self.label = Surface((self.minw, 30)).convert_alpha()
		self.label.fill((0, 0, 0, 0))
		
		for i, char in enumerate(text):
			x = i*21
			j, k = charset.get(char, (-1, 0))
			self.label.blit(font, (x, 0), area=(j*21, k*30, 21, 30))
		self.render()

	def render(self):
		w = max(self.maxw, self.minw+18)

		self.image = Surface((w, 48)).convert_alpha()
		self.image.fill((0, 0, 0, 0))

		off = 48 if self.pressed else 0

		self.image.blit(btnbg, (0, 0), area=(off, 0, 12, 48))
		for i in range((w-24)//24):
			x = 12 + i*24
			self.image.blit(btnbg, (x, 0), area=(off+12, 0, 24, 48))
		self.image.blit(btnbg, (x+24, 0), area=(off+12, 0, (w-24)%24, 48))
		self.image.blit(btnbg, (w-12, 0), area=(off+36, 0, 12, 48))

		self.image.blit(self.label, (w/2 - self.minw/2, 9))
		
		self.rect = self.image.get_rect()
		self.rect.x = self.pos[0] - self.anchor[0]*w
		self.rect.y = self.pos[1] - self.anchor[1]*24

	def update(self, delta):
		x, y = mouse.get_pos()
		if 0 < x-self.rect.x < self.rect.w and 0 < y-self.rect.y < self.rect.h:
			if mouse.get_pressed()[0]:
				if not self.pressed:
					playsfx()
					self.pressed = True
					self.render()
			else:
				if self.pressed:
					self.pressed = False
					self.render()
					self.command()