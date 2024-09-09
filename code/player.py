from settings import * 

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, collision_sprites):
		super().__init__(groups)
		self.image = pygame.Surface((48,56))
		self.image.fill('red')
  
		# rect
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()

		# movement 
		self.direction = vector()
		self.speed = 200
		self.gravity = 1300
  
		# collision
		self.collision_sprites = collision_sprites

	def input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector()
		if keys[pygame.K_RIGHT]:
			input_vector.x += 1
		if keys[pygame.K_LEFT]:
			input_vector.x -= 1
   
		self.direction.x = input_vector.normalize().x if input_vector else 0

	def move(self, dt):
		# horizontal
		self.rect.x += self.direction.x * self.speed * dt
		self.collision('horizontal')
  
		# vertical
		self.direction.y += self.gravity/2 * dt
		self.rect.y += self.direction.y * dt
		self.direction.y += self.gravity/2 * dt
		self.collision('vertical')
  
	def collision(self, axis):
		for sprite in self.collision_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if axis == 'horizontal':
					if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right: # moving left
						self.rect.left = sprite.rect.right
					elif self.rect.right <= sprite.rect.left and self.old_rect.right >= sprite.old_rect.left: # moving right
						self.rect.right = sprite.rect.left

				elif axis == 'vertical':
					if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom: # moving up
						self.rect.top = sprite.rect.bottom
					elif self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top: # moving down
						self.rect.bottom = sprite.rect.top
					self.direction.y = 0

	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.input()
		self.move(dt)
