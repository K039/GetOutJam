from pygame import *
from ui import get_rsc_path

mixer.pre_init(channels=3)
init()

display.set_caption("Get Out - GMTK GameJam 2020")

icon = image.load(get_rsc_path('x32.png'))
logo = image.load(get_rsc_path('logosmall.png'))

window = display.set_mode((520, 300), NOFRAME)
window.blit(logo, (20, 30))
display.flip()

import game

game.loadtextures()
game.loadsounds()
game.setupmenus()

lastframe = 0
playingmusic = False
clock = time.Clock()
time.delay(2000)
window = display.set_mode((960, 600))
display.set_icon(icon)

game.homemenu()

while game.running:
	if not playingmusic:
		if time.get_ticks()>10000:
			playingmusic = True
			mixer.music.play(-1)
	for ev in event.get():
		if ev.type == QUIT:
			game.running = False

	now = time.get_ticks()
	game.view.update((now-lastframe)/1000)
	lastframe = now

	window.fill((0, 0, 0))

	game.view.draw(window)

	display.flip()
	clock.tick(60)

quit()