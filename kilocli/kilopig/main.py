#!/usr/bin/env python3
"""
Flappy KiloPig game with 6 levels and boss fight.
Implements high score management using XML file.
"""

import sys
import subprocess
import os
import xml.etree.ElementTree as ET
import random
import math

import os
os.environ['SDL_AUDIODRIVER'] = 'alsa'

try:
    import pygame
    from pygame import mixer
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
    from pygame import mixer

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
FPS = 60

LEVEL_COLORS = [
    (135, 206, 235),  
    (144, 238, 144),  
    (255, 218, 185),  
    (221, 160, 221),  
    (255, 182, 193),  
    (255, 99, 71),    
]

HIGHSCORE_FILE = "highscore.xml"


def get_high_score():
    """Load high score from XML file."""
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        tree = ET.parse(HIGHSCORE_FILE)
        root = tree.getroot()
        score = int(root.find('score').text)
        return score
    except (ET.ParseError, AttributeError, ValueError):
        return 0


def save_high_score(score):
    """Save high score to XML file."""
    if not os.path.exists(HIGHSCORE_FILE):
        root = ET.Element('highscore')
        score_elem = ET.SubElement(root, 'score')
        score_elem.text = '0'
        tree = ET.ElementTree(root)
        tree.write(HIGHSCORE_FILE)
    
    try:
        tree = ET.parse(HIGHSCORE_FILE)
        root = tree.getroot()
        current = int(root.find('score').text)
        if score > current:
            root.find('score').text = str(score)
            tree.write(HIGHSCORE_FILE)
    except (ET.ParseError, AttributeError, ValueError):
        root = ET.Element('highscore')
        score_elem = ET.SubElement(root, 'score')
        score_elem.text = str(score)
        tree = ET.ElementTree(root)
        tree.write(HIGHSCORE_FILE)


class Bird:
    """The player-controlled bird."""
    
    def __init__(self):
        self.x = 150
        self.y = SCREEN_HEIGHT // 2
        self.width = 40
        self.height = 30
        self.velocity = 0
        self.gravity = 0.5
        self.flap_strength = -8
        self.angle = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.wing_offset = 0
        self.wing_timer = 0
    
    def flap(self):
        """Make the bird jump upward."""
        self.velocity = self.flap_strength
    
    def update(self):
        """Update bird position and physics."""
        self.velocity += self.gravity
        self.y += self.velocity
        self.angle = min(max(self.velocity * 3, -30), 90)
        self.rect.y = int(self.y)
        
        self.wing_timer += 1
        if self.wing_timer >= 8:
            self.wing_timer = 0
            self.wing_offset = -self.wing_offset if self.wing_offset != 0 else 8
        
        if self.y < 0:
            self.y = 0
            self.velocity = 0
    
    def draw(self, screen, ai_mode=False):
        """Draw the pig with rotation."""
        pig_color = (255, 182, 193)  # Pink
        pig_dark = (255, 105, 180)   # Darker pink
        wing_color = (255, 255, 255) # White wings
        rocket_color = (100, 100, 100) # Gray rockets
        rocket_fire = (255, 140, 0)   # Orange fire
        eye_color = (0, 0, 0)
        snout_color = (255, 150, 170)
        
        angle = self.angle
        
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Body
        body_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, pig_color, (0, 0, self.width, self.height))
        
        # Draw wings or rockets based on mode
        if ai_mode:
            # Rockets
            rocket_surf = pygame.Surface((self.width + 30, self.height + 20), pygame.SRCALPHA)
            # Left rocket
            pygame.draw.rect(rocket_surf, rocket_color, (0, 8, 12, 18), border_radius=3)
            pygame.draw.polygon(rocket_surf, rocket_fire, [(0, 26), (6, 20), (12, 26)])
            # Right rocket
            pygame.draw.rect(rocket_surf, rocket_color, (self.width + 12, 8, 12, 18), border_radius=3)
            pygame.draw.polygon(rocket_surf, rocket_fire, [(self.width + 12, 26), (self.width + 18, 20), (self.width + 24, 26)])
            
            wing_surf = rocket_surf
        else:
            # Wings
            wing_surf = pygame.Surface((self.width + 20, self.height + 10), pygame.SRCALPHA)
            wing_y = 5 + self.wing_offset
            pygame.draw.ellipse(wing_surf, wing_color, (-5, wing_y, 25, 15))
            pygame.draw.ellipse(wing_surf, wing_color, (self.width - 15, wing_y, 25, 15))
        
        # Head
        head_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(head_surf, pig_color, (15, 15), 14)
        
        # Eyes
        pygame.draw.circle(head_surf, eye_color, (10, 12), 3)
        pygame.draw.circle(head_surf, eye_color, (20, 12), 3)
        
        # Snout
        pygame.draw.ellipse(head_surf, snout_color, (8, 16, 14, 10))
        pygame.draw.circle(head_surf, pig_dark, (11, 20), 2)
        pygame.draw.circle(head_surf, pig_dark, (19, 20), 2)
        
        # Ears
        pygame.draw.polygon(head_surf, pig_color, [(2, 8), (8, 0), (12, 8)])
        pygame.draw.polygon(head_surf, pig_color, [(18, 8), (22, 0), (28, 8)])
        
        if angle != 0:
            body_surf = pygame.transform.rotate(body_surf, -angle)
            wing_surf = pygame.transform.rotate(wing_surf, -angle)
            head_surf = pygame.transform.rotate(head_surf, -angle)
            
            body_rect = body_surf.get_rect(center=(center_x, center_y))
            wing_rect = wing_surf.get_rect(center=(center_x, center_y))
            head_rect = head_surf.get_rect(center=(center_x + 10, center_y - 3))
            
            screen.blit(wing_surf, wing_rect)
            screen.blit(body_surf, body_rect)
            screen.blit(head_surf, head_rect)
        else:
            if ai_mode:
                screen.blit(wing_surf, (self.x - 5, self.y - 10))
            else:
                screen.blit(wing_surf, (self.x - 10, self.y - 5))
            screen.blit(body_surf, (self.x, self.y))
            screen.blit(head_surf, (self.x + 10, self.y - 3))
    
    def reset(self):
        """Reset bird to initial state."""
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.angle = 0


class Pipe:
    """Obstacle pipe in the game."""
    
    def __init__(self, x, gap_height, gap_y):
        self.x = x
        self.gap_height = gap_height
        self.gap_y = gap_y
        self.width = 70
        self.speed = 3
        self.passed = False
        self.top_rect = pygame.Rect(x, 0, self.width, gap_y)
        self.bottom_rect = pygame.Rect(x, gap_y + gap_height, self.width, SCREEN_HEIGHT - gap_y - gap_height)
    
    def update(self, speed):
        """Update pipe position."""
        self.speed = speed
        self.x -= speed
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)
    
    def draw(self, screen):
        """Draw the pipes."""
        pipe_color = (34, 139, 34)
        pipe_highlight = (50, 205, 50)
        border_color = (0, 100, 0)
        
        pygame.draw.rect(screen, border_color, (self.top_rect.x - 2, self.top_rect.y - 2, 
                                                self.width + 4, self.top_rect.height + 4))
        pygame.draw.rect(screen, pipe_color, self.top_rect)
        pygame.draw.rect(screen, pipe_highlight, (self.top_rect.x + 5, self.top_rect.y + 5,
                                                  self.width - 10, self.top_rect.height - 10))
        
        pygame.draw.rect(screen, border_color, (self.bottom_rect.x - 2, self.bottom_rect.y - 2,
                                                self.width + 4, self.bottom_rect.height + 4))
        pygame.draw.rect(screen, pipe_color, self.bottom_rect)
        pygame.draw.rect(screen, pipe_highlight, (self.bottom_rect.x + 5, self.bottom_rect.y + 5,
                                                   self.width - 10, self.bottom_rect.height - 10))
    
    def check_collision(self, bird_rect):
        """Check if bird collides with pipe."""
        return self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect)
    
    def is_off_screen(self):
        """Check if pipe is off screen."""
        return self.x + self.width < 0


