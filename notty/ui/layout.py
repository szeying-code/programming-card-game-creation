# notty/ui/layout.py
import pygame

"----------------------------------------The main parent areas of the screen----------------------------------------"
def rect_father_layout(screen):
    #Margin
    margin = 10

    # Get screen width and height
    screen_w = screen.get_width()
    screen_h = screen.get_height()

    # The screen height proportion occupied by the main parent areas
    status_bar_h = int(screen_h * 0.05)  # Status bar
    ai_hand_h = int(screen_h * 0.36) #NPC hand
    player_hand_h = int(screen_h * 0.2) #User hand
    footer_h = int(screen_h * 0.06) #footer
    # Remaining height is used as the table area
    table_h = screen_h - (status_bar_h + ai_hand_h + player_hand_h + footer_h) - (margin * 6) #Desk
    "----------------------------------------Rects for each main area----------------------------------------"
    status_bar_rect = pygame.Rect(margin, margin, screen_w - (margin * 2), status_bar_h)# Status bar at the top
    ai_hand_rect = pygame.Rect(margin, status_bar_rect.bottom + margin, screen_w - (margin * 2), ai_hand_h)# NPC hand
    table_rect = pygame.Rect(margin, ai_hand_rect.bottom + margin, screen_w - (margin * 2), table_h)# Table
    player_hand_rect = pygame.Rect(margin, table_rect.bottom + margin, screen_w - (margin * 2), player_hand_h)#User hand
    footer_rect = pygame.Rect(margin, player_hand_rect.bottom + margin, screen_w - (margin * 2), footer_h)# footer
    return {
        'status': status_bar_rect,
            'ai_hand': ai_hand_rect,
            'table': table_rect,
            'player_hand': player_hand_rect,
            'footer': footer_rect,
            'screen_w': screen_w,
            'screen_h': screen_h,
            'margin': margin
            }# Return all main rects

"----------------------------------------Rects for NPC hand----------------------------------------"
def rect_son_layout_ai(father_layout):
    # Extract NPC area rect and margin from father layout
    ai_hand_rect, margin = father_layout['ai_hand'], father_layout['margin']

    ai_sidebar_w = int(ai_hand_rect.width * 0.15)# Side area width for AI info/avatars (15% of total width)
    ai_card_w = int((ai_hand_rect.width - (ai_sidebar_w * 2)) / 2)# Card area width for each AI
    ai_info_1_rect = pygame.Rect(ai_hand_rect.left, ai_hand_rect.top, ai_sidebar_w, ai_hand_rect.height) # Left NPC info area
    ai_cards_1_rect = pygame.Rect(ai_info_1_rect.right, ai_hand_rect.top, ai_card_w, ai_hand_rect.height) # Left NPC card area
    ai_cards_2_rect = pygame.Rect(ai_cards_1_rect.right, ai_hand_rect.top, ai_card_w, ai_hand_rect.height) # Right NPC card area
    ai_info_2_rect = pygame.Rect(ai_cards_2_rect.right, ai_hand_rect.top, ai_sidebar_w, ai_hand_rect.height) # Right NPC area

    ai_info_1_text_rect = pygame.Rect(ai_info_1_rect.left+5, ai_info_1_rect.top, ai_info_1_rect.width, ai_info_1_rect.height * 0.2)# NPC 1 text area
    ai_info_1_image_rect = pygame.Rect(ai_info_1_rect.left, ai_info_1_rect.top + ai_info_1_rect.height * 0.2, ai_info_1_rect.width, ai_info_1_rect.height * 0.8) # NPC 1 image area
    ai_info_2_text_rect = pygame.Rect(ai_info_2_rect.left-5, ai_info_2_rect.top, ai_info_2_rect.width, ai_info_2_rect.height * 0.2)# NPC 2 text area
    ai_info_2_image_rect = pygame.Rect(ai_info_2_rect.left, ai_info_2_rect.top + ai_info_2_rect.height * 0.2, ai_info_2_rect.width, ai_info_2_rect.height * 0.8) # NPC 2 image area
    return {
        'ai_info_1': {
            'whole': ai_info_1_rect,
            'ai_info_1_text': ai_info_1_text_rect,
            'ai_info_1_image': ai_info_1_image_rect
        },
        'ai_cards_1': ai_cards_1_rect,
        'ai_cards_2': ai_cards_2_rect,
        'ai_info_2': {
            'whole': ai_info_2_rect,
            'ai_info_2_text': ai_info_2_text_rect,
            'ai_info_2_image': ai_info_2_image_rect
        },
    }# Return sub-rects for AI info and card areas

