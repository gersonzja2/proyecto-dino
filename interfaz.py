# game_view.py
import pygame
import numpy as np
import sys
from logica import GameEngine
import random

pygame.init()
pygame.mixer.init() # Inicializar el mezclador de audio

# Configuración de pantalla
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dinosaurio - Chrome Game")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (83, 83, 83)
NIGHT_BLUE = (25, 25, 112)

# FPS
clock = pygame.time.Clock()
FPS = 60

def generate_sound(frequency=440, duration=0.1, volume=0.1):
    """Genera un sonido simple y lo devuelve como un objeto pygame.mixer.Sound."""
    sample_rate = pygame.mixer.get_init()[0]
    n_samples = int(round(duration * sample_rate))
    
    # Generar la onda de sonido
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    max_sample = 2**(16 - 1) - 1
    
    t = np.linspace(0., duration, n_samples, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    
    # Aplicar volumen y convertir a formato de 16 bits
    buf[:,0] = (wave * max_sample * volume).astype(np.int16)
    buf[:,1] = buf[:,0] # Sonido estéreo
    
    return pygame.sndarray.make_sound(buf)

# Generar sonidos en lugar de cargarlos desde archivos
jump_sound = generate_sound(660, 0.05, 0.1)  # Tono agudo y corto
point_sound = generate_sound(880, 0.05, 0.08) # Tono más agudo para puntos
die_sound = generate_sound(220, 0.2, 0.15)   # Tono grave y más largo
highscore_sound = generate_sound(1046, 0.15, 0.1) # Tono muy agudo para nuevo récord
game_sounds = {"jump": jump_sound, "point": point_sound, "die": die_sound, "highscore": highscore_sound}


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.blink_timer = 0
        
    def draw_dino(self, dino_state):
        """Dibuja el dinosaurio basado en su objeto de estado"""
        x, y, width, height = dino_state.x, dino_state.y, dino_state.width, dino_state.height
        
        # El cuerpo del dinosaurio se dibuja con varios rectángulos para darle forma
        if dino_state.ducking and not dino_state.jumping:
            # Dinosaurio agachado
            pygame.draw.rect(self.screen, GRAY, (x, y + 30, 55, 30)) # Cuerpo
            pygame.draw.rect(self.screen, GRAY, (x + 55, y + 30, 20, 20)) # Cabeza
            pygame.draw.rect(self.screen, BLACK, (x + 65, y + 35, 5, 5)) # Ojo
        else:
            # Dinosaurio de pie
            pygame.draw.rect(self.screen, GRAY, (x, y + 20, 30, 40)) # Cuerpo
            pygame.draw.rect(self.screen, GRAY, (x - 10, y + 40, 10, 10)) # Cola
            # Animación de piernas
            if dino_state.anim_frame == 0:
                pygame.draw.rect(self.screen, GRAY, (x + 5, y + 60, 10, 10)) # Pierna trasera
                pygame.draw.rect(self.screen, GRAY, (x + 20, y + 55, 10, 15)) # Pierna delantera
            else:
                pygame.draw.rect(self.screen, GRAY, (x + 5, y + 55, 10, 15)) # Pierna trasera
                pygame.draw.rect(self.screen, GRAY, (x + 20, y + 60, 10, 10)) # Pierna delantera
            pygame.draw.rect(self.screen, GRAY, (x + 20, y + 25, 10, 5)) # Brazo
            pygame.draw.rect(self.screen, GRAY, (x + 25, y, 25, 25)) # Cabeza
            pygame.draw.rect(self.screen, BLACK, (x + 40, y + 5, 5, 5)) # Ojo

            
    def draw_obstacle(self, obs_state):
        """Dibuja un obstáculo basado en su objeto de estado"""
        x, y, width, height = obs_state.x, obs_state.y, obs_state.width, obs_state.height
        obs_type = obs_state.type
        
        if 'cactus' in obs_type:
            # Dibuja el cactus principal
            pygame.draw.rect(self.screen, GRAY, (x, y, 20, height)) # Dibuja el primer cactus
            # Dibuja detalles adicionales según el tipo
            if obs_type == 'cactus_large':
                pygame.draw.rect(self.screen, GRAY, (x - 8, y + 10, 10, 15)) # Brazo izquierdo
            elif obs_type == 'cactus_group':
                # Dibuja un segundo cactus más pequeño al lado
                pygame.draw.rect(self.screen, GRAY, (x + 25, y + 10, 15, 30))
            elif obs_type == 'cactus_triple':
                pygame.draw.rect(self.screen, GRAY, (x + 22, y, 20, height)) # Segundo cactus
                pygame.draw.rect(self.screen, GRAY, (x + 44, y, 20, height)) # Tercer cactus

        elif obs_type == 'bird':
            # Pájaro
            pygame.draw.ellipse(self.screen, GRAY, (x, y, width, height))
            # Animación de alas
            if obs_state.anim_frame == 0: # Alas arriba
                pygame.draw.polygon(self.screen, GRAY, [(x + 10, y + 5), (x + 30, y + 5), (x + 20, y - 5)])
            else: # Alas abajo
                pygame.draw.polygon(self.screen, GRAY, [(x + 10, y + 10), (x + 30, y + 10), (x + 20, y + 20)])
        else: # pterodactyl
            # Cuerpo y cabeza
            pygame.draw.polygon(self.screen, GRAY, [(x, y + 10), (x + 20, y + 10), (x + 30, y), (x + 45, y + 5)])
            # Animación de alas
            if obs_state.anim_frame == 0: # Alas arriba
                pygame.draw.polygon(self.screen, GRAY, [(x + 10, y + 10), (x + 30, y), (x + 40, y)])
            else: # Alas abajo
                pygame.draw.polygon(self.screen, GRAY, [(x + 10, y + 10), (x + 30, y + 20), (x + 40, y + 20)])
            
    def draw_cloud(self, cloud_state):
        """Dibuja una nube"""
        pygame.draw.ellipse(self.screen, GRAY, (cloud_state.x, cloud_state.y, cloud_state.width, cloud_state.height))

    def draw_particles(self, particles, is_night):
        """Dibuja las partículas de polvo."""
        particle_color = (120, 120, 120) if not is_night else (180, 180, 180)
        for p in particles:
            pygame.draw.circle(self.screen, particle_color, (p.x, p.y), p.size)

    def draw_stars(self, stars):
        """Dibuja las estrellas en el cielo nocturno."""
        for star in stars:
            # La visibilidad se calcula aquí en la interfaz
            is_visible = star.blink_timer < 5
            if is_visible:
                # El color parpadea ligeramente
                brightness = random.randint(180, 255)
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (star.x, star.y), star.size)

    def draw_sun_and_moon(self, time_of_day, cycle_duration, width, height):
        """Dibuja el sol o la luna según la hora del día."""
        progress = (time_of_day % cycle_duration) / cycle_duration
        angle = progress * 2 * np.pi

        # Posición celestial
        celestial_x = width / 2 - np.cos(angle) * (width / 2.5)
        celestial_y = height / 2 + np.sin(angle) * (height / 2.5)

        # El sol es visible durante la primera mitad del ciclo (día)
        if 0 <= progress < 0.5:
            if celestial_y < height - 100: # Solo si está por encima del suelo
                pygame.draw.circle(self.screen, (255, 255, 0), (celestial_x, celestial_y), 20)
        # La luna es visible durante la segunda mitad (noche)
        else:
            if celestial_y < height - 100:
                pygame.draw.circle(self.screen, (240, 240, 240), (celestial_x, celestial_y), 20) # Luna
                # Cráter para dar apariencia de luna
                pygame.draw.circle(self.screen, (200, 200, 200), (celestial_x + 8, celestial_y - 5), 4)

    def draw_ground(self, ground_state, width):
        """Dibuja el suelo basado en su estado"""
        x = ground_state.x
        y = ground_state.y
        
        # Línea del suelo
        pygame.draw.line(self.screen, GRAY, (0, y), (width, y), 3)
        # Detalles del suelo
        for i in range(0, width + 50, 50):
            draw_x = i + x
            pygame.draw.line(self.screen, GRAY, (draw_x, y + 5), (draw_x + 20, y + 5), 2)
            
    def draw_score(self, score, high_score, width, new_high_score, is_night):
        """Dibuja el puntaje"""
        self.blink_timer = (self.blink_timer + 1) % 40 # Ciclo de parpadeo
        text_color = WHITE if is_night else GRAY
        
        # Si hay nuevo récord, parpadea el texto "HI"
        if new_high_score and self.blink_timer < 20:
            high_score_text = self.font.render(f"HI {high_score:05}", True, text_color if is_night else WHITE)
        else:
            high_score_text = self.font.render(f"HI {high_score:05}", True, text_color)

        score_text = self.font.render(f"{score:05}", True, text_color)
        self.screen.blit(high_score_text, (width - 250, 20))
        self.screen.blit(score_text, (width - 120, 20))
        
    def draw_game_over(self, width, height):
        """Dibuja la pantalla de game over"""
        game_over_text = self.font.render("GAME OVER", True, GRAY)
        restart_text = self.small_font.render("Press SPACE to restart", True, GRAY)
        self.screen.blit(game_over_text, (width // 2 - 100, height // 2 - 50))
        self.screen.blit(restart_text, (width // 2 - 150, height // 2))
        
    def draw_pause_screen(self, width, height):
        """Dibuja la pantalla de pausa."""
        # Capa semitransparente
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128)) # Negro con 50% de opacidad
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (width // 2 - 70, height // 2 - 30))

    def render(self, game_state):
        """Renderiza el estado completo del juego"""
        time_of_day = game_state['time_of_day']
        cycle_duration = game_state['cycle_duration']
        progress = time_of_day / cycle_duration

        # Interpolar color de fondo
        if progress < 0.45: # Día
            bg_color = WHITE
        elif progress < 0.55: # Atardecer
            trans_progress = (progress - 0.45) / 0.1
            bg_color = tuple(int(WHITE[i] * (1 - trans_progress) + NIGHT_BLUE[i] * trans_progress) for i in range(3))
        elif progress < 0.95: # Noche
            bg_color = NIGHT_BLUE
        else: # Amanecer
            trans_progress = (progress - 0.95) / 0.05
            bg_color = tuple(int(NIGHT_BLUE[i] * (1 - trans_progress) + WHITE[i] * trans_progress) for i in range(3))

        # Limpiar pantalla
        self.screen.fill(bg_color)
        
        is_night = 0.55 <= progress < 0.95

        # Dibujar estrellas si es de noche
        if is_night:
            self.draw_stars(game_state['stars'])

        # Dibujar elementos
        self.draw_sun_and_moon(time_of_day, cycle_duration, game_state['width'], game_state['height'])
        self.draw_ground(game_state['ground'], game_state['width'])
        
        self.draw_particles(game_state['particles'], is_night)
        for cloud_state in game_state['clouds']:
            self.draw_cloud(cloud_state)

        self.draw_dino(game_state['dino'])
        
        for obs_state in game_state['obstacles']:
            self.draw_obstacle(obs_state)
            
        self.draw_score(game_state['score'], game_state['high_score'], game_state['width'], game_state['new_high_score_achieved'], is_night)
        
        if game_state['game_over']:
            self.draw_game_over(game_state['width'], game_state['height'])
        elif game_state['paused']:
            self.draw_pause_screen(game_state['width'], game_state['height'])
            
        # Actualizar pantalla
        pygame.display.flip()


def main():
    # Inicializar motor del juego (con sonidos) y renderizador
    game = GameEngine(WIDTH, HEIGHT, game_sounds)
    renderer = GameRenderer(screen)
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Procesar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    game.toggle_pause()
                elif event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.restart()
                    else:
                        game.handle_jump()
                elif event.key == pygame.K_UP and not game.game_over:
                    game.handle_jump()
        
        # Manejar tecla de agacharse (mantenida)
        if not game.game_over and not game.paused:
            keys = pygame.key.get_pressed()
            game.handle_duck(keys[pygame.K_DOWN])
        
        # Actualizar lógica del juego
        game.update()
        
        # Renderizar
        game_state = game.get_game_state()
        renderer.render(game_state)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()