class Projectile:
    """Projectile fired by player during boss fight."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.radius = 8
        self.rect = pygame.Rect(x, y, self.radius * 2, self.radius * 2)
    
    def update(self):
        """Update projectile position."""
        self.x += self.speed
        self.rect.x = int(self.x)
    
    def draw(self, screen):
        """Draw the projectile."""
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x + self.radius), int(self.y + self.radius)), self.radius)
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x + self.radius), int(self.y + self.radius)), self.radius - 3)
    
    def is_off_screen(self):
        """Check if projectile is off screen."""
        return self.x > SCREEN_WIDTH


class Boss:
    """The final boss in level 6."""
    
    def __init__(self):
        self.x = SCREEN_WIDTH - 150
        self.y = SCREEN_HEIGHT // 2
        self.width = 120
        self.height = 100
        self.hp = 20
        self.max_hp = 20
        self.direction = 1
        self.speed = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.shoot_timer = 0
        self.shoot_interval = 90
    
    def update(self):
        """Update boss position and behavior."""
        self.y += self.speed * self.direction
        
        if self.y <= 50:
            self.direction = 1
        elif self.y + self.height >= SCREEN_HEIGHT - 50:
            self.direction = -1
        
        self.rect.y = int(self.y)
        
        self.shoot_timer += 1
    
    def should_shoot(self):
        """Check if boss should shoot."""
        return self.shoot_timer >= self.shoot_interval
    
    def reset_shoot(self):
        """Reset shoot timer."""
        self.shoot_timer = 0
    
    def draw(self, screen):
        """Draw the boss."""
        boss_color = (139, 0, 0)
        eye_color = (255, 0, 0)
        outline_color = (0, 0, 0)
        
        pygame.draw.rect(screen, outline_color, (self.rect.x - 3, self.rect.y - 3, 
                                                   self.width + 6, self.height + 6), border_radius=10)
        pygame.draw.rect(screen, boss_color, self.rect, border_radius=10)
        
        pygame.draw.circle(screen, eye_color, (int(self.x + 30), int(self.y + 30)), 12)
        pygame.draw.circle(screen, eye_color, (int(self.x + self.width - 30), int(self.y + 30)), 12)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 30), int(self.y + 30)), 6)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + self.width - 30), int(self.y + 30)), 6)
        
        mouth_y = self.y + self.height - 25
        pygame.draw.arc(screen, (0, 0, 0), 
                        (self.x + 20, mouth_y, self.width - 40, 30),
                        0, 3.14, 3)
        
        hp_bar_width = 100
        hp_bar_height = 10
        hp_bar_x = self.x + (self.width - hp_bar_width) // 2
        hp_bar_y = self.y - 20
        
        pygame.draw.rect(screen, (100, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        hp_width = int(hp_bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (hp_bar_x, hp_bar_y, hp_width, hp_bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1)


class BossProjectile:
    """Projectile fired by boss."""
    
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 6
        self.radius = 10
        
        dx = target_x - x
        dy = target_y - y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            dist = 1
        
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        
        self.rect = pygame.Rect(x, y, self.radius * 2, self.radius * 2)
    
    def update(self):
        """Update projectile position."""
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def draw(self, screen):
        """Draw the projectile."""
        pygame.draw.circle(screen, (255, 50, 50), (int(self.x + self.radius), int(self.y + self.radius)), self.radius)
        pygame.draw.circle(screen, (200, 0, 0), (int(self.x + self.radius), int(self.y + self.radius)), self.radius - 4)
    
    def is_off_screen(self):
        """Check if projectile is off screen."""
        return (self.x < -20 or self.x > SCREEN_WIDTH + 20 or 
                self.y < -20 or self.y > SCREEN_HEIGHT + 20)


class Firework:
    """Firework particle effect."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 165, 0)]
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 60,
                'color': random.choice(colors)
            })
    
    def update(self):
        """Update particles."""
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # Gravity
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, screen):
        """Draw particles."""
        for p in self.particles:
            alpha = p['life'] / 60
            size = int(4 * alpha) + 1
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), size)
    
    def is_done(self):
        return len(self.particles) == 0