"----------------------------------------Rects for Deck----------------------------------------"
def rect_son_layout_table(father_layout):
    table_rect, margin = father_layout['table'], father_layout['margin']# Get table rect and margin
    deck_w = int(table_rect.width * 0.5)# Deck and discard uses 50% of table width separately
    deck_rect = pygame.Rect(table_rect.left, table_rect.top, deck_w, table_rect.height)# deck area
    discard_rect = pygame.Rect(deck_rect.right, table_rect.top, deck_w, table_rect.height)# discard area
    return {
        'deck': deck_rect,
        'discard': discard_rect
    }# Return deck and discard rects

"----------------------------------------Rects for User hand----------------------------------------"
def rect_son_layout_player(father_layout):
    player_hand_rect, margin = father_layout['player_hand'], father_layout['margin']# Get player hand rect and margin
    player_sidebar_w = int(player_hand_rect.width * 0.15)# Side width for avatar/info and buttons
    player_info_rect = pygame.Rect(player_hand_rect.left, player_hand_rect.top, player_sidebar_w,player_hand_rect.height)# Player avatar/info area
    player_cards_rect = pygame.Rect(player_info_rect.right, player_hand_rect.top, player_hand_rect.width - (player_sidebar_w * 2), player_hand_rect.height)# Player cards area
    player_buttons_rect = pygame.Rect(player_cards_rect.right, player_hand_rect.top, player_sidebar_w, player_hand_rect.height)# Action buttons area
    player_info_text_rect = pygame.Rect(player_info_rect.left+5, player_info_rect.top-4, player_info_rect.width, player_info_rect.height * 0.3)# Player text area
    player_info_image_rect = pygame.Rect(player_info_rect.left+5, player_info_rect.top-4 + player_info_rect.height * 0.3, player_info_rect.width, player_info_rect.height * 0.7)# Player image area

    # Margin
    margin_button = 5
    # Single button height
    singal_button_height = (player_buttons_rect.height - margin_button * 4 * 4) // 3#Single button height(Reduce the height by multiplied margin)
    short_button_weight =  (player_buttons_rect.width - margin_button * 3) // 2# Width of short button
    long_button_weight = player_buttons_rect.width - margin_button * 2# Width of long button
    #from top-left to bottom-right
    # 1st row: two short buttons
    short_button1_rect = pygame.Rect(player_buttons_rect.left + margin_button, player_buttons_rect.top + margin_button * 4, short_button_weight, singal_button_height)
    short_button2_rect = pygame.Rect(short_button1_rect.right + margin_button, player_buttons_rect.top + margin_button * 4, short_button_weight, singal_button_height)
    # 2nd row: two short buttons
    short_button3_rect = pygame.Rect(player_buttons_rect.left + margin_button, short_button1_rect.bottom + margin_button * 4, short_button_weight, singal_button_height)
    short_button4_rect = pygame.Rect(short_button3_rect.right + margin_button, short_button2_rect.bottom + margin_button * 4, short_button_weight, singal_button_height)
    # 3rd row: long buttons
    long_button_rect =  pygame.Rect(player_buttons_rect.left + margin_button, short_button4_rect.bottom + margin_button * 4, long_button_weight, singal_button_height)

    return {
            'player_info': {
                'whole': player_info_rect,
                'player_info_text': player_info_text_rect,
                'player_info_image': player_info_image_rect
                },
            'player_cards': player_cards_rect,
            'player_buttons': {
                'whole': player_buttons_rect,
                'short_button1': short_button1_rect,
                'short_button2': short_button2_rect,
                'short_button3': short_button3_rect,
                'short_button4': short_button4_rect,
                'long_button': long_button_rect
                }
            }# Return all sub-rects for player area

"----------------------------------------Rects for Status Bar----------------------------------------"
def rect_son_layout_status_header(father_layout):
    status_bar_rect = father_layout['status']# Get status bar rect
    status_side_w = int(status_bar_rect.width * 0.3)# Side width for left and right sections
    status_card_num_rect = pygame.Rect(status_bar_rect.left, status_bar_rect.top, status_side_w, status_bar_rect.height)# Left
    status_main_alarm_rect = pygame.Rect(status_card_num_rect.right, status_bar_rect.top, status_bar_rect.width - (status_side_w * 2), status_bar_rect.height)# middle
    status_player_rect = pygame.Rect(status_main_alarm_rect.right, status_bar_rect.top, status_side_w, status_bar_rect.height)# Right
    return {
        'status_card_num': status_card_num_rect,
        'status_main_alarm': status_main_alarm_rect,
        'status_player': status_player_rect
    }# Return all sub-rects for status bar

"----------------------------------------Rects for footer----------------------------------------"
def rect_son_layout_status_footer(father_layout):
    footer_rect = father_layout['footer']# Get footer rect
    margin = 15  #Vertical margin

    #Button size
    short_w = int(footer_rect.width * 0.088)  # Short button width
    long_w = int(short_w * 4.3)# Long button width
    btn_h = footer_rect.height - margin * 2# Button height

    # Total width of 5 buttons
    total_btn_w = short_w * 4 + long_w

    # 6 gaps: left, 4 between buttons, right, Calculate it
    gap = (footer_rect.width - total_btn_w) / 6

    # Button order: short, short, long, short, short
    x = footer_rect.left + gap

    btn1 = pygame.Rect(x, footer_rect.top + margin, short_w, btn_h)
    x += short_w + gap
    btn2 = pygame.Rect(x, footer_rect.top + margin, short_w, btn_h)
    x += short_w + gap
    btn3 = pygame.Rect(x, footer_rect.top + margin, long_w, btn_h)
    x += long_w + gap
    btn4 = pygame.Rect(x, footer_rect.top + margin, short_w, btn_h)
    x += short_w + gap
    btn5 = pygame.Rect(x, footer_rect.top + margin, short_w, btn_h)

    return {
        'footer_btn1': btn1,
        'footer_btn2': btn2,
        'footer_btn3': btn3,
        'footer_btn4': btn4,
        'footer_btn5': btn5,
    }# Return all sub-rects for footer button

