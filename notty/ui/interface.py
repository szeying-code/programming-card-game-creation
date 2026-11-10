import pygame, sys, random
from notty.ui.layout import (
    rect_father_layout,
    rect_son_layout_ai,
    rect_son_layout_table,
    rect_son_layout_player,
    rect_son_layout_status_header,
    rect_son_layout_status_footer,
    card_layout,
)
from notty.ui.widgets import button_widget, card_widget, background_widget
from notty.element_action.game import GameEngine

"----------------------------------------Main UI class of the game----------------------------------------"
class GameInterfaceUI:

  def __init__(self, screen):
    self.screen = screen
    self.screen_width = screen.get_width()
    self.screen_height = screen.get_height()
    self.animating_cards = []  # Cards currently flying
    # Load background
    self.background = background_widget(
      (self.screen_width, self.screen_height),
      "ui/resource/background.png"
    )

    # Avatar images
    self.logo_ai1 = pygame.image.load("ui/resource/AI1.png").convert_alpha()
    self.logo_ai2 = pygame.image.load("ui/resource/AI2.png").convert_alpha()
    self.logo_player = pygame.image.load("ui/resource/user.png").convert_alpha()

    # Mask for NPC + hover highlight effect
    self.ai1_mask = pygame.mask.from_surface(self.logo_ai1)
    self.ai2_mask = pygame.mask.from_surface(self.logo_ai2)

    # Generate semi-transparent white highlight overlay for hover effects
    self.ai1_hover_overlay = self.ai1_mask.to_surface(
      setcolor=(255, 255, 255, 80),
      unsetcolor=(0, 0, 0, 0)
    ).convert_alpha()

    self.ai2_hover_overlay = self.ai2_mask.to_surface(
      setcolor=(255, 255, 255, 80),
      unsetcolor=(0, 0, 0, 0)
    ).convert_alpha()

    # Layout
    # parent layout
    self.father_layout = rect_father_layout(screen)
    # NPC
    self.ai_layout = rect_son_layout_ai(self.father_layout)
    # Table
    self.table_layout = rect_son_layout_table(self.father_layout)
    #Player
    self.player_layouts = rect_son_layout_player(self.father_layout)
    #Status_bar
    self.status_layout = rect_son_layout_status_header(self.father_layout)
    #footer
    self.footer_layout = rect_son_layout_status_footer(self.father_layout)
    #Btn in the footer
    self.player_buttons_layout = rect_son_layout_player(self.father_layout)['player_buttons']
    # Card
    self.card_layout = card_layout()

    # Initialize the game engine
    self.engine = GameEngine(num_ai=1)

    # UI font settings
    self.font = pygame.font.SysFont("arial", 18, bold=True)

    # Lists of card widgets for player, NPCs, deck, and discard pile
    self.player_card_widgets = []
    self.ai_card_widgets = []
    self.deck_card_widgets = []
    self.discard_card_widgets = []
    self._updating_widgets = False

    # Status bar main message (Middle)
    self.status_message = "Notty"
    # Current player's name (Right)
    self.current_player_name = self.engine.current_player

    # player has already taken an action?
    self.player_has_done_action = False

    # Discard pile temporary display timer
    self.discard_show_until = None

    # NPC count
    self.ai_count = 1

    # Waiting for the player to click an NPC avatar to steal from
    self.waiting_steal_target = False
    # Clickable rect list for NPC avatars
    self.ai_avatar_click_rects = []  # [NPC1_rect, NPC2_rect...]

    # Current mouse position
    self.mouse_pos = (0, 0)

    # Create all UI buttons
    self.create_buttons()
    # Initialize card widgets
    self.update_card_widgets()

    # Old steal target variable
    self.steal_target = None
    self.steal_target = 1

    # Winner popup related
    self.popup_animation_scale = 1.0 # Text scale factor
    self.popup_animation_speed = 0.01# Speed of the scale animation
    self.popup_text_direction = 1# Scale direction
    self.winner_popup_active = False# Whether the winner popup is currently active
    self.winner_name = None# Winner's name

    # Winner avatar lookup table: winner names -> images
    self.winner_avatars = {
      "player": self.logo_player,
      "ai_1": self.logo_ai1,
      "ai_2": self.logo_ai2,
  }

    # Initialize the audio mixer and load the winner sound.
    # If there is no audio device or the file is missing, the game still runs without sound.
    try:
      pygame.mixer.init()
      self.win_sound = pygame.mixer.Sound("ui/resource/winnersound.mp3")
    except (pygame.error, FileNotFoundError):
      pass

  # Display winner message
  def show_winner_message(self, winner_name):
    if winner_name == "You":
      self.status_message = f"You are the winner! Congratulations!"
    else:
      self.status_message = f"{winner_name} is the winner! Better luck next time!"

  # Unified function to check whether the game is over
  def check_game_over(self, result=None):
    if result and result.get("winner"): # If result contains a winner name, handle this first
      winner = result["winner"]
      self.show_winner_message(winner)
      return True

    if self.engine.winner:# Otherwise check engine's internal winner attribute
      winner = self.engine.winner
      self.show_winner_message(winner)
      return True

    return False

  # Activate victory popup (Only trigger once)
  def show_winner_popup(self, winner_name):
    if not self.winner_popup_active:
      self.winner_popup_active = True
      self.winner_name = winner_name
      self.popup_animation_scale = 1.0# Reset animation scale
      self.popup_text_direction = 1# Reset animation direction

      # Play victory sound
      if hasattr(self, "win_sound"):
        self.win_sound.play()

  # If popup is not active, skip drawing
  def draw_winner_popup(self):
    if not self.winner_popup_active:
      return

    avatar_key = "ai1" # Default avatar key

    # Draw full-screen semi-transparent black overlay
    overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    self.screen.blit(overlay, (0, 0))

    # Breathing animation for the victory text
    self.popup_animation_scale += self.popup_text_direction * self.popup_animation_speed
    if self.popup_animation_scale > 1.3:
      self.popup_text_direction = -1
    elif self.popup_animation_scale < 0.8:
      self.popup_text_direction = 1

    # Dynamic font size
    font_size = int(150 * self.popup_animation_scale)
    font = pygame.font.SysFont("arial", font_size, bold=True)

    # Process winner name -> key
    name = self.winner_name.lower().replace(" ", "").replace("_", "")

    # Player win vs NPC win text
    if name in ("you", "player"):
      text = "YOU WIN!"
      color = (255, 240, 0)
      avatar_key = "player"
    else:
      text = f"{self.winner_name.upper()} WINS!"
      color = (255, 80, 80)
      if "npc" in name:
        name = name.replace("npc", "ai")
      avatar_key = name

    # Draw victory title text
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 180))
    self.screen.blit(rendered, rect)

    # Get winner avatar from lookup table
    avatar = None
    for key, img in self.winner_avatars.items():
      if key.replace("_", "").lower() == avatar_key.lower():
        avatar = img
        break

    # Use NPC1 image if no avatar is matched
    if avatar is None:
      avatar = self.logo_ai1

    # Scale avatar image so the longest side becomes 400
    aw, ah = avatar.get_size()
    scale = 400 / max(aw, ah)
    new_size = (int(aw * scale), int(ah * scale))
    avatar_scaled = pygame.transform.smoothscale(avatar, new_size)

    # Avatar display position
    avatar_rect = avatar_scaled.get_rect(
      center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 160)
    )

    # Draw avatar
    self.screen.blit(avatar_scaled, avatar_rect)

  # Get layout rects for status bar (left: deck count / center: message / right: current player)
  def draw_status_bar(self, surface):
    rects = self.status_layout
    card_rect = rects['status_card_num']
    alarm_rect = rects['status_main_alarm']
    player_rect = rects['status_player']

    # Left side: display remaining deck count
    deck_count = self.engine.deck_count()
    left_text = f"Remaining in the deck: {deck_count}"
    left_surf = self.font.render(left_text, True, (255, 255, 255))
    left_rect = left_surf.get_rect(center=card_rect.center)
    surface.blit(left_surf, left_rect)

    # Center: display main message
    mid_text = self.status_message
    mid_surf = self.font.render(mid_text, True, (255, 215, 0))
    mid_rect = mid_surf.get_rect(center=alarm_rect.center)
    surface.blit(mid_surf, mid_rect)

    # Right side: display whose turn it is (player or NPC)
    player_text = f"Current player: {self.current_player_name}"
    player_surf = self.font.render(player_text, True, (255, 255, 255))
    player_text_rect = player_surf.get_rect(center=player_rect.center)
    surface.blit(player_surf, player_text_rect)

  # Update status message from result dict; fallback to default -> Notty
  def update_status_bar_from_result(self, result):
    msg = result.get("message")
    if msg:
      self.status_message = msg
    else:
      self.status_message = "Notty"

    # Update current player name so the top-right display stays correct
    self.current_player_name = self.engine.current_player

  #Player info/image
  # Get original image width and height
  def _blit_scaled_center(self, surface, image, target_rect):
    iw, ih = image.get_size()
    if iw == 0 or ih == 0:
      return target_rect ## Prevent errors if the image has invalid size

    # Calculate scale factor so the image fits inside target_rect
    scale = min(target_rect.width / iw, target_rect.height / ih)
    new_size = (int(iw * scale), int(ih * scale))

    # Scale the image to new size
    img_scaled = pygame.transform.smoothscale(image, new_size)

    # Center the scaled image inside the target rectangle
    dst_rect = img_scaled.get_rect(center=target_rect.center)

    # Draw the scaled image
    surface.blit(img_scaled, dst_rect)
    return dst_rect

  def draw_avatars(self, surface):
    num_ai = self.engine.num_ai # Get number of NPCs (1 or 2)
    mouse_pos = self.mouse_pos # Current logic mouse position for hover detection

    # Ensure click-rect list matches NPC count
    if len(self.ai_avatar_click_rects) < num_ai:
      self.ai_avatar_click_rects = [None] * num_ai

    # ---------------- NPC 1 ----------------
    ai1_img_rect = self.ai_layout["ai_info_1"]["ai_info_1_image"]
    ai1_text_rect = self.ai_layout["ai_info_1"]["ai_info_1_text"]

    # Draw NPC1 avatar
    dst_rect1 = self._blit_scaled_center(surface, self.logo_ai1, ai1_img_rect)
    self.ai_avatar_click_rects[0] = dst_rect1
    # Update clickable rect

    # If in steal-target mode and mouse hovers → draw highlight
    if self.waiting_steal_target and dst_rect1.collidepoint(mouse_pos):
      overlay1 = pygame.transform.smoothscale(
        self.ai1_hover_overlay, dst_rect1.size
      )
      surface.blit(overlay1, dst_rect1.topleft)

    # Draw NPC1 name label
    ai1_label = self.font.render("NPC 1", True, (255, 255, 255))
    ai1_label_rect = ai1_label.get_rect(center=ai1_text_rect.center)
    surface.blit(ai1_label, ai1_label_rect)

    # ---------------- NPC 2 ----------------
    if num_ai >= 2:
      ai2_img_rect = self.ai_layout["ai_info_2"]["ai_info_2_image"]
      ai2_text_rect = self.ai_layout["ai_info_2"]["ai_info_2_text"]

      # Draw NPC2 avatar
      dst_rect2 = self._blit_scaled_center(surface, self.logo_ai2, ai2_img_rect)

      # Update clickable rect for NPC2
      if len(self.ai_avatar_click_rects) < 2:
        self.ai_avatar_click_rects.append(dst_rect2)
      else:
        self.ai_avatar_click_rects[1] = dst_rect2

      # Hover highlight
      if self.waiting_steal_target and dst_rect2.collidepoint(mouse_pos):
        overlay2 = pygame.transform.smoothscale(
          self.ai2_hover_overlay, dst_rect2.size
        )
        surface.blit(overlay2, dst_rect2.topleft)
      # Draw NPC2 name label
      ai2_label = self.font.render("NPC 2", True, (255, 255, 255))
      ai2_label_rect = ai2_label.get_rect(center=ai2_text_rect.center)
      surface.blit(ai2_label, ai2_label_rect)

    # ---------------- Player ----------------
    player_img_rect = self.player_layouts["player_info"]["player_info_image"]
    player_text_rect = self.player_layouts["player_info"]["player_info_text"]

    # Draw player avatar
    self._blit_scaled_center(surface, self.logo_player, player_img_rect)

    # Draw Player label
    player_label = self.font.render("Player", True, (255, 255, 255))
    player_label_rect = player_label.get_rect(center=player_text_rect.center)
    surface.blit(player_label, player_label_rect)

  # ---------- Button ----------

  def create_buttons(self):
    self.buttons = [] # Create button lists
    self.player_buttons = [] # Player action buttons

    font = self.font
    foot = self.footer_layout # Footer layout for bottom buttons

    # NPC number toggle button
    self.buttons.append(
      button_widget(
        foot['footer_btn1'], # Button rect
        "3 People" if self.ai_count == 1 else "2 People", # Initial text
        font,
        self.ai_num, # Callback: switch NPC count
        bg_image_path="ui/resource/button.png" # Button background image
      )
    )

    # Difficulty switch button
    self.buttons.append(
      button_widget(
        foot['footer_btn2'],
        "Hard",
        font,
        self.on_difficulty,
        bg_image_path="ui/resource/button.png"
      )
    )

    # Restart
    self.buttons.append(
      button_widget(
        foot['footer_btn3'],
        "Restart",
        font,
        self.on_restart_button_click,
        bg_image_path="ui/resource/button_long.png"
      )
    )

    # Play For Me
    self.buttons.append(
      button_widget(
        foot['footer_btn4'],
        "Play For Me",
        font,
        self.on_play_for_me,
        bg_image_path="ui/resource/button.png"
      )
    )

    # Quit
    self.buttons.append(
      button_widget(
        foot['footer_btn5'],
        "Quit",
        font,
        self.on_quit,
        bg_image_path="ui/resource/button.png"
      )
    )

    pb = self.player_buttons_layout # Layout region for player's right-side buttons

    # Draw x3
    self.player_buttons.append(
      button_widget(pb['short_button1'],
                    "Draw", font,
                    self.on_draw_three,
                    bg_image_path="ui/resource/button.png")
    )

    # Enter steal mode
    self.player_buttons.append(
      button_widget(
        pb['short_button2'],
        "Steal",
        font,
        self.on_steal,
        bg_image_path="ui/resource/button.png"
      )
    )

    # Draw & Discard
    self.player_buttons.append(
      button_widget(pb['short_button3'],
                    "Draw & Discard", font,
                    self.on_draw_discard,
                    bg_image_path="ui/resource/button.png")
    )

    # Group Out
    self.player_buttons.append(
      button_widget(pb['short_button4'],
                    "Group Out", font,
                    self.on_discard_group,
                    bg_image_path="ui/resource/button.png")
    )

    # End Turn
    self.player_buttons.append(
      button_widget(pb['long_button'],
                    "Pass", font,
                    self.on_end_turn,
                    bg_image_path="ui/resource/button.png")
    )

  # ---------- Button logic ----------
  # Save result to last_action_result and update status bar
  def _notify(self, result):
    self.last_action_result = result
    self.update_status_bar_from_result(result)

  # Auto-play one turn for the player
  def on_play_for_me(self, *args, **kwargs):
    result = self.engine.player_auto_play()

    self._notify(result)# Update status bar
    if self.check_game_over(result):
      return# Stop if game ended

    self.update_card_widgets()# Refresh UI

  # Reset the whole game
  def on_restart_button_click(self, mouse_btn, *args, **kwargs):
    self.engine.reset_game()
    # Notify: Game restarted
    self._notify({"message": "Game restarted."})
    # Refresh UI
    self.update_card_widgets()

  # Quit game on left-click
  def on_quit(self, mouse_btn, *args, **kwargs):
    if mouse_btn == "left":
      pygame.quit()
      sys.exit()

  # Toggle game difficulty (Hard or Easy)
  def on_difficulty(self, mouse_btn=None, *args, **kwargs):
    btn = self.buttons[1]# Second button is difficulty button
    if btn.text == "Hard":
      btn.set_text("Easy")# Change text to Easy
      self.engine.set_difficulty("hard")
      self._notify({"message": "Difficulty set to Hard."})
    elif btn.text == "Easy":
      btn.set_text("Hard")# But actual logic uses "hard"
      self.engine.set_difficulty("easy")
      self._notify({"message": "Difficulty set to Easy."})

    # Refresh UI
    self.update_card_widgets()

  # Toggle NPC count
  def ai_num(self, *args, **kwargs):
    self.ai_count = 2 if self.ai_count == 1 else 1
    # Recreate engine with new NPC count
    self.engine = GameEngine(num_ai=self.ai_count)
    # Clear selected card cache
    self.selected_cards = []
    # Reset has done action flag
    self.player_has_done_action = False
    # Recreate all buttons
    self.create_buttons()
    # Refresh card widgets
    self.update_card_widgets()
    # Show message
    self._notify({"message": f"NPC count changed to {self.ai_count}."})

  # ---------- Draw up to 3 ----------

  def on_draw_three(self, *args, **kwargs):
    # Get player object
    player = self.engine.players[0]
    # Record hand size before drawing
    old_hand_len = len(player.hand)

    # Get top deck card position
    if self.deck_card_widgets:
      start_pos = self.deck_card_widgets[-1].rect.topleft
    else:
      start_pos = None# No animation when deck empty

    # Perform "draw up to 3"
    result = self.engine.player_draw_up_to_three()
    # Mark action done
    self.player_has_done_action = True
    # Update status bar
    self._notify(result)

    # If drawing causes victory → show winner popup
    if self.check_game_over(result):
      return

    # Refresh UI
    self.update_card_widgets()

    # No animation when deck empty
    if start_pos is None:
      return

    new_hand_len = len(self.engine.players[0].hand)
    # Number of newly added cards
    num_new = new_hand_len - old_hand_len
    if num_new <= 0:
      return# No cards drawn → no animation

    # Get newly drawn card widgets
    new_widgets = self.player_card_widgets[new_hand_len - num_new:new_hand_len]

    # Start flying animation for each new card
    for w in new_widgets:
      end_pos = w.rect.topleft# Target position of card
      back = "ui/resource/card/back.png"
      flying = card_widget(
        w.rect.copy(),
        back,# Show card back in animation
        back,
        face_up=False,
        selectable=False,
        hover_enabled=False,
      )
      # Fly from deck to player's hand
      flying.start_animation(start_pos, end_pos, duration=0.35)
      # Add to animation queue
      self.animating_cards.append(flying)

  # ---------- Card Stealing: NPC - > Player (Flying Card) ----------

  def _play_steal_animation(self, target_index, result):

    # No animation when steal fails
    if not result.get("ok"):
      return

    # Snapshot of player hand after stealing
    snapshot_after = self.engine.ui_snapshot()
    player_hand_after = snapshot_after["player_hand"]
    new_len = len(player_hand_after)

    if new_len == 0:
      return

    ai_hands_now = snapshot_after["ai_hands"]

    # Ensure NPC index valid
    if target_index - 1 >= len(ai_hands_now):
      return

    # Compute NPC card index range inside ai_card_widgets
    start_index = 0
    for i in range(target_index - 1):
      start_index += len(ai_hands_now[i])

    ai_len = len(ai_hands_now[target_index - 1])

    if ai_len == 0:
      return

    npc_widgets = self.ai_card_widgets[start_index:start_index + ai_len]

    # Use last card in NPC hand as animation start point
    start_widget = npc_widgets[-1]
    start_pos = start_widget.rect.topleft

    # Player’s newest card is animation end point
    new_widget = self.player_card_widgets[-1]
    end_pos = new_widget.rect.topleft

    stolen_card = player_hand_after[-1]

    front = f"ui/resource/card/{stolen_card.colour}/{stolen_card.number}.png"
    back = "ui/resource/card/back.png"

    flying = card_widget(
      new_widget.rect.copy(),
      front,
      back,
      face_up=True,
      selectable=False,
      hover_enabled=False,
    )

    # NPC → Player flying animation
    flying.start_animation(start_pos, end_pos, duration=0.4)

    # Add to animation queue
    self.animating_cards.append(flying)

  def on_steal(self, mouse_btn="left", *args, **kwargs):

    # Prevent stealing more than once each turn
    if self.engine.used_steal:
      self._notify({"ok": False, "message": "You already used the steal action this turn."})
      return

    # Can only steal on player's turn
    if self.engine.current_player != self.engine.players[0].name:
      self._notify({"ok": False, "message": "It is not your turn."})
      return

    # Enter "choose NPC by clicking avatar" mode
    self.waiting_steal_target = True
    self.status_message = "Click an NPC avatar to steal a card."

    # ---------- Draw & Discard: player -> discard pile (with flying animation) ----------
    # ---------- Draw & Discard consists of two steps ----------
  def on_draw_discard(self, *args, **kwargs):

    # -------- Player has NOT drawn yet → draw 1 card and enter “waiting for discard” mode --------
    if not getattr(self.engine, "pending_discard_required", False):
      player = self.engine.players[0]
      old_hand_len = len(player.hand)

      # Deck top position (animation start point)
      if self.deck_card_widgets:
        start_pos = self.deck_card_widgets[-1].rect.topleft
      else:
        start_pos = None

      result = self.engine.player_draw_one_for_discard()
      self.player_has_done_action = True
      self._notify(result)

      # Stop immediately if game ends as a result of the draw
      if self.check_game_over(result):
        return

      # Refresh hand UI after drawing
      self.update_card_widgets()

      # If drawing failed or no card was drawn, stop
      if not result.get("ok") or not result.get("drawn"):
        return

      # Flying animation: deck → player's new card
      if start_pos is not None:
        new_hand_len = len(self.engine.players[0].hand)
        if new_hand_len > old_hand_len:
          new_widget = self.player_card_widgets[-1]  # the newly drawn card
          end_pos = new_widget.rect.topleft

          back = "ui/resource/card/back.png"
          flying = card_widget(
            new_widget.rect.copy(),
            back,
            back,
            face_up=False,
            selectable=False,
            hover_enabled=False,
          )
          flying.start_animation(start_pos, end_pos, duration=0.35)
          self.animating_cards.append(flying)

      return  # End of Step 1

    # -------- Already drew 1 card → must select exactly one card to discard --------
    idx = self.get_selected_player_card_indices()

    if len(idx) == 0:
      self._notify({"ok": False, "message": "Please select 1 card to discard."})
      return
    if len(idx) > 1:
      self._notify({"ok": False, "message": "Please select ONLY 1 card for discard."})
      return

    discard_index = idx[0]

    # Animation start point: position of the selected card
    if discard_index >= len(self.player_card_widgets):
      self._notify({"ok": False, "message": "Invalid selected card index."})
      return

    start_widget = self.player_card_widgets[discard_index]
    start_pos = start_widget.rect.topleft

    # Record the card object to be discarded (hand will change after calling engine)
    player_hand = self.engine.players[0].hand
    if discard_index >= len(player_hand):
      self._notify({"ok": False, "message": "Invalid selected card index."})
      return
    discard_card_obj = player_hand[discard_index]

    # Perform the discard step
    result = self.engine.player_discard_one_after_draw(discard_index)
    self.player_has_done_action = True
    self._notify(result)

    # Stop if game ends
    if self.check_game_over(result):
      return

    has_discard = result.get("ok") and result.get("discarded") is not None
    if has_discard:
      self.schedule_discard_recycle()

    # Refresh UI (hand & discard pile)
    self.update_card_widgets()

    # Flying animation: player → discard pile
    if has_discard and self.discard_card_widgets:
      end_rect = self.discard_card_widgets[-1].rect
      end_pos = end_rect.topleft

      front = f"ui/resource/card/{discard_card_obj.colour}/{discard_card_obj.number}.png"
      back = "ui/resource/card/back.png"

      flying = card_widget(
        end_rect,
        front,
        back,
        face_up=True,
        selectable=False,
        hover_enabled=False
      )
      flying.start_animation(start_pos, end_pos, duration=0.35)
      self.animating_cards.append(flying)

    # -------- Step2：One card has already been drawn → You must select one card to discard --------
    idx = self.get_selected_player_card_indices()

    if len(idx) == 0:
      self._notify({"ok": False, "message": "Please select 1 card to discard."})
      return
    if len(idx) > 1:
      self._notify({"ok": False, "message": "Please select ONLY 1 card for discard."})
      return

    discard_index = idx[0]

    # Starting point: the position of the currently selected card
    if discard_index >= len(self.player_card_widgets):
      self._notify({"ok": False, "message": "Invalid selected card index."})
      return

    start_widget = self.player_card_widgets[discard_index]
    start_pos = start_widget.rect.topleft

    # Record the card objects to be lost
    player_hand = self.engine.players[0].hand
    if discard_index >= len(player_hand):
      self._notify({"ok": False, "message": "Invalid selected card index."})
      return
    discard_card_obj = player_hand[discard_index]

    # Invoke the second step logic: Discard 1 sheet
    result = self.engine.player_discard_one_after_draw(discard_index)
    self.player_has_done_action = True
    self._notify(result)

    if self.check_game_over(result):
      return

    has_discard = result.get("ok") and result.get("discarded") is not None
    if has_discard:
      self.schedule_discard_recycle()

    # Update the UI (hand & discard pile)
    self.update_card_widgets()

    # Create a discard animation: Player → Discard pile
    if has_discard and self.discard_card_widgets:
      end_rect = self.discard_card_widgets[-1].rect
      end_pos = end_rect.topleft

      front = f"ui/resource/card/{discard_card_obj.colour}/{discard_card_obj.number}.png"
      back = "ui/resource/card/back.png"

      flying = card_widget(
        end_rect,
        front,
        back,
        face_up=True,
        selectable=False,
        hover_enabled=False
      )
      flying.start_animation(start_pos, end_pos, duration=0.35)
      self.animating_cards.append(flying)


  # ---------- Group discard: Multiple cards - Player -> Discard pile (Flying cards) ----------#

  def on_discard_group(self, *args, **kwargs):
    hand = self.engine.players[0].hand
    selected_indices = self.get_selected_player_card_indices()

    if len(hand) < 3:
      self._notify({"ok": False, "message": "Not enough cards"})
      return

    if len(selected_indices) < 3:
      self._notify({"ok": False, "message": "Please select at least 3 cards as a group."})
      return

    start_positions = [self.player_card_widgets[i].rect.topleft for i in selected_indices]
    discard_cards = [hand[i] for i in selected_indices]
    group_cards = discard_cards[:]

    result = self.engine.player_discard_group(group_cards)
    self.player_has_done_action = True
    self._notify(result)

    if self.check_game_over(result):
      return

    if result.get("ok"):
      self.schedule_discard_recycle()

    self.update_card_widgets()

    if result.get("ok"):
      if self.discard_card_widgets:
        base_rect = self.discard_card_widgets[-1].rect
      else:
        base_rect = self.player_card_widgets[0].rect

      for card_obj, start_pos in zip(discard_cards, start_positions):
        front = f"ui/resource/card/{card_obj.colour}/{card_obj.number}.png"
        back = "ui/resource/card/back.png"
        target_rect = base_rect.copy()
        end_pos = target_rect.topleft

        flying = card_widget(
          target_rect,
          front,
          back,
          face_up=True,
          selectable=False,
          hover_enabled=False
        )
        flying.start_animation(start_pos, end_pos, duration=0.4)
        self.animating_cards.append(flying)

  def on_end_turn(self, *args, **kwargs):
    result = self.engine.end_player_turn()
    self._notify(result)

    if self.check_game_over(result):
      return

    if result.get("ok"):
      now = pygame.time.get_ticks()
      self.engine.ai_wait_until = now + 1200
      self.engine._pending_ai_phase = True

    self.player_has_done_action = False
    self.update_card_widgets()

  # ---------- Select card ----------#

  def get_selected_player_card_indices(self):
    indices = []
    for i, w in enumerate(self.player_card_widgets):
      if w.selected:
        indices.append(i)
    return indices

  # ---------- discard action ----------#

  def schedule_discard_recycle(self):
    if self.engine.discard_pile:
      now = pygame.time.get_ticks()
      #1 second
      self.discard_show_until = now + 1000

  # ---------- cards ----------#

  def update_card_widgets(self):
    snapshot = self.engine.ui_snapshot()

    # Calculate the size first
    self.card_layout.layout_ai(
      self.ai_layout["ai_cards_1"],
      len(snapshot["ai_hands"][0]) if snapshot["ai_hands"] else 4
    )

    # player cards
    self.player_card_widgets = []
    player_hand = snapshot["player_hand"]
    area = self.player_layouts["player_cards"]
    rects = self.card_layout.card_layout_player(area, len(player_hand))

    for i, card in enumerate(player_hand):
      r = rects[i]
      front = f"ui/resource/card/{card.colour}/{card.number}.png"
      back = "ui/resource/card/back.png"
      widget = card_widget(r, front, back, face_up=True, selectable=True, hover_enabled=True)
      self.player_card_widgets.append(widget)

    # AI cards
    self.ai_card_widgets = []
    ai_hands = snapshot["ai_hands"]
    ai_areas = [
      self.ai_layout["ai_cards_1"],
      self.ai_layout["ai_cards_2"]
    ]

    for ai_index, hand in enumerate(ai_hands):
      area = ai_areas[ai_index]
      if ai_index == 0:
        # AI1 → arrange from left
        rects = self.card_layout.layout_ai(area, len(hand), align="left")
      else:
        # AI2 → arrange from right
        rects = self.card_layout.layout_ai(area, len(hand), align="right")

      for i, card in enumerate(hand):
        r = rects[i]
        front = f"ui/resource/card/{card.colour}/{card.number}.png"
        back = "ui/resource/card/back.png"
        widget = card_widget(r, front, back, face_up=True, selectable=False, hover_enabled=False)
        self.ai_card_widgets.append(widget)

    # deck of cards
    self.deck_card_widgets = []
    deck_cards = snapshot["deck_cards"]
    deck_area = self.table_layout["deck"]
    rects = self.card_layout.card_layout_desk(deck_area, len(deck_cards))

    for i, r in enumerate(rects):
      card = deck_cards[i]
      front = f"ui/resource/card/{card.colour}/{card.number}.png"
      back = "ui/resource/card/back.png"
      widget = card_widget(
        r,
        front,
        back,
        face_up=False,
        selectable=False,
        hover_enabled=False
      )
      self.deck_card_widgets.append(widget)

    # give up cards
    self.discard_card_widgets = []
    discard_cards = snapshot["discard_pile"]
    discard_area = self.table_layout["discard"]
    rects = self.card_layout.card_layout_discard(discard_area, len(discard_cards))

    for i, card in enumerate(discard_cards[:len(rects)]):
      r = rects[i]
      front = f"ui/resource/card/{card.colour}/{card.number}.png"
      back = "ui/resource/card/back.png"
      widget = card_widget(r, front, back, face_up=True, selectable=False, hover_enabled=False)
      self.discard_card_widgets.append(widget)

    # text on the "Draw One, Discard One" button changes according to the status
    if getattr(self.engine, "pending_discard_required", False):
      # the cards have been drawn; now it's time to fold.
      self.player_buttons[2].set_text("Discard Selected")
    else:
      self.player_buttons[2].set_text("Draw & Discard")

    # Switch between the "Draw Cards" and "End Turn" buttons
    if not self.player_has_done_action:
      self.player_buttons[-1].set_text("Pass")
    else:
      self.player_buttons[-1].set_text("End Turn")

  def draw_card(self):
    for card in reversed(self.player_card_widgets):
      card.draw(self.screen)

      # ---------- AI hand segmentation drawing----------#
      snapshot = self.engine.ui_snapshot()
      ai_hands = snapshot["ai_hands"]

      index = 0
      for ai_index, hand in enumerate(ai_hands):
        count = len(hand)
        ai_segment = self.ai_card_widgets[index:index + count]

        if ai_index == 0:
          # AI1→ Reverse the drawing, the leftmost element is at the top
          for card in reversed(ai_segment):
            card.draw(self.screen)
        else:
          # AI2→ Drawing in a forward direction, the rightmost element is positioned at the top
          for card in ai_segment:
            card.draw(self.screen)
        index += count
    for card in self.deck_card_widgets:
      card.draw(self.screen)
    for card in self.discard_card_widgets:
      card.draw(self.screen)
    # the card in flight is on top.
    for card in self.animating_cards:
      card.draw(self.screen)

  def draw(self):
    # Synchronize current player name
    self.current_player_name = self.engine.current_player
    # AI action
    if self.engine.ai_wait_until is not None:
      now = pygame.time.get_ticks()

      if now >= self.engine.ai_wait_until:
        phase_finished, log = self.engine.run_single_ai_turn()

        if log:
          self.status_message = log.get("message", "NPC acted.")
          if self.check_game_over(log):
            return
          if log.get("needs_recycle"):
            self.schedule_discard_recycle()

        self.update_card_widgets()

        if phase_finished:
          self.engine.ai_wait_until = None
          self.engine._pending_ai_phase = False
        else:
          self.engine.ai_wait_until = now + 1200

    # Discard recovery time
    if self.discard_show_until is not None:
      now = pygame.time.get_ticks()
      if now >= self.discard_show_until:
        moved = self.engine.recycle_discard_pile()
        self.discard_show_until = None

        if moved > 0:
          self.status_message = f"{moved} cards were shuffled back into the deck."

        self.update_card_widgets()

    s = self.screen
    self.background.draw(s)
    self.draw_avatars(s)
    self.draw_status_bar(s)
    self.draw_card()

    # button
    for btn in self.buttons:
      btn.draw(s)
    for btn in self.player_buttons:
      btn.draw(s)

    pygame.display.flip()

  # ---------- event entry----------#

  def handle_event(self, event):
    # Disable actions while NPC is thinking
    if getattr(self.engine, "_pending_ai_phase", False):
      return

    # Update logical mouse coordinates
    if event.type == pygame.MOUSEMOTION:
      self.mouse_pos = event.pos

    #Action disabled when drawing and discarding one
    if getattr(self.engine, "pending_discard_required", False):
      # the target mode of stealing cards is not allowed
      self.waiting_steal_target = False

      # Only process player hand card clicks
      for card in self.player_card_widgets:
        card.handle_event(event, self.screen_width, self.screen_height)

      # player_buttons: [Draw, Steal, Draw&Discard, Group Out, Pass/End Turn]
      if len(self.player_buttons) >= 3:
        self.player_buttons[2].handle_event(event)

      # 3 People / Difficulty / Restart / Play for me / Quit are disable
      # Draw, Steal, Group Out, Pass are not work
      return

    # -------- Card Stealing Target Selection Mode --------#
    if self.waiting_steal_target:
      # Right-click: Cancel stealing cards
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        self.waiting_steal_target = False
        self._notify({"ok": False, "message": "Steal cancelled."})
        return

      # Left click: Only handles clicks on NPC portraits
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        pos = event.pos
        for i, r in enumerate(self.ai_avatar_click_rects):
          if r is not None and r.collidepoint(pos):
            target_index = i + 1

            # First call the card-stealing logic
            result = self.engine.player_steal(target_index)
            self.waiting_steal_target = False
            self.player_has_done_action = True
            self._notify(result)

            if self.check_game_over(result):
              return

            # refresh UI
            self.update_card_widgets()

            # Card Flying Animation: NPC -> Player
            self._play_steal_animation(target_index, result)

            return

        # Tap elsewhere to exit mode
        return

      # Other events are ignored
      return

    # -------- normal mode-------#

    # bottom button
    for btn in self.buttons:
      btn.handle_event(event)

    # Player's right button
    for btn in self.player_buttons:
      btn.handle_event(event)

    # player cards
    for card in self.player_card_widgets:
      card.handle_event(event, self.screen_width, self.screen_height)

    # AI cards
    for card in self.ai_card_widgets:
      card.handle_event(event, self.screen_width, self.screen_height)

    # deck of cards
    for card in self.deck_card_widgets:
      card.handle_event(event, self.screen_width, self.screen_height)

  # ---------- Update animation every frame ----------#

  def update(self, dt):
    #The card-flying animation updates every frame, dt unit: seconds
    for w in self.animating_cards:
      w.update(dt)
    self.animating_cards = [w for w in self.animating_cards if w.animating]

"----------------------------------------Reference----------------------------------------"
"""
[1]pygame_cards — GitHub repository. https://github.com/vannov/pygame_cards
"""

