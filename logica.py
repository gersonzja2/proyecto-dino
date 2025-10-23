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
    def __init__(self, x, obs_type, ground_y, speed=8):
        self.x = x
        self.type = obs_type
        self.speed = speed
        
        if 'cactus' in obs_type:
            self.width = 20
            if obs_type == 'cactus_small':
                self.height = 40
            elif obs_type == 'cactus_large':
                self.height = 60
            elif obs_type == 'cactus_group':
                # Este será un grupo de cactus, el hitbox principal
                self.width = 45 
                self.height = 40
            self.y = ground_y + 60 - self.height # 60 es la altura del dino
        else:  # bird
            self.width = 40
            self.height = 30
            self.y = ground_y - random.choice([0, 20, 40]) # Varias alturas para el pájaro
            
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


class Cloud:
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = random.randint(40, 80)
        self.height = random.randint(15, 30)

    def update(self):
        self.x -= self.speed

    def get_state(self):
        """Retorna el estado de la nube para renderizado"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    def off_screen(self):
        return self.x < -self.width


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
    def __init__(self, width=800, height=400, sounds=None):
        self.width = width
        self.height = height
        self.ground_y = height - 100
        self.speed = 8
        self.speed_increase_interval = 10 # Aumentar velocidad cada 10 puntos
        self.next_speed_increase_score = self.speed_increase_interval
        
        self.sounds = sounds if sounds is not None else {}
        
        self.dino = Dino(50, self.ground_y)
        self.ground = Ground(height - 40, speed=self.speed)
        self.obstacles = []
        self.clouds = []
        self.score = 0
        self.game_over = False
        
        self.spawn_timer = 0
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = random.randint(120, 240)
        self.spawn_interval = random.randint(60, 120)
        
    def handle_jump(self):
        if not self.game_over:
            if self.sounds.get('jump') and not self.dino.jumping:
                self.sounds['jump'].play()
            self.dino.jump()
            
    def handle_duck(self, ducking):
        if not self.game_over:
            self.dino.duck(ducking)
            
    def restart(self):
        """Reinicia el estado del juego."""
        new_game = GameEngine(self.width, self.height, self.sounds)
        self.dino = new_game.dino
        self.ground = new_game.ground
        self.obstacles = new_game.obstacles
        self.clouds = new_game.clouds
        self.score = new_game.score
        self.game_over = new_game.game_over
        
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
        
        # Generar nubes
        self.cloud_spawn_timer += 1
        if self.cloud_spawn_timer > self.cloud_spawn_interval:
            cloud_y = random.randint(50, 150)
            self.clouds.append(Cloud(self.width, cloud_y))
            self.cloud_spawn_timer = 0
            self.cloud_spawn_interval = random.randint(120, 300)

        # Actualizar nubes
        for cloud in self.clouds[:]:
            cloud.update()
            if cloud.off_screen():
                self.clouds.remove(cloud)

        # Generar obstáculos
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_interval:
            obs_type = random.choice(['cactus_small', 'cactus_large', 'cactus_group', 'bird'])
            self.obstacles.append(Obstacle(self.width, obs_type, self.ground_y, speed=self.speed))
            self.spawn_timer = 0
            self.spawn_interval = random.randint(60, 120)
            
        # Actualizar obstáculos
        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen():
                self.obstacles.remove(obs)
                if not self.game_over:
                    self.score += 1
                    if self.sounds.get('point'):
                        self.sounds['point'].play()

                    # Aumentar velocidad
                    if self.score >= self.next_speed_increase_score:
                        self.speed += 0.5
                        self.ground.speed = self.speed
                        self.next_speed_increase_score += self.speed_increase_interval
                
            # Verificar colisión
            if self.check_collision(self.dino.get_rect(), obs.get_rect()):
                self.game_over = True
                if self.sounds.get('die'):
                    self.sounds['die'].play()
                
    def get_game_state(self):
        """Retorna el estado completo del juego para renderizado"""
        return {
            'dino': self.dino.get_state(),
            'ground': self.ground.get_state(),
            'obstacles': [obs.get_state() for obs in self.obstacles],
            'clouds': [cloud.get_state() for cloud in self.clouds],
            'score': self.score,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }