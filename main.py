import pygame
import math

from pygame.math import Vector2
from random import choice

class Bullet:
	def __init__(self,x,y,angle):
		self.x = x
		self.y = y
		self.velocity = 8
		self.angle = math.radians(angle)
		self.vec = (math.cos(self.angle), math.sin(self.angle))
		self.line_length = 10

	def out_of_bounds(self, winx, winy):
		oob_x = self.x <= 0 or self.x >= winx
		oob_y = self.y <= 0 or self.y >= winy
		return oob_x or oob_y

	def update(self):
		self.x += self.vec[0] * self.velocity
		self.y += self.vec[1] * self.velocity

	def render(self,surface):
		start = (self.x, self.y)
		end = (self.x + self.vec[0] * self.line_length, self.y + self.vec[1] * self.line_length)
		pygame.draw.line(surface, "white", start, end, 3)

class Ship:
	def __init__(self,winx,winy):
		self.winx = winx
		self.winy = winy
		self.position = Vector2(winx//2,winy//2)
		self.velocity = Vector2(0,0)
		self.friction_constant = 0.025 # how much speed the ship looses
		self.angle = 0 # updated globally
		self.width = winx // 20
		self.height = winy // 25
		self.bullets = []
		self.image = pygame.image.load('ship.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.width, self.height))
		self.fire_images = []
		self.firing = False

		for itm in ['ship_flame1.png','ship_flame2.png']:
			img = pygame.image.load(itm).convert_alpha()
			img = pygame.transform.scale(img, (self.width, self.height))
			self.fire_images.append(img)

	def fire(self):
		# only support one bullet for now
		if len(self.bullets) > 0:
			return

		# Correct issue with angle being 'mirrored' for bullets
		angle = 360 - self.angle
		#print("angle",self.angle)
		self.bullets.append(Bullet(self.position.x, self.position.y, angle))

	def move(self):
		angle = math.radians(self.angle)
		vec = (math.cos(angle), math.sin(angle) * -1)
		#print(f"vec {vec}")
		self.velocity.x += vec[0]
		self.velocity.y += vec[1]

		self.firing = True

	def update(self, velocity_threshold=0.05):
		self.position.x += self.velocity.x
		self.position.y += self.velocity.y

		#print("self.velocity.x",self.velocity.x)
		#print("self.velocity.y",self.velocity.y)

		if abs(self.velocity.x) >= velocity_threshold:
			if self.velocity.x < 0:
				self.velocity.x += self.friction_constant
			else:
				self.velocity.x -= self.friction_constant

		if abs(self.velocity.y) >= velocity_threshold:
			if self.velocity.y < 0:
				self.velocity.y += self.friction_constant
			else:
				self.velocity.y -= self.friction_constant

		if self.position.x < 0:
			self.position.x = self.winx + self.position.x

		if self.position.x > self.winx:
			self.position.x = self.position.x - self.winx

		if self.position.y < 0:
			self.position.y = self.winy + self.position.y

		if self.position.y > self.winy:
			self.position.y = self.position.y - self.winy

		bcpy = []
		for bullet in self.bullets:
			bullet.update()
			if not bullet.out_of_bounds(self.winx, self.winy):
				bcpy.append(bullet)
		self.bullets = bcpy

	def render(self,surface):
		chosen_img = choice(self.fire_images) if self.firing else self.image
		rot = pygame.transform.rotate(chosen_img, self.angle)
		rect = rot.get_rect(center=(self.position.x, self.position.y))
		surface.blit(rot, rect)

		for bullet in self.bullets:
			bullet.render(surface)

		self.firing = False

def main(winx=600,winy=600):
	pygame.display.init()
	screen = pygame.display.set_mode((winx,winy))

	clock = pygame.time.Clock()
	ship = Ship(winx,winy)
	rotate_velocity = 10
	angle = 0

	done = False
	while not done:
		clock.tick(60)

		ship.angle = angle
		ship.update()

		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				done = True
				break
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_SPACE:
					ship.fire()
				elif e.key == pygame.K_UP:
					ship.move()
				elif e.key == pygame.K_LEFT:
					angle += rotate_velocity
				elif e.key == pygame.K_RIGHT:
					angle -= rotate_velocity
				elif e.key == pygame.K_ESCAPE:
					done = True
					break

		screen.fill("black")
		ship.render(screen)
		pygame.display.flip()

	pygame.display.quit()

if __name__ == "__main__":
	main()
