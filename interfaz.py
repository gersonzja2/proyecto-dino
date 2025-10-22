# game_view.py
import pygame
import sys
from logica import GameEngine

pygame.init()

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
        
        if ducking and not jumping:
            # Dinosaurio agachado
            pygame.draw.rect(self.screen, GRAY, (x, y + 30, width + 20, height - 30))
        else:
            # Cuerpo
            pygame.draw.rect(self.screen, GRAY, (x, y, width, height))
            # Cabeza
            pygame.draw.rect(self.screen, GRAY, (x + 30, y - 10, 20, 20))
            # Ojo
            pygame.draw.rect(self.screen, BLACK, (x + 40, y - 5, 5, 5))
            
    def draw_obstacle(self, obs_state):
        """Dibuja un obstáculo basado en su estado"""
        x = obs_state['x']
        y = obs_state['y']
        width = obs_state['width']
        height = obs_state['height']
        obs_type = obs_state['type']
        
        if obs_type == 'cactus':
            # Cactus
            pygame.draw.rect(self.screen, GRAY, (x, y, width, height))
            pygame.draw.rect(self.screen, GRAY, (x - 8, y + 10, 10, 15))
            pygame.draw.rect(self.screen, GRAY, (x + width - 2, y + 15, 10, 15))
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
    # Inicializar motor del juego y renderizador
    game = GameEngine(WIDTH, HEIGHT)
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