"----------------------------------------Rects for card----------------------------------------"
class card_layout:
    def __init__(self,max_cards_per_row=10,max_cards_total=20,overlap_ratio=0.3,card_aspect=1.4):
        self.max_cards_per_row = max_cards_per_row# Maximum number of cards per row
        self.max_cards_total = max_cards_total# Maximum total cards to display
        self.overlap_ratio = overlap_ratio# Overlap ratio
        self.card_aspect = card_aspect# Card aspect ratio (width / height)

        # Width / Height record
        self.card_width = None
        self.card_height = None

    "--------------------Rects for NPC card--------------------"
    def layout_ai(self, area_rect, num_cards, align="left"):

        # Displayed card num < max_cards_total
        n = min(num_cards, self.max_cards_total)
        if n == 0:
            return []

        # Card size

        # Vertical:Half the area height for one row (+margin)
        total_h = area_rect.height
        card_h_from_height = (total_h / 2) * 0.95
        card_w_from_height = card_h_from_height / self.card_aspect

        # Horizontal: based on max_cards_per_row and overlap ratio
        visible_ratio = 1.0 - self.overlap_ratio
        max_total_width = area_rect.width * 0.95
        card_w_from_width = max_total_width / (1 + (self.max_cards_per_row - 1) * visible_ratio)

        # Final card width = min of height-based and width-based
        card_w = int(min(card_w_from_height, card_w_from_width))
        card_h = int(card_w * self.card_aspect)
        step_x = int(card_w * visible_ratio)

        # Horizontal step between cards
        self.card_width = card_w
        self.card_height = card_h

        rects = []

        # Compute Y positions for up to 2 rows
        H = area_rect.height
        gap = (H - card_h * 2) / 3
        row1_y = area_rect.y + gap
        row2_y = area_rect.y + gap + card_h + gap

        # Compute X positions based on card num
        if n <= self.max_cards_per_row:
            rows = 1
            row1_n = n
            row2_n = 0
        else:
            rows = 2
            row1_n = self.max_cards_per_row
            row2_n = n - self.max_cards_per_row

        # X offset to create a margin with border
        offset_x = 20

        # First row
        if align == "left":
            # Left aligned
            x = area_rect.x + offset_x
        else:
            # Right aligned: Start from the right
            x = area_rect.right - offset_x - card_w - step_x * (row1_n - 1)

        for i in range(row1_n):
            rects.append(pygame.Rect(int(x), int(row1_y), card_w, card_h))
            x += step_x

        # Second row (Similar)
        if rows == 2:
            if align == "left":
                x = area_rect.x + offset_x
            else:
                x = area_rect.right - offset_x - card_w - step_x * (row2_n - 1)

            for i in range(row2_n):
                rects.append(pygame.Rect(int(x), int(row2_y), card_w, card_h))
                x += step_x #**[1]**

        return rects

    "--------------------Rects for Deck--------------------"
    def card_layout_desk(self, area_rect, num_cards):

        # Use existing card size
        card_w = self.card_width
        card_h = self.card_height

        # Fixed left offset
        offset_x = 43

        # Max card num = 90
        max_n = 90
        n = min(num_cards, max_n)
        if n == 0:
            return []

        rects = []

        # Max width of the area = 90% of the deck
        max_width = area_rect.width * 0.9

        # Step between positions when 90 cards fully occupy max_width
        if max_n > 1:
            step_x = (max_width - card_w) / (max_n - 1)
            if step_x < 1:
                step_x = 1
        else:
            step_x = 0

        # Start from left + offset
        start_x = area_rect.x + offset_x

        # Vertical center
        start_y = area_rect.y + (area_rect.height - card_h) / 2

        # Generate rects list
        for i in range(n):
            x = start_x + i * step_x
            rects.append(pygame.Rect(int(x), int(start_y), card_w, card_h))

        return rects

    "--------------------Rects for Discard area--------------------"
    def card_layout_discard(self, area_rect, num_cards, gap=10):

        # Max card num = 9
        n = min(num_cards, 9)
        if n == 0:
            return []

        card_w = self.card_width
        card_h = self.card_height

        rects = []

        # Total width = n * card_w + (n - 1) * gap
        total_width = n * card_w + (n - 1) * gap

        # Horizontally centered
        start_x = area_rect.x + (area_rect.width - total_width) / 2
        # Vertically centered
        start_y = area_rect.y + (area_rect.height - card_h) / 2

        # Place discard cards left -> right
        for i in range(n):
            x = start_x + i * (card_w + gap)
            rects.append(pygame.Rect(int(x), int(start_y), card_w, card_h))

        return rects

    "--------------------Rects for Player hand--------------------"
    def card_layout_player(self, area_rect, num_cards):

        # Max card num = 20
        n = min(num_cards, 20)
        if n == 0:
            return []

        card_w = self.card_width
        card_h = self.card_height

        # Visible part ratio (based on overlap)
        visible_ratio = 1.0 - self.overlap_ratio
        step_x = int(card_w * visible_ratio)

        # Left-based + offset
        offset_x = 53

        start_x = area_rect.x + offset_x

        # Vertically centered
        start_y = area_rect.y + (area_rect.height - card_h) / 2

        rects = []
        x = start_x
        for i in range(n):
            rects.append(pygame.Rect(int(x), int(start_y), card_w, card_h))
            x += step_x

        return rects

"----------------------------------------Reference----------------------------------------"
"""
[1]Stack Overflow. How to make multiple blocks with same dimensions but different locations in Pygame.
https://stackoverflow.com/questions/43708962/how-to-make-multiple-blocks-with-same-dimensions-but-different-locations-in-pyga?
The author demonstrates how to use pygame.Rect together with a for i in range(...) loop to generate multiple blocks 
in bulk by applying a fixed step size (step = i * width) and assigning each block its own x and y coordinates.
Our code adapts this idea by also using loops and a step size (step_x), along with an offset (offset_x) and alignment (align) logic, 
to place cards into two rows and calculate their coordinates individually.
"""
