# game_logic.py
import random
import json

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
        self.just_landed = False
        self.powerup_active = False
        self.powerup_timer = 0
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vel_y = self.jump_force
            
    def duck(self, ducking):
        self.ducking = ducking
        
    def update(self):
        # Actualizar power-up
        if self.powerup_active:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powerup_active = False

        if self.jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            
            if self.y >= self.ground:
                self.y = self.ground
                self.jumping = False
                self.just_landed = True # Bandera para indicar que acaba de aterrizar
                self.vel_y = 0
        
        # Animación de carrera
        if not self.jumping and not self.ducking:
            self.anim_timer += 1
            if self.anim_timer > 6: # Cambiar de frame cada 6 ticks
                self.anim_frame = (self.anim_frame + 1) % 2
                self.anim_timer = 0
        else:
            # Reiniciar la bandera si no está en el suelo
            self.just_landed = False
                
    def get_rect(self):
        if self.ducking and not self.jumping:
            return {
                'x': self.x,
                'y': self.y + 30,
                'width': 55, # Ancho ajustado para coincidir con el sprite agachado
                'height': 30 # Altura ajustada
            }
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    def activate_powerup(self, duration=300): # 5 segundos a 60 FPS
        self.powerup_active = True
        self.powerup_timer = duration
    

class Obstacle:
    def __init__(self, x, obs_type, ground_y, speed=8):
        self.x = x
        self.type = obs_type
        self.speed = speed
        self.destroyed = False
        
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
            elif obs_type == 'cactus_triple':
                self.width = 65 # Hitbox para tres cactus
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
        
        if self.destroyed:
            # Los fragmentos caen y se desvanecen
            self.y += 2
        
    def get_rect(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    def off_screen(self):
        return self.x < -50 or self.y > 500 # También se elimina si cae fuera de la pantalla

    def destroy(self):
        if 'cactus' in self.type:
            self.destroyed = True
            self.speed = 0 # Detener el movimiento horizontal


class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 8

    def update(self):
        self.x -= self.speed

    def get_rect(self):
        return {'x': self.x, 'y': self.y, 'width': self.width, 'height': self.height}

    def off_screen(self):
        return self.x < -self.width


class Cloud:
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = random.randint(40, 80)
        self.height = random.randint(15, 30)

    def update(self):
        self.x -= self.speed

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
            
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, -0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.lifespan = random.randint(15, 30) # Duración en frames
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1


class Star:
    def __init__(self, x, y, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height // 2)
        self.size = random.randint(1, 2)
        self.blink_rate = random.randint(50, 150)
        self.blink_timer = random.randint(0, self.blink_rate)

    def update(self):
        self.blink_timer = (self.blink_timer + 1) % self.blink_rate

class GameEngine:
    def __init__(self, width=800, height=400, sounds=None):
        self.width = width
        self.height = height
        self.ground_y = height - 100
        self.speed = 8
        self.high_score = 0
        self.data_file = "game_data.json"
        self.speed_increase_interval = 10 # Aumentar velocidad cada 10 puntos
        self.next_speed_increase_score = self.speed_increase_interval
        
        self.sounds = sounds if sounds is not None else {}
        
        self.dino = Dino(50, self.ground_y)
        self.ground = Ground(height - 40, speed=self.speed)
        self.obstacles = []
        self.clouds = []
        self.powerups = []
        self.particles = []
        self.stars = [Star(0, 0, width, height) for _ in range(50)] # Generar 50 estrellas
        self.score = 0
        self.started = False
        self.game_over = False
        self.paused = False
        self.new_high_score_achieved = False

        # Ciclo día-noche
        self.time_of_day = 0
        self.cycle_duration = 4800 # 80 segundos a 60 FPS

        self.load_data()
        
        self.spawn_timer = 0
        self.cloud_spawn_timer = 0
        self.cloud_spawn_interval = random.randint(120, 240)
        self.spawn_interval = random.randint(60, 120)

    def load_data(self):
        """Carga datos del juego desde un archivo JSON."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.high_score = data.get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_score = 0

    def save_data(self):
        """Guarda datos del juego en un archivo JSON."""
        data = {
            "high_score": self.high_score
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        
    def toggle_pause(self):
        """Activa o desactiva la pausa del juego."""
        if not self.game_over:
            self.paused = not self.paused

    def start_game(self):
        if not self.started:
            self.started = True

    def handle_jump(self):
        if self.started and not self.game_over and not self.paused:
            if self.sounds.get('jump') and not self.dino.jumping:
                self.sounds['jump'].play()
            self.dino.jump()
            
    def handle_duck(self, ducking):
        if self.started and not self.game_over and not self.paused:
            self.dino.duck(ducking)
            
    def restart(self):
        """Reinicia el estado del juego."""
        new_game = GameEngine(self.width, self.height, self.sounds)
        new_game.high_score = self.high_score # Mantener la puntuación alta
        new_game.start_game() # El juego reiniciado comienza inmediatamente
        self.dino = new_game.dino
        self.ground = new_game.ground
        self.obstacles = new_game.obstacles
        self.clouds = new_game.clouds
        self.particles = []
        self.stars = new_game.stars
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
        if not self.started or self.game_over or self.paused:
            return
            
        # Actualizar ciclo día-noche
        self.time_of_day = (self.time_of_day + 1) % self.cycle_duration

        # Actualizar dinosaurio
        self.dino.update()
        
        # Generar partículas al aterrizar
        if hasattr(self.dino, 'just_landed') and self.dino.just_landed:
            for _ in range(10): # Explosión de partículas
                self.particles.append(Particle(self.dino.x + 10, self.dino.y + self.dino.height))
            self.dino.just_landed = False

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

        # Generar partículas al correr
        if not self.dino.jumping and not self.dino.ducking and self.dino.anim_timer % 4 == 0:
            self.particles.append(Particle(self.dino.x, self.dino.y + self.dino.height))

        # Actualizar partículas
        for p in self.particles[:]:
            p.update()
            if p.lifespan <= 0:
                self.particles.remove(p)

        for star in self.stars:
            star.update()

        # Generar y actualizar power-ups
        if random.random() < 0.001 and not self.dino.powerup_active: # Probabilidad baja de aparecer
            self.powerups.append(PowerUp(self.width, self.ground_y + 40))
        
        for pu in self.powerups[:]:
            pu.update()
            if self.check_collision(self.dino.get_rect(), pu.get_rect()):
                self.dino.activate_powerup()
                self.powerups.remove(pu)
            elif pu.off_screen():
                self.powerups.remove(pu)

        # Generar obstáculos
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_interval:
            # Lógica de generación de obstáculos mejorada
            choice = random.random()
            if choice < 0.6: # 60% de probabilidad de cactus
                obs_type = random.choice(['cactus_small', 'cactus_large', 'cactus_group', 'cactus_triple'])
            elif choice < 0.85: # 25% de probabilidad de enemigos aéreos
                obs_type = random.choice(['bird', 'pterodactyl'])
            else: # 15% de probabilidad de grupos de pájaros
                num_birds = random.choice([2, 3])
                for i in range(num_birds):
                    # Añade pájaros con un pequeño desfase para que no estén superpuestos
                    bird_x = self.width + (i * 80)
                    self.obstacles.append(Obstacle(bird_x, 'bird', self.ground_y, speed=self.speed))
                obs_type = None # No generar un obstáculo adicional

            if obs_type:
                self.obstacles.append(Obstacle(self.width, obs_type, self.ground_y, speed=self.speed))
            self.spawn_timer = 0
            self.spawn_interval = random.randint(60, 120)
            
        # Actualizar obstáculos
        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen() and not obs.destroyed:
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
            if not obs.destroyed and self.check_collision(self.dino.get_rect(), obs.get_rect()):
                if self.dino.powerup_active and 'cactus' in obs.type:
                    obs.destroy()
                    # Aquí podrías añadir un sonido de "romper"
                else:
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.new_high_score_achieved = True
                        if self.sounds.get('highscore'):
                            self.sounds['highscore'].play()
                    self.save_data()
                    if self.sounds.get('die'):
                        self.sounds['die'].play()
            elif obs.destroyed and obs.off_screen():
                self.obstacles.remove(obs)
                
    def get_game_state(self):
        """Retorna el estado completo del juego para renderizado"""
        return {
            'dino': self.dino,
            'ground': self.ground,
            'obstacles': self.obstacles,
            'clouds': self.clouds,
            'powerups': self.powerups,
            'particles': self.particles,
            'stars': self.stars,
            'score': self.score,
            'high_score': self.high_score,
            'started': self.started,
            'new_high_score_achieved': self.new_high_score_achieved,
            'paused': self.paused,
            'time_of_day': self.time_of_day,
            'cycle_duration': self.cycle_duration,
            'game_over': self.game_over,
            'width': self.width,
            'height': self.height
        }