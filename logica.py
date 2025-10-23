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
        self.anim_timer = 0
        self.anim_frame = 0
        
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
        
        # Animación de carrera
        if not self.jumping and not self.ducking:
            self.anim_timer += 1
            if self.anim_timer > 6: # Cambiar de frame cada 6 ticks
                self.anim_frame = (self.anim_frame + 1) % 2
                self.anim_timer = 0
                
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
            'jumping': self.jumping,
            'anim_frame': self.anim_frame
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
        elif obs_type == 'bird':
            self.width = 40
            self.height = 30
            self.y = ground_y - random.choice([0, 20, 40]) # Varias alturas para el pájaro
            self.anim_timer = 0
            self.anim_frame = 0
        else:  # pterodactyl
            self.width = 45
            self.height = 25
            self.y = ground_y - random.choice([50, 70]) # Vuela más alto que el pájaro
            self.anim_timer = 0
            self.anim_frame = 0
            
    def update(self):
        self.x -= self.speed
        if self.type in ['bird', 'pterodactyl']:
            self.anim_timer += 1
            if self.anim_timer > 10: # Cambiar de frame cada 10 ticks
                self.anim_frame = (self.anim_frame + 1) % 2
                self.anim_timer = 0
        
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
            'type': self.type,
            # Añadir anim_frame solo si es un pájaro
            'anim_frame': self.anim_frame if self.type in ['bird', 'pterodactyl'] else 0
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
        self.high_score = 0
        self.highscore_file = "highscore.txt"
        self.speed_increase_interval = 10 # Aumentar velocidad cada 10 puntos
        self.next_speed_increase_score = self.speed_increase_interval
        
        self.sounds = sounds if sounds is not None else {}
        
        self.dino = Dino(50, self.ground_y)
        self.ground = Ground(height - 40, speed=self.speed)
        self.obstacles = []
        self.clouds = []
        self.score = 0
        self.game_over = False
        self.paused = False
        self.new_high_score_achieved = False

        # Ciclo día-noche
        self.time_of_day = 0
        self.cycle_duration = 4800 # 80 segundos a 60 FPS

        self.load_high_score()
        
        self.spawn_timer = 0
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = random.randint(120, 240)
        self.spawn_interval = random.randint(60, 120)

    def load_high_score(self):
        """Carga la puntuación más alta desde un archivo."""
        try:
            with open(self.highscore_file, 'r') as f:
                self.high_score = int(f.read())
        except (FileNotFoundError, ValueError):
            self.high_score = 0

    def save_high_score(self):
        """Guarda la puntuación más alta en un archivo."""
        with open(self.highscore_file, 'w') as f:
            f.write(str(self.high_score))
        
    def toggle_pause(self):
        """Activa o desactiva la pausa del juego."""
        if not self.game_over:
            self.paused = not self.paused

    def handle_jump(self):
        if not self.game_over and not self.paused:
            if self.sounds.get('jump') and not self.dino.jumping:
                self.sounds['jump'].play()
            self.dino.jump()
            
    def handle_duck(self, ducking):
        if not self.game_over and not self.paused:
            self.dino.duck(ducking)
            
    def restart(self):
        """Reinicia el estado del juego."""
        new_game = GameEngine(self.width, self.height, self.sounds)
        new_game.high_score = self.high_score # Mantener la puntuación alta
        self.dino = new_game.dino
        self.ground = new_game.ground
        self.obstacles = new_game.obstacles
        self.clouds = new_game.clouds
        self.score = new_game.score
        self.game_over = new_game.game_over
        self.paused = new_game.paused
        self.time_of_day = 0 # Reiniciar el ciclo
        self.new_high_score_achieved = False
        
    def check_collision(self, rect1, rect2):
        """Verifica colisión entre dos rectángulos"""
        return (rect1['x'] < rect2['x'] + rect2['width'] and
                rect1['x'] + rect1['width'] > rect2['x'] and
                rect1['y'] < rect2['y'] + rect2['height'] and
                rect1['y'] + rect1['height'] > rect2['y'])
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Actualizar ciclo día-noche
        self.time_of_day = (self.time_of_day + 1) % self.cycle_duration

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
            obs_type = random.choice(['cactus_small', 'cactus_large', 'cactus_group', 'bird', 'pterodactyl'])
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
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.new_high_score_achieved = True
                    if self.sounds.get('highscore'):
                        self.sounds['highscore'].play()
                    self.save_high_score()
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
            'high_score': self.high_score,
            'new_high_score_achieved': self.new_high_score_achieved,
            'paused': self.paused,
            'time_of_day': self.time_of_day,
            'cycle_duration': self.cycle_duration,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }