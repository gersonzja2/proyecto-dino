# game_view.py
import pygame
import numpy as np
import sys
from logica import GameEngine

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
game_sounds = {"jump": jump_sound, "point": point_sound, "die": die_sound}


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        
    def draw_dino(self, dino_state):
        """Dibuja el dinosaurio basado en su estado"""
        x = dino_state['x']
        y = dino_state['y']
        width = dino_state['width']
        height = dino_state['height']
        ducking = dino_state['ducking']
        jumping = dino_state['jumping']
        
        # El cuerpo del dinosaurio se dibuja con varios rectángulos para darle forma
        if ducking and not jumping:
            # Dinosaurio agachado
            pygame.draw.rect(self.screen, GRAY, (x, y + 30, 55, 30)) # Cuerpo
            pygame.draw.rect(self.screen, GRAY, (x + 55, y + 30, 20, 20)) # Cabeza
            pygame.draw.rect(self.screen, BLACK, (x + 65, y + 35, 5, 5)) # Ojo
        else:
            # Dinosaurio de pie
            pygame.draw.rect(self.screen, GRAY, (x, y + 20, 30, 40)) # Cuerpo
            pygame.draw.rect(self.screen, GRAY, (x - 10, y + 40, 10, 10)) # Cola
            pygame.draw.rect(self.screen, GRAY, (x + 5, y + 60, 10, 10)) # Pierna trasera
            pygame.draw.rect(self.screen, GRAY, (x + 20, y + 60, 10, 10)) # Pierna delantera
            pygame.draw.rect(self.screen, GRAY, (x + 20, y + 25, 10, 5)) # Brazo
            pygame.draw.rect(self.screen, GRAY, (x + 25, y, 25, 25)) # Cabeza
            pygame.draw.rect(self.screen, BLACK, (x + 40, y + 5, 5, 5)) # Ojo

            
    def draw_obstacle(self, obs_state):
        """Dibuja un obstáculo basado en su estado"""
        x = obs_state['x']
        y = obs_state['y']
        width = obs_state['width']
        height = obs_state['height']
        obs_type = obs_state['type']
        
        if 'cactus' in obs_type:
            # Dibuja el cactus principal
            pygame.draw.rect(self.screen, GRAY, (x, y, width, height))
            # Dibuja detalles adicionales según el tipo
            if obs_type == 'cactus_large':
                pygame.draw.rect(self.screen, GRAY, (x - 8, y + 10, 10, 15)) # Brazo izquierdo
            if obs_type == 'cactus_group':
                # Dibuja un segundo cactus más pequeño al lado
                pygame.draw.rect(self.screen, GRAY, (x + 25, y + 10, 15, 30))
        else:  # bird
            # Pájaro
            pygame.draw.ellipse(self.screen, GRAY, (x, y, width, height))
            pygame.draw.polygon(self.screen, GRAY, [
                (x, y + 15),
                (x - 15, y + 10),
                (x - 10, y + 20)
            ])
            
    def draw_ground(self, ground_state, width):
        """Dibuja el suelo basado en su estado"""
        x = ground_state['x']
        y = ground_state['y']
        
        # Línea del suelo
        pygame.draw.line(self.screen, GRAY, (0, y), (width, y), 3)
        # Detalles del suelo
        for i in range(0, width + 50, 50):
            draw_x = i + x
            pygame.draw.line(self.screen, GRAY, (draw_x, y + 5), (draw_x + 20, y + 5), 2)
            
    def draw_score(self, score, width):
        """Dibuja el puntaje"""
        score_text = self.font.render(f"Score: {score}", True, GRAY)
        self.screen.blit(score_text, (width - 150, 20))
        
    def draw_game_over(self, width, height):
        """Dibuja la pantalla de game over"""
        game_over_text = self.font.render("GAME OVER", True, GRAY)
        restart_text = self.small_font.render("Press SPACE to restart", True, GRAY)
        self.screen.blit(game_over_text, (width // 2 - 100, height // 2 - 50))
        self.screen.blit(restart_text, (width // 2 - 150, height // 2))
        
    def render(self, game_state):
        """Renderiza el estado completo del juego"""
        # Limpiar pantalla
        self.screen.fill(WHITE)
        
        # Dibujar elementos
        self.draw_ground(game_state['ground'], game_state['width'])
        self.draw_dino(game_state['dino'])
        
        for obs_state in game_state['obstacles']:
            self.draw_obstacle(obs_state)
            
        self.draw_score(game_state['score'], game_state['width'])
        
        if game_state['game_over']:
            self.draw_game_over(game_state['width'], game_state['height'])
            
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
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        game.restart()
                    else:
                        game.handle_jump()
                elif event.key == pygame.K_UP and not game.game_over:
                    game.handle_jump()
        
        # Manejar tecla de agacharse (mantenida)
        if not game.game_over:
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