import pygame

"----------------------------------------button----------------------------------------"


# A simple button class with text, color, and callback function.
class button_widget:
  # Initialize button properties and resources.
  def __init__(self, rect, text, font, callback,
               bg_color=(66, 133, 244), fg_color=(255, 255, 255),
               hover_bg=None, bg_image_path=None):

    self.rect = rect
    self.callback = callback
    self.text = text
    self.font = font
    self.bg_color = bg_color
    self.fg_color = fg_color
    self.hover_bg = hover_bg
    self.hover = False

    # Base button image: only for creating the mask; actual display uses bg_image.
    base_image = pygame.image.load("ui/resource/button.png").convert_alpha()
    base_image = pygame.transform.scale(base_image, (rect.width, rect.height))

    # Create a mask from the image to ignore transparent pixels.
    self.mask = pygame.mask.from_surface(base_image)

    # Create a highlight overlay with the same shape as the button.
    # Mask pixels with value 1 are light white; others are transparent.
    self.hover_overlay = self.mask.to_surface(
      setcolor=(255, 255, 255, 60),
      unsetcolor=(0, 0, 0, 0)
    ).convert_alpha()  # [1]

    # Load the background image and scale it to the button size.
    self.bg_image = None
    if bg_image_path is not None:
      img = pygame.image.load(bg_image_path).convert_alpha()
      self.bg_image = pygame.transform.smoothscale(
        img, (rect.width, rect.height)
      )

    # Render the button text and center it inside the button rect.
    self.text_surf = self.font.render(self.text, True, (255, 255, 255))
    self.text_rect = self.text_surf.get_rect(center=self.rect.center)

  # Update the button text.
  def set_text(self, new_text):
    self.text = new_text

  # Handle hover and click events for this button.
  def handle_event(self, event):
    if event.type == pygame.MOUSEMOTION:
      # Check if the mouse is inside the button rect.
      if self.rect.collidepoint(event.pos):
        local_x = event.pos[0] - self.rect.x
        local_y = event.pos[1] - self.rect.y
        if 0 <= local_x < self.rect.width and 0 <= local_y < self.rect.height:
          # Only count hover on non-transparent pixels of the mask.
          self.hover = self.mask.get_at((local_x, local_y)) == 1
        else:
          self.hover = False
      else:
        self.hover = False

    elif event.type == pygame.MOUSEBUTTONDOWN:
      # Check click inside button rect first.
      if self.rect.collidepoint(event.pos):
        local_x = event.pos[0] - self.rect.x
        local_y = event.pos[1] - self.rect.y
        # Only trigger click on non-transparent pixels.
        if 0 <= local_x < self.rect.width and 0 <= local_y < self.rect.height:
          if self.mask.get_at((local_x, local_y)) == 1:
            # Left button: 1, right button: 3.
            if event.button == 1:
              if callable(self.callback):
                self.callback("left")
            elif event.button == 3:
              if callable(self.callback):
                self.callback("right")

  # Draw the button (background, highlight, and text).
  def draw(self, screen):
    # Draw the button background (image or colored rect).
    if self.bg_image:
      screen.blit(self.bg_image, self.rect)
    else:
      bg = self.hover_bg if (self.hover and self.hover_bg is not None) else self.bg_color
      pygame.draw.rect(screen, bg, self.rect, border_radius=10)

    # Draw the highlight overlay only when hovered.
    if self.hover:
      screen.blit(self.hover_overlay, self.rect)

    # Render and draw the button text centered in the rect.
    txt_surf = self.font.render(self.text, True, self.fg_color)
    txt_rect = txt_surf.get_rect(center=self.rect.center)
    screen.blit(txt_surf, txt_rect)


"----------------------------------------Card----------------------------------------"


# Card widget with front/back images, hover, selection, and move animation.
class card_widget:
  # Initialize a card with rect, images, and state.
  def __init__(self, rect, front_image_path, back_image_path, face_up=True, selectable=True, hover_enabled=True):
    self.rect = rect
    self.face_up = face_up
    self.front_image = pygame.image.load(front_image_path)
    self.front_image = pygame.transform.scale(self.front_image, (rect.width, rect.height))
    self.back_image = pygame.image.load(back_image_path)
    self.back_image = pygame.transform.scale(self.back_image, (rect.width, rect.height))
    self.hovered = False
    self.moved_to_center = False
    # Animation control state.
    self.animating = False
    self.animation_time = 0
    self.animation_duration = 0
    self.start_pos = None
    self.end_pos = None
    # Selection and hover options.
    self.selectable = selectable
    self.hover_enabled = hover_enabled
    self.selected = False
    self.hovered = False

  # Set whether the card shows front or back.
  def set_face_up(self, face_up):
    self.face_up = face_up

  # Handle hover and click events for this card.
  def handle_event(self, event, screen_width, screen_height):
    # Ignore all events if this card is not selectable.
    if not self.selectable:
      return

    # Update hover state on mouse move.
    if event.type == pygame.MOUSEMOTION:
      self.hovered = self.rect.collidepoint(event.pos)

    # Left click toggles selection.
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      if self.rect.collidepoint(event.pos):
        self.selected = not self.selected

  # Draw the card (with hover / selection lift).
  def draw(self, screen):
    # Choose front or back image based on face_up.
    img = self.front_image if self.face_up else self.back_image

    offset_y = 0

    # Slight lift on hover (if not selected).
    if self.hovered and not self.selected:
      offset_y = -30

    # Selected cards stay lifted.
    if self.selected:
      offset_y = -30

    rect_to_draw = self.rect.move(0, offset_y)

    # Draw the card image at its (possibly lifted) position.
    screen.blit(img, rect_to_draw)  # [2]

  # Start a move animation from start_pos to end_pos.
  def start_animation(self, start_pos, end_pos, duration=0.3):

    self.start_pos = start_pos
    self.end_pos = end_pos
    self.animation_duration = duration
    self.animation_time = 0
    self.animating = True

    # Set initial position.
    self.rect.topleft = start_pos

  # Update the animation each frame based on dt.
  def update(self, dt):
    # Skip if no animation is running.
    if not self.animating:
      return

    self.animation_time += dt

    # Compute progress ratio (0.0 ~ 1.0).
    progress = min(self.animation_time / self.animation_duration, 1.0)

    # Linear interpolation between start_pos and end_pos.
    x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
    y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

    self.rect.topleft = (x, y)

    # Stop animation when finished.
    if progress >= 1.0:
      self.animating = False  # [3]


"----------------------------------------Avatar&logo----------------------------------------"


# Avatar / logo widget for displaying an image at a fixed rect.
class logo():
  # Initialize the logo with its rect and image.
  def __init__(self, rect, image_path):
    self.rect = rect
    self.image = pygame.image.load(image_path)
    self.image = pygame.transform.scale(self.image, (rect.width, rect.height))

    # Optional hover state.
    self.hover = False

  # Draw the logo image at its rect.
  def draw(self, screen):
    screen.blit(self.image, self.rect)


"----------------------------------------Background----------------------------------------"


# Full-screen background widget.
class background_widget:
  # Initialize the background with screen size and image.
  def __init__(self, screen_size, image_path):
    self.width, self.height = screen_size

    # Load and scale the background image to screen size.
    self.image = pygame.image.load(image_path)
    self.image = pygame.transform.scale(self.image, screen_size)

  # Draw the background at the top-left corner.
  def draw(self, screen):
    screen.blit(self.image, (0, 0))


"----------------------------------------Winner interface----------------------------------------"


# Winner overlay widget for showing a centered message.
class winner:
  def __init__(self, screen_size, text, font):
    self.width, self.height = screen_size
    self.text = text
    self.font = font

    # Pre-render the winner text.
    self.text_surf = self.font.render(self.text, True, (255, 255, 255))
    self.text_rect = self.text_surf.get_rect(
      center=(self.width // 2, self.height // 2)
    )

  # Draw dark overlay and winner text in the center.
  def draw(self, screen):
    # Draw a semi-transparent dark overlay.
    overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Draw the winner text in the center.
    screen.blit(self.text_surf, self.text_rect)


"----------------------------------------Reference----------------------------------------"
"""
[1]mask - pygame documentation
https://scuba.cs.uchicago.edu/pygame/ref/mask.html

[2]Hover Effect in pygame
https://stackoverflow.com/questions/55837520/hover-effect-in-pygame

[3]How can I apply some animation for list of images in pygame?
https://stackoverflow.com/questions/73129963/how-can-i-apply-some-animation-for-list-of-images-in-pygame

The hovering and animation effects were achieved by using part of the code structure and changing the parameters.
"""