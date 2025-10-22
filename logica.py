# game_logic.py
import random

class Dino:
    def __init__(self, x=50, ground_y=300):
        self.x = x
        self.y = ground_y
        self.width = 40
        self.height = 60
        self.vel_y = 0
        self.jumping = False
        self.ducking = False
        self.ground = ground_y
        self.jump_force = -15
        self.gravity = 0.8
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vel_y = self.jump_force
            
    def duck(self, ducking):
        self.ducking = ducking
        
    def update(self):
        if self.jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            
            if self.y >= self.ground:
                self.y = self.ground
                self.jumping = False
                self.vel_y = 0
                
    def get_rect(self):
        if self.ducking and not self.jumping:
            return {
                'x': self.x,
                'y': self.y + 30,
                'width': self.width + 20,
                'height': self.height - 30
            }
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    def get_state(self):
        """Retorna el estado completo del dinosaurio para renderizado"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'ducking': self.ducking,
            'jumping': self.jumping
        }


class Obstacle:
    def __init__(self, x, obs_type, speed=8):
        self.x = x
        self.type = obs_type
        self.speed = speed
        
        if obs_type == 'cactus':
            self.width = 20
            self.height = random.choice([40, 50, 60])
            self.y = 300 - self.height  # ground_y - height
        else:  # bird
            self.width = 40
            self.height = 30
            self.y = 300 - random.choice([60, 80, 100])
            
    def update(self):
        self.x -= self.speed
        
    def get_rect(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    def get_state(self):
        """Retorna el estado completo del obstáculo para renderizado"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.type
        }
    
    def off_screen(self):
        return self.x < -50


class Ground:
    def __init__(self, y=360, speed=8):
        self.x = 0
        self.y = y
        self.speed = speed
        self.reset_point = -50
        
    def update(self):
        self.x -= self.speed
        if self.x <= self.reset_point:
            self.x = 0
            
    def get_state(self):
        """Retorna el estado del suelo para renderizado"""
        return {
            'x': self.x,
            'y': self.y
        }


class GameEngine:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.ground_y = height - 100
        
        self.dino = Dino(50, self.ground_y)
        self.ground = Ground(height - 40)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_min = 60
        self.spawn_max = 120
        
    def handle_jump(self):
        if not self.game_over:
            self.dino.jump()
            
    def handle_duck(self, ducking):
        if not self.game_over:
            self.dino.duck(ducking)
            
    def restart(self):
        self.dino = Dino(50, self.ground_y)
        self.ground = Ground(self.height - 40)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        
    def check_collision(self, rect1, rect2):
        """Verifica colisión entre dos rectángulos"""
        return (rect1['x'] < rect2['x'] + rect2['width'] and
                rect1['x'] + rect1['width'] > rect2['x'] and
                rect1['y'] < rect2['y'] + rect2['height'] and
                rect1['y'] + rect1['height'] > rect2['y'])
        
    def update(self):
        if self.game_over:
            return
            
        # Actualizar dinosaurio
        self.dino.update()
        
        # Actualizar suelo
        self.ground.update()
        
        # Generar obstáculos
        self.spawn_timer += 1
        if self.spawn_timer > random.randint(self.spawn_min, self.spawn_max):
            obs_type = random.choice(['cactus', 'cactus', 'cactus', 'bird'])
            self.obstacles.append(Obstacle(self.width, obs_type))
            self.spawn_timer = 0
            
        # Actualizar obstáculos
        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen():
                self.obstacles.remove(obs)
                self.score += 1
                
            # Verificar colisión
            if self.check_collision(self.dino.get_rect(), obs.get_rect()):
                self.game_over = True
                
    def get_game_state(self):
        """Retorna el estado completo del juego para renderizado"""
        return {
            'dino': self.dino.get_state(),
            'ground': self.ground.get_state(),
            'obstacles': [obs.get_state() for obs in self.obstacles],
            'score': self.score,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }