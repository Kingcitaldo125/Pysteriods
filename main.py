import pygame
import math

from pygame.math import Vector2
from os.path import join

class Bullet:
	def __init__(self,x,y,angle):
		self.x = x
		self.y = y
		self.velocity = 10
		self.angle = angle
		self.vec = Vector2(math.cos(self.angle),math.sin(self.angle))
		self.line_length = 10

	def out_of_bounds(self, winx, winy):
		oob_x = self.x <= 0 or self.x >= winx
		oob_y = self.y <= 0 or self.y >= winy
		return oob_x or oob_y

	def update(self):
		self.x += self.vec.x * self.velocity
		self.y += self.vec.y * self.velocity

	def render(self,surface):
		start = (self.x,self.y)
		end = (self.x + self.line_length, self.y + self.line_length)
		pygame.draw.line(surface, "white", start, end)

class Ship:
	def __init__(self,winx,winy):
		self.position = Vector2(winx//2,winy//2)
		self.velocity = Vector2(0,0)
		self.friction_constant = 0.5 # how much speed the ship looses
		self.angle = math.pi / 2
		self.width = winx // 25
		self.height = winy // 20
		self.bullets = []
		self.image = pygame.image.load('ship.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.width, self.height))

	def fire(self):
		# only support one bullet for now
		if len(self.bullets) > 0:
			return

		self.bullets.append(Bullet(self.position.x, self.position.y, self.angle))

	def update(self,winx,winy):
		self.position.x += self.velocity.x
		self.position.y += self.velocity.y

		self.velocity.x = max(0,self.velocity.x - self.friction_constant)
		self.velocity.y = max(0,self.velocity.y - self.friction_constant)

		for bullet in self.bullets:
			bullet.update()

	def render(self,surface):
		rot = pygame.transform.rotate(self.image, self.angle)
		rect = rot.get_rect(center=(self.position.x, self.position.y))
		surface.blit(rot, rect)

		for bullet in self.bullets:
			bullet.render(surface)

def main(winx=600,winy=600):
	pygame.display.init()
	screen = pygame.display.set_mode((winx,winy))

	clock = pygame.time.Clock()
	ship = Ship(winx,winy)
	angle = 0

	done = False
	while not done:
		clock.tick(60)
		
		angle -= 1
		if angle < 0:
			angle = 359
		angle = angle % 360
		ship.angle = angle

		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				done = True
				break
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_SPACE:
					ship.fire()
				elif e.key == pygame.K_LEFT:
					ship.rotate(-1)
				elif e.key == pygame.K_RIGHT:
					ship.rotate(1)
				elif e.key == pygame.K_ESCAPE:
					done = True
					break

		screen.fill("black")
		ship.render(screen)
		pygame.display.flip()
	pygame.display.quit()

if __name__ == "__main__":
	main()
