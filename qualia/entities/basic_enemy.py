from dataclasses import dataclass
import pygame


@dataclass(slots=True)
class EnemyContext:
    enemy_center: pygame.Vector2
    player_center: pygame.Vector2
    offset_to_player: pygame.Vector2
    distance_to_player: float
    direction_to_player: pygame.Vector2
    angle_to_player: float
    has_line_of_sight: bool
    can_shoot: bool
    in_preferred_range: bool
    preferred_min_range: float
    preferred_max_range: float

class Enemy():
    def __init__(self, game, level, player, pos, image, hp, speed, fire_cooldown, role):
        # базовые импорты
        self.game = game
        self.level = level
        self.player = player

        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.hp = hp
        self.speed = speed

        self.fire_cooldown = fire_cooldown
        self.time_since_shot = fire_cooldown

        self.active = False
        self.phase = None
        self.phase_timer = 0
        self.attack_behavior = None
        self.movement_behavior = None

        self.preferred_min_range = 0
        self.preferred_max_range = 0
        self.contact_damage = 1
        self.room_id = None
        self.role = role        

    # сбор контекста (позиция игрока, расстояние до игрока, линия взгляда, готовность к выстрелу)
    def build_context(self):
        enemy_center = pygame.Vector2(self.rect.center)
        player_center = pygame.Vector2(self.player.rect.center)

        offset_to_player = player_center - enemy_center
        distance_to_player = offset_to_player.length()

        if distance_to_player > 0:
            direction_to_player = offset_to_player.normalize()
            angle_to_player = direction_to_player.as_polar()[1]
        else:
            direction_to_player = pygame.Vector2()
            angle_to_player = 0.0

        has_line_of_sight = self.level.has_line_of_sight(
            self.rect.center,
            self.player.rect.center,
        )

        can_shoot = self.can_shoot()

        in_preferred_range = (
            self.preferred_min_range <= distance_to_player <= self.preferred_max_range
        )

        return EnemyContext(
            enemy_center=enemy_center,
            player_center=player_center,
            offset_to_player=offset_to_player,
            distance_to_player=distance_to_player,
            direction_to_player=direction_to_player,
            angle_to_player=angle_to_player,
            has_line_of_sight=has_line_of_sight,
            can_shoot=can_shoot,
            in_preferred_range=in_preferred_range,
            preferred_min_range=self.preferred_min_range,
            preferred_max_range=self.preferred_max_range,
        )

    def move_with_collision(self, move_vector, delta_time):
        if move_vector.length_squared() > 1:
            move_vector = move_vector.normalize()

        move_x = move_vector.x * self.speed * delta_time
        move_y = move_vector.y * self.speed * delta_time

        next_rect_x = self.rect.copy()
        next_rect_x.x += int(move_x)
        if not self.level.collides_with_wall(next_rect_x):
            self.rect.x = next_rect_x.x

        next_rect_y = self.rect.copy()
        next_rect_y.y += int(move_y)
        if not self.level.collides_with_wall(next_rect_y):
            self.rect.y = next_rect_y.y
        
    def update_fire_timer(self, delta_time):
        self.time_since_shot += delta_time

    def can_shoot(self):
        return self.time_since_shot >= self.fire_cooldown

    def reset_shot_timer(self):
        self.time_since_shot = 0

    def take_damage(self, amount):
        self.hp -= amount

    def is_dead(self):
        return self.hp <= 0

    def get_shot_origin(self):
        return self.rect.center

    def render(self, display, camera=None):
        if camera is None:
            display.blit(self.image, self.rect)
            return

        screen_rect = camera.apply_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, screen_rect.size)
        display.blit(scaled_image, screen_rect)