class Game:
    """Main game class handling all game states."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy KiloPig - 6 Levels & Boss Fight")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.large_font = pygame.font.Font(None, 80)
        
        self.state = "start"
        self.bird = Bird()
        self.pipes = []
        self.projectiles = []
        self.boss = None
        self.boss_projectiles = []
        
        self.score = 0
        self.high_score = get_high_score()
        self.level = 1
        self.level_transition = False
        self.level_transition_timer = 0
        
        self.pipe_timer = 0
        self.base_pipe_interval = 1500
        
        self.running = True
        self.ai_mode = False
        self.ai_timer = 0
        self.fireworks = []
        
        self.try_init_audio()
    
    def try_init_audio(self):
        """Try to initialize audio, gracefully handle if unavailable."""
        try:
            mixer.init()
            self.sound_enabled = True
            self.sounds = {}
            self.generate_sounds()
        except Exception as e:
            print(f"Audio init failed: {e}")
            self.sound_enabled = False
    
    def generate_sounds(self):
        """Generate and save sound effects to files, then load them."""
        if not self.sound_enabled:
            return
        
        import wave as wavefile
        import struct
        import sys
        
        sample_rate = 44100
        
        # Check if running as bundled exe
        if getattr(sys, 'frozen', False):
            try:
                base_path = sys._MEIPASS
            except:
                base_path = '/tmp'
        else:
            base_path = '/tmp'
        
        sound_data = {
            'flap': 'whoosh',
            'score': 'chime',
            'hit': 'explosion',
            'levelup': 'powerup',
            'boss_hit': 'hit_sound',
        }
        
        for name, sound_type in sound_data.items():
            filepath = f"{base_path}/sounds/flappy_{name}.wav"
            if os.path.exists(filepath):
                self.sounds[name] = mixer.Sound(filepath)
            else:
                # Generate dramatic sound
                if sound_type == 'whoosh':
                    sound = self.make_whoosh(sample_rate)
                elif sound_type == 'chime':
                    sound = self.make_chime(sample_rate)
                elif sound_type == 'explosion':
                    sound = self.make_explosion(sample_rate)
                elif sound_type == 'powerup':
                    sound = self.make_powerup(sample_rate)
                elif sound_type == 'hit_sound':
                    sound = self.make_hit_sound(sample_rate)
                else:
                    sound = self.make_tone(440, 0.2, sample_rate)
                
                tmp_path = f"/tmp/flappy_{name}.wav"
                with wavefile.open(tmp_path, 'w') as w:
                    w.setnchannels(1)
                    w.setsampwidth(2)
                    w.setframerate(sample_rate)
                    data = struct.pack('<' + 'h' * len(sound), * (sound * 32767).astype(np.int16))
                    w.writeframesraw(data)
                self.sounds[name] = mixer.Sound(tmp_path)
        
        # Victory fanfare
        victory_path = f"{base_path}/sounds/flappy_victory.wav"
        if os.path.exists(victory_path):
            self.sounds['victory'] = mixer.Sound(victory_path)
        else:
            victory_tone = self.make_fanfare(sample_rate)
            tmp_path = "/tmp/flappy_victory.wav"
            with wavefile.open(tmp_path, 'w') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sample_rate)
                data = struct.pack('<' + 'h' * len(victory_tone), * (victory_tone * 32767).astype(np.int16))
                w.writeframesraw(data)
            self.sounds['victory'] = mixer.Sound(tmp_path)
    
    def make_tone(self, freq, duration, sample_rate):
        """Create a simple tone."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-t * 10)
        return wave * envelope * 0.5
    
    def make_whoosh(self, sample_rate):
        """Create a dramatic whoosh sound for flapping."""
        duration = 0.25
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Mix of frequencies for whoosh
        freq_sweep = np.linspace(800, 200, len(t))
        wave = np.sin(2 * np.pi * freq_sweep * t)
        # Add some noise
        noise = np.random.normal(0, 0.3, len(t))
        wave = wave * 0.7 + noise * 0.3
        envelope = np.exp(-t * 8)
        return wave * envelope * 0.6
    
    def make_chime(self, sample_rate):
        """Create a cheerful chime for scoring."""
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Two-tone chime
        wave1 = np.sin(2 * np.pi * 880 * t)
        wave2 = np.sin(2 * np.pi * 1318 * t)  # Perfect 5th
        wave = wave1 * 0.6 + wave2 * 0.4
        envelope = np.exp(-t * 6)
        return wave * envelope * 0.6
    
    def make_explosion(self, sample_rate):
        """Create an explosion sound."""
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Noise-based explosion
        noise = np.random.normal(0, 1, len(t))
        # Low frequency rumble
        rumble = np.sin(2 * np.pi * 60 * t)
        wave = noise * 0.8 + rumble * 0.2
        envelope = np.exp(-t * 5)
        return wave * envelope * 0.7
    
    def make_powerup(self, sample_rate):
        """Create a power-up sound."""
        duration = 0.4
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Rising frequency sweep
        freq_sweep = np.linspace(300, 1200, len(t))
        wave = np.sin(2 * np.pi * freq_sweep * t)
        # Add harmonics
        wave2 = np.sin(4 * np.pi * freq_sweep * t) * 0.3
        wave = wave + wave2
        envelope = np.exp(-t * 4)
        return wave * envelope * 0.6
    
    def make_hit_sound(self, sample_rate):
        """Create a hit/impact sound."""
        duration = 0.15
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Punchy low frequency
        wave = np.sin(2 * np.pi * 150 * t)
        # Add noise for crunch
        noise = np.random.normal(0, 0.4, len(t))
        wave = wave * 0.7 + noise * 0.3
        envelope = np.exp(-t * 15)
        return wave * envelope * 0.7
    
    def make_fanfare(self, sample_rate):
        """Create a longer victory fanfare."""
        notes = [523, 659, 784, 1047, 784, 659, 523, 659, 784, 1047, 1319, 1047, 784]
        duration = 0.2
        wave = np.array([])
        for note in notes:
            t = np.linspace(0, duration, int(sample_rate * duration))
            tone = np.sin(2 * np.pi * note * t)
            wave = np.concatenate([wave, tone])
        envelope = np.linspace(1, 0, len(wave))
        return wave * envelope * 0.5
    
    def play_sound(self, name):
        """Play a sound effect."""
        if self.sound_enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
    
    def get_level_params(self):
        """Get parameters based on current level."""
        base_speed = 3
        base_gap = 180
        base_interval = self.base_pipe_interval
        
        speed = base_speed + (self.level - 1) * 0.8
        gap = base_gap - (self.level - 1) * 20
        interval = base_interval - (self.level - 1) * 150
        
        return max(speed, 5), max(gap, 100), max(interval, 600)
    
    def spawn_pipe(self):
        """Spawn a new pipe."""
        speed, gap, _ = self.get_level_params()
        gap_y = random.randint(100, SCREEN_HEIGHT - 100 - gap)
        pipe = Pipe(SCREEN_WIDTH, gap, gap_y)
        pipe.speed = speed
        self.pipes.append(pipe)
    
    def start_level_transition(self):
        """Start level transition animation."""
        self.level_transition = True
        self.level_transition_timer = 180
    
    def reset_game(self):
        """Reset game to initial state."""
        self.bird.reset()
        self.pipes = []
        self.projectiles = []
        self.boss = None
        self.boss_projectiles = []
        self.score = 0
        self.level = 1
        self.pipe_timer = 0
        self.level_transition = False
        self.ai_mode = False
        self.ai_timer = 0
    
    def start_boss_fight(self):
        """Start the boss fight."""
        self.boss = Boss()
        self.pipes = []
        self.projectiles = []
        self.boss_projectiles = []
    
    def handle_events(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "start":
                        self.state = "gameplay"
                        self.reset_game()
                    elif self.state == "gameplay":
                        self.bird.flap()
                        self.play_sound('flap')
                    elif self.state == "gameover" or self.state == "victory":
                        self.state = "start"
                
                elif event.key == pygame.K_f:
                    if self.state == "gameplay" and self.level == 6 and self.boss:
                        proj = Projectile(self.bird.x + self.bird.width, self.bird.y + self.bird.height // 2)
                        self.projectiles.append(proj)
                        self.play_sound('flap')
                
                elif event.key == pygame.K_a:
                    if self.state == "start":
                        self.state = "gameplay"
                        self.reset_game()
                        self.ai_mode = True
    
    def update(self):
        """Update game logic."""
        if self.state == "gameplay":
            if self.level_transition:
                self.level_transition_timer -= 1
                if self.level_transition_timer <= 0:
                    self.level_transition = False
            
            if self.level == 6 and not self.boss:
                self.start_boss_fight()
            
            # AI logic
            if self.ai_mode:
                self.ai_timer += 1
                
                if self.level < 6:
                    # Default: stay in middle
                    target_y = SCREEN_HEIGHT // 2 - self.bird.height // 2
                    
                    # Only adjust when very close to pipe (past its left edge)
                    for pipe in self.pipes:
                        if pipe.x < self.bird.x + self.bird.width + 30:
                            # We're at/near the pipe - ensure we're in the gap center
                            gap_center = pipe.gap_y + pipe.gap_height // 2
                            target_y = gap_center - self.bird.height // 2
                            break
                    
                    # Keep well within screen bounds
                    target_y = max(60, min(target_y, SCREEN_HEIGHT - 80))
                    
                    # Move directly to target
                    self.bird.y = target_y
                    self.bird.velocity = 0
                    self.bird.rect.y = int(self.bird.y)
                    
                    # Force update bird's position to match rect
                    self.bird.rect = pygame.Rect(self.bird.x, self.bird.y, self.bird.width, self.bird.height)
                else:
                    # Boss fight - simple pattern: oscillate and shoot
                    if self.boss and self.boss.hp > 0:
                        # Simple up/down oscillation in the middle
                        target_y = SCREEN_HEIGHT // 2 - self.bird.height // 2
                        target_y += int(math.sin(self.ai_timer * 0.03) * 100)
                        
                        # Hard clamp to keep visible
                        self.bird.y = 150
                        self.bird.rect.y = 150
                        self.bird.rect = pygame.Rect(self.bird.x, 150, self.bird.width, self.bird.height)
                        
                        # Shoot at boss
                        if self.ai_timer % 5 == 0:
                            proj = Projectile(self.bird.x + self.bird.width, self.bird.y + self.bird.height // 2)
                            self.projectiles.append(proj)
            
            if self.level < 6:
                self.bird.update()
                
                speed, gap, interval = self.get_level_params()
                current_time = pygame.time.get_ticks()
                
                if current_time - self.pipe_timer > interval:
                    self.spawn_pipe()
                    self.pipe_timer = current_time
                
                for pipe in self.pipes:
                    pipe.update(speed)
                    
                    # Skip collision check in AI mode
                    if not self.ai_mode:
                        if pipe.check_collision(self.bird.rect):
                            self.game_over()
                    
                    if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                        pipe.passed = True
                        self.score += 1
                        self.play_sound('score')
                        
                        if self.score % 10 == 0 and self.level < 6:
                            self.level += 1
                            self.start_level_transition()
                            self.play_sound('levelup')
                
                self.pipes = [p for p in self.pipes if not p.is_off_screen()]
                
                # Skip ground check in AI mode since we control position directly
                if not self.ai_mode:
                    if self.bird.y + self.bird.height >= SCREEN_HEIGHT:
                        self.game_over()
            
            else:
                self.bird.update()
                
                if self.boss:
                    self.boss.update()
                    
                    for proj in self.projectiles:
                        proj.update()
                        
                        if proj.rect.colliderect(self.boss.rect):
                            self.boss.hp -= 1
                            self.play_sound('boss_hit')
                            if proj in self.projectiles:
                                self.projectiles.remove(proj)
                            
                            if self.boss.hp <= 0:
                                self.play_sound('victory')
                                self.boss_projectiles = []  # Clear all boss projectiles
                                self.victory()
                                return
                    
                    self.projectiles = [p for p in self.projectiles if not p.is_off_screen()]
                    
                    if self.boss.should_shoot():
                        boss_proj = BossProjectile(
                            self.boss.x, self.boss.y + self.boss.height // 2,
                            self.bird.x + self.bird.width // 2, self.bird.y + self.bird.height // 2
                        )
                        self.boss_projectiles.append(boss_proj)
                        self.boss.reset_shoot()
                    
                    for boss_proj in self.boss_projectiles:
                        boss_proj.update()
                        
                        # Skip collision check in AI mode
                        if not self.ai_mode:
                            if boss_proj.rect.colliderect(self.bird.rect):
                                self.game_over()
                    
                    self.boss_projectiles = [bp for bp in self.boss_projectiles if not bp.is_off_screen()]
                
                # Skip ground check in AI mode
                if not self.ai_mode:
                    if self.bird.y + self.bird.height >= SCREEN_HEIGHT:
                        self.game_over()
    
    def game_over(self):
        """Handle game over state."""
        self.play_sound('hit')
        self.state = "gameover"
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
    
    def victory(self):
        """Handle victory state."""
        self.state = "victory"
        # Spawn fireworks
        for _ in range(5):
            self.fireworks.append(Firework(random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 2)))
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
    
    def draw(self):
        """Render the game."""
        bg_color = LEVEL_COLORS[self.level - 1] if self.level <= 6 else LEVEL_COLORS[5]
        self.screen.fill(bg_color)
        
        # Update and draw fireworks
        for fw in self.fireworks:
            fw.update()
            fw.draw(self.screen)
        self.fireworks = [fw for fw in self.fireworks if not fw.is_done()]
        
        # Spawn more fireworks periodically in victory
        if self.state == "victory" and random.random() < 0.05:
            self.fireworks.append(Firework(random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT // 2)))
        
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "gameplay":
            self.draw_gameplay()
        elif self.state == "gameover":
            self.draw_gameover()
        elif self.state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_start_screen(self):
        """Draw the start screen."""
        title = self.large_font.render("FLAPPY KILOPIG", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Press SPACE to Flap",
            "Press SPACE to Start",
            "Press A to See KiloPig Using Rockets AI Run",
            "",
            "Levels 1-5: Pass pipes to advance",
            "Level 6: Defeat the boss with F key",
            "",
            f"High Score: {self.high_score}"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50 + i * 35))
            self.screen.blit(text, text_rect)
    
    def draw_gameplay(self):
        """Draw the gameplay screen."""
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        if self.boss:
            self.boss.draw(self.screen)
        
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        for boss_proj in self.boss_projectiles:
            boss_proj.draw(self.screen)
        
        self.bird.draw(self.screen, self.ai_mode)
        
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))
        
        level_text = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
        self.screen.blit(level_text, (SCREEN_WIDTH - 120, 20))
        
        high_text = self.font.render(f"Best: {self.high_score}", True, (0, 0, 0))
        self.screen.blit(high_text, (20, 60))
        
        if self.level == 6:
            boss_hp_text = self.font.render(f"Boss HP: {self.boss.hp if self.boss else 0}", True, (0, 0, 0))
            self.screen.blit(boss_hp_text, (SCREEN_WIDTH - 160, 60))
        
        if self.level_transition:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            level_up_text = self.large_font.render(f"LEVEL {self.level}", True, (255, 255, 0))
            text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(level_up_text, text_rect)
    
    def draw_gameover(self):
        """Draw the game over screen."""
        game_over_text = self.large_font.render("GAME OVER", True, (200, 0, 0))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        high_text = self.font.render(f"High Score: {self.high_score}", True, (0, 0, 0))
        high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(high_text, high_rect)
        
        restart_text = self.font.render("Press SPACE to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """Draw the victory screen."""
        if self.ai_mode:
            victory_text = self.large_font.render("MISSION COMPLETE!", True, (0, 200, 0))
        else:
            victory_text = self.large_font.render("VICTORY!", True, (0, 200, 0))
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(victory_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        high_text = self.font.render(f"High Score: {self.high_score}", True, (0, 0, 0))
        high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(high_text, high_rect)
        
        restart_text = self.font.render("Press SPACE to Play Again", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
