from settings import * 
from timer import Timer # type: ignore
from os.path import join

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites, semi_collision_sprites):
		super().__init__(groups)
		self.image = pygame.image.load(join("..", "graphics","player","idle","0.png")).convert_alpha()
  
		# rect
		self.rect = self.image.get_frect(topleft = pos)
		self.hitbox_rect = self.rect.inflate(-76,-36)
		self.old_rect = self.hitbox_rect.copy()

		# movement 
		self.direction = vector()
		self.speed = 200
		self.gravity = 1300
		self.jump = False
		self.jump_height = 900
  
		# collision
		self.collision_sprites = collision_sprites
		self.semi_collision_sprites = semi_collision_sprites
		self.on_surface = {'floor': False, 'left': False, 'right': False}
		self.platform = None
  
		# timers
		self.timers = {
			'wall jump': Timer(200),
			'wall slide block': Timer(250),
			'platform skip': Timer(300)
		}

	def input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector()
		if not self.timers['wall jump'].active:
			if keys[pygame.K_RIGHT]:
				input_vector.x += 1
			if keys[pygame.K_LEFT]:
				input_vector.x -= 1
			if keys[pygame.K_DOWN]:
				self.timers['platform skip'].activate()

			self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
  
		if keys[pygame.K_SPACE]:
			self.jump = True
			self.timers['wall jump'].activate()
   


	def move(self, dt):
		# horizontal
		self.hitbox_rect.x += self.direction.x * self.speed * dt
		self.collision('horizontal')
  
		# vertical
		if not self.on_surface['floor'] and any((self.on_surface['left'],self.on_surface['right'])) and not self.timers['wall slide block'].active:
			self.direction.y = 0
			self.rect.y += self.gravity/10 * dt
		else:
			self.direction.y += self.gravity/2 * dt
			self.hitbox_rect.y += self.direction.y * dt
			self.direction.y += self.gravity/2 * dt

		if self.jump:
			if self.on_surface['floor']:
				self.direction.y = -self.jump_height
				self.timers['wall slide block'].activate()
				# fixed: player stand on moving platforms but can not jump
				self.hitbox_rect.bottom -= 1
			elif any((self.on_surface['right'], self.on_surface['left'])) and not self.timers['wall slide block'].active:
				self.timers['wall jump'].activate()
				self.direction.y = -self.jump_height
				self.direction.x = 1 if self.on_surface['left'] else -1
			self.jump = False
   
		self.collision('vertical')
		self.semi_collision()
		self.rect.center = self.hitbox_rect.center
  
	def platform_move(self, dt):
		if self.platform:
			self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt 

	def check_contact(self):
		floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,2))
		right_rect = pygame.Rect((self.hitbox_rect.topright + vector(2,self.hitbox_rect.height/4)),(2,self.hitbox_rect.height/2))
		left_rect = pygame.Rect((self.hitbox_rect.topleft + vector(-2,self.hitbox_rect.height/4)), (2, self.hitbox_rect.height/2))
		collide_rects = [sprite.rect for sprite in self.collision_sprites]
		semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]
  
		# collisions
		self.on_surface['floor'] = floor_rect.collidelist(collide_rects) >= 0 or (floor_rect.collidelist(semi_collide_rects) >= 0 and self.direction.y >= 0)
		self.on_surface['right'] = right_rect.collidelist(collide_rects) >= 0
		self.on_surface['left'] = left_rect.collidelist(collide_rects) >= 0
  
		self.platform = None
		sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
		for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
			if sprite.rect.colliderect(floor_rect):
				self.platform = sprite
  
	def collision(self, axis):
		for sprite in self.collision_sprites.sprites():
			if sprite.rect.colliderect(self.hitbox_rect):
				if axis == 'horizontal':
					if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right): # moving left
						self.hitbox_rect.left = sprite.rect.right
					elif self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left): # moving right
						self.hitbox_rect.right = sprite.rect.left

				elif axis == 'vertical':
					if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom): # moving up
						self.hitbox_rect.top = sprite.rect.bottom
						if hasattr(sprite, 'moving'):
							self.hitbox_rect.top += 6
					elif self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top): # moving down
						self.hitbox_rect.bottom = sprite.rect.top
					self.direction.y = 0

	def semi_collision(self):
		if not self.timers['platform skip'].active:
			for sprite in self.semi_collision_sprites:
				if sprite.rect.colliderect(self.hitbox_rect):
					if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:
							self.hitbox_rect.bottom = sprite.rect.top
							if self.direction.y > 0:
								self.direction.y = 0

	def update_timers(self):
		for timer in self.timers.values():
			timer.update()

	def update(self, dt):
		self.old_rect = self.hitbox_rect.copy()
		self.update_timers()
		self.input()
		self.move(dt)
		self.platform_move(dt)
		self.check_contact()