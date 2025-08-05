import pygame
import math

from pygame.math import Vector2
from random import choice, randrange, uniform
from fontcontroller import FontController
from rendertext import RenderText

class Asteriod:
	def __init__(self,winx,winy,velocityx,velocityy,rad):
		self.x = randrange(0,winx)
		self.y = randrange(0,winy)
		self.winx = winx
		self.winy = winy
		self.velocityx = velocityx
		self.velocityy = velocityy
		self.rad = rad

	def colliding(self, shipx, shipy, rad):
		return math.hypot((shipx - self.x),(shipy - self.y)) <= rad + self.rad

	def update(self):
		self.x += self.velocityx
		self.y += self.velocityy

		self.x,self.y = wrap_position(self.winx, self.winy, self.x, self.y, self.rad)

	def render(self, surface):
		pygame.draw.circle(surface, "white", (self.x, self.y), self.rad, 1)

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
		self.friction_constant = 0.02 # how much speed the ship looses
		self.angle = 0 # updated globally
		self.vec = (math.cos(self.angle), math.sin(self.angle) * -1)
		self.width = winx // 20
		self.height = winy // 25
		self.line_length = 10 # used for the destroyed ship
		self.bullets = []
		self.image = pygame.image.load('ship.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.width, self.height))
		self.fire_images = []
		self.firing = False

		# Load the images for the moving ship with thrusters
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
		# sin should be 'atan2' equivalent
		self.vec = (math.cos(angle), math.sin(angle) * -1)
		self.velocity.x += self.vec[0]
		self.velocity.y += self.vec[1]

		self.firing = True

	def update(self, velocity_threshold=0.05):
		self.position.x += self.velocity.x
		self.position.y += self.velocity.y

		# Slow down the ship.
		# Gradually make the ship's x and y velocities approach '0'
		# Use a friction/mass constant/heuristic to simulate the force acting on/against the ship.
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

		# Checks to make the ship move to the other side of the screen
		self.position.x,self.position.y = wrap_position(self.winx, self.winy, self.position.x, self.position.y)

		# Update the bullets
		bcpy = []
		for bullet in self.bullets:
			bullet.update()
			# If the bullet goes out of bounds, exclude it from the next set of bullets
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

def spawn_asteroids(winx,winy,level):
	amount = randrange(level * 2, level * 4)
	radii = [10,20,30,40,50]
	asteroids = []
	for i in range(amount):
		velocityx = uniform(-1.0,1.0)
		velocityy = uniform(-1.0,1.0)
		rad = choice(radii)
		asteroids.append(Asteriod(winx, winy, velocityx, velocityy, rad))
	return asteroids

def wrap_position(winx, winy, xpos, ypos, rad=1):
	# Checks to make the ship move to the other side of the screen
	if xpos < -rad:
		xpos = winx + rad

	if xpos > winx + rad:
		xpos = -rad

	if ypos < -rad:
		ypos = winy + rad

	if ypos > winy + rad:
		ypos = -rad

	return [xpos, ypos]

def show_main_menu(font_controller,winx,winy,screen,clock):
	asteroids = spawn_asteroids(winx,winy,2)

	hx = winx//2
	hy = winy//2

	playtext = RenderText(font_controller, "grey", "black")
	playtext.update_x(hx)
	playtext.update_y(hy)
	playtext.update_text("Play")

	rx,ry,rw,rh = playtext.get_render_rect()

	playpos_x = hx - rw // 2
	playpos_y = hy - rh // 2

	gamename = RenderText(font_controller, "white", "black")
	gamename.update_x(hx)
	gamename.update_y(hy - winy//6)
	gamename.update_text("Pysteroids")

	collide = False
	leftpress = False
	while True:
		clock.tick(60)

		if collide and leftpress:
			break

		for ast in asteroids:
			ast.update()

		mx,my = pygame.mouse.get_pos()
		leftpress,midpress,rightpress = pygame.mouse.get_pressed()

		collide_x = mx >= playpos_x and mx <= playpos_x + rw
		collide_y = my >= playpos_y and my <= playpos_y + rh
		collide = collide_x and collide_y

		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				return True
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_ESCAPE:
					return True

		screen.fill("black")

		for ast in asteroids:
			ast.render(screen)

		gamename.draw(screen)
		playtext.draw(screen,collide)

		pygame.display.flip()

	return False

def main(winx=600,winy=600):
	pygame.display.init()
	screen = pygame.display.set_mode((winx,winy))

	font_controller = FontController()

	clock = pygame.time.Clock()
	ship = Ship(winx,winy)
	shiprad = (ship.width + ship.height) // 2
	shiprad = shiprad * 0.75
	rotate_velocity = 15
	angle = 0

	death_segments = []
	level = 1
	lives = 3
	game_over = False
	level_timeout = 50
	ctimeout = 0
	score = 0
	radii = [10,20,30,40,50]
	max_rad = radii[-1]
	life_icons = []
	game_events = [False,False]

	menu_res = show_main_menu(font_controller,winx,winy,screen,clock)
	done = menu_res

	for i in range(lives):
		img = pygame.image.load('ship.png').convert_alpha()
		img = pygame.transform.scale(img, (30, 20))
		life_icons.append(img)

	asteroids = spawn_asteroids(winx,winy,level)

	while not done:
		tick = clock.tick(60)
		#print(f"tick {tick}")

		if any(game_events):
			ctimeout += tick / 100

		if ctimeout >= level_timeout:
			ctimeout = 0
			
			if game_over:
				done = True
				break

			# Process a level change
			if game_events[1]:
				game_events[1] = False
				level += 1
				asteroids = spawn_asteroids(winx,winy,level)
				ast_collide = True
				# While there is an asteroid 'spawn camping' the player's ship, re-spawn asteroids
				while ast_collide:
					ast_collide = False
					for ast in asteroids:
						if ast.colliding(ship.position.x, ship.position.y, shiprad):
							ast_collide = True
							break
					if ast_collide:
						asteroids = spawn_asteroids(winx,winy,level)

			# Process a death change
			if game_events[0]:
				if lives < 1:
					print("Game Over.")
					level_timeout = level_timeout * 2
					game_over = True
					asteroids = spawn_asteroids(winx,winy,level)
					life_icons = []
				else:
					game_events[0] = False
					ship = Ship(winx,winy)
					death_segments = []
					life_icons = life_icons[:-1]

		if not game_over:
			ship.angle = angle
			ship.update()

		# Render the bits of the destroyed ship
		for seg in death_segments:
			seg[0][0] += uniform(-1.0,1.0)
			seg[0][1] += uniform(-1.0,1.0)
			seg[1][0] += uniform(-1.0,1.0)
			seg[1][1] += uniform(-1.0,1.0)

		nasteroids = [ast for ast in asteroids]
		for ast in asteroids:
			ast.update()

			if game_over:
				continue

			# Ship collides with Asteriod
			if ast.colliding(ship.position.x, ship.position.y, shiprad) and not game_events[0]:
				game_events[0] = True
				# Render the destroyed ship segments
				for i in range(3):
					endx = ship.position.x + ship.vec[0] * ship.line_length
					endy = ship.position.y + ship.vec[1] * ship.line_length
					start = [ship.position.x, ship.position.y]
					end = [endx, endy]
					death_segments.append([start,end])
				lives -= 1

			for bullet in ship.bullets:
				# If we did not shoot this asteroid, continue including it in the level
				if ast.colliding(bullet.x, bullet.y, 1):
					nasteroids.remove(ast)
					ship.bullets.remove(bullet)
					# If we can split the asteroid into two parts, do so
					# Only do this if the radius of the current asteroid is large enough
					if ast.rad > radii[0]:
						for i in range(2):
							new_rad = radii[radii.index(ast.rad) - 1]
							new_x_velocity = 2 * abs(ast.velocityx) * uniform(-1.0,1.0)
							new_y_velocity = 2 * abs(ast.velocityy) * uniform(-1.0,1.0)
							nast = Asteriod(winx, winy, new_x_velocity, new_y_velocity, new_rad)
							nast.x = ast.x
							nast.y = ast.y
							nasteroids.append(nast)
					score += max(1,max_rad - ast.rad)
					break

		asteroids = nasteroids

		# Player killed all of the asteroids.
		if len(asteroids) == 0:
			game_events[1] = True

		# Process user input
		events = pygame.event.get()
		for e in events:
			if game_over:
				break
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

		# Render the score
		scoretext = RenderText(font_controller, "white", "black")
		scoretext.update_x(50)
		scoretext.update_y(10)
		scoretext.update_text(str(f"Score: {score}"))
		scoretext.draw(screen)

		# Render the life icons
		icx = 30
		for icon in life_icons:
			rot = pygame.transform.rotate(icon, 90)
			rect = rot.get_rect(center=(icx, 50))
			screen.blit(rot, rect)
			icx += 50

		if not game_over:
			if game_events[0]:
				for seg in death_segments:
					start,end = seg
					pygame.draw.line(screen, "white", start, end, 3)
			else:
				ship.render(screen)
		else:
			rendertext = RenderText(font_controller, "white", "black")
			rendertext.update_x(winx//2)
			rendertext.update_y(winy//2)
			rendertext.update_text(str("Game Over."))
			rendertext.draw(screen)
		for ast in asteroids:
			ast.render(screen)
		# renders ship bounding circle
		#pygame.draw.circle(screen, "white", (ship.position.x, ship.position.y), shiprad, 1)
		pygame.display.flip()

	pygame.display.quit()

if __name__ == "__main__":
	main()

