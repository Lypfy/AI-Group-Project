import pygame
import pygame_gui

class GameUI:
    def __init__(self, manager):
        self.manager = manager
        
        self.inventory_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, 20), (120, 40)),
            text='Inventory',
            manager=self.manager
        )
        
        self.run_skill_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, 70), (120, 40)),
            text='Run Skill',
            manager=self.manager
        )
        
        self.auto_move_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((980, 20), (100, 40)),
            text='Auto Move',
            manager=self.manager
        )
        self.auto_move_button.disable() # Disabled until path found
        
        self.sensor_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((1090, 20), (90, 40)),
            text='Sensor: OFF',
            manager=self.manager
        )
        
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((980, 70), (100, 40)),
            text='Reset Level',
            manager=self.manager
        )
        
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((850, 120), (120, 30)),
            text='Pause',
            manager=self.manager
        )
        
        self.unlocked_levels = ['Level 1']
        self.level_selector = pygame_gui.elements.UIDropDownMenu(
            options_list=self.unlocked_levels,
            starting_option='Level 1',
            relative_rect=pygame.Rect((980, 120), (100, 30)),
            manager=self.manager
        )
        
        self.unlock_all_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((1090, 120), (100, 30)),
            text='Unlock All',
            manager=self.manager
        )
        
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((850, 160), (100, 20)),
            text='Speed (ms):',
            manager=self.manager
        )
        
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((950, 160), (230, 20)),
            start_value=0,
            value_range=(0.0, 2000.0),
            manager=self.manager
        )

        self.log_lines = ["<font color='#00FF00'>System Initialized.</font>"]
        self.log_text = "<br>".join(self.log_lines)
        self.log_box = pygame_gui.elements.UITextBox(
            html_text=self.log_text,
            relative_rect=pygame.Rect((850, 190), (330, 410)),
            manager=self.manager
        )
        
        self.clear_log_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((1060, 605), (120, 30)),
            text='Clear Log',
            manager=self.manager
        )
        
        self.inventory_window = None
        self.skill_list = None
        self.level_complete_window = None
        self.next_level_button = None
        self.selected_skill = "BFS"
        self.player_skills = ["BFS"]
        self.is_paused = False
        self.sensor_on = False

    def update_level_selector(self, selected_option):
        if self.level_selector:
            self.level_selector.kill()
        self.level_selector = pygame_gui.elements.UIDropDownMenu(
            options_list=self.unlocked_levels,
            starting_option=selected_option,
            relative_rect=pygame.Rect((980, 120), (100, 30)),
            manager=self.manager
        )

    def reset_pause(self):
        self.is_paused = False
        self.pause_button.set_text('Pause')

    def log(self, message):
        self.log_lines.append(message)
        if len(self.log_lines) > 50:
            self.log_lines = self.log_lines[-50:]
        
        self.log_text = "<br>".join(self.log_lines)
        self.log_box.set_text(self.log_text)
        if hasattr(self.log_box, 'scroll_bar') and self.log_box.scroll_bar:
            self.log_box.scroll_bar.set_scroll_from_start_percentage(1.0)
            self.log_box.update(0.0)

    def clear_log(self):
        self.log_lines = []
        self.log_text = ""
        self.log_box.set_text(self.log_text)

    def open_inventory(self):
        if self.inventory_window is None:
            self.inventory_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect((400, 150), (300, 300)),
                manager=self.manager,
                window_display_title='Inventory'
            )
            self.skill_list = pygame_gui.elements.UISelectionList(
                relative_rect=pygame.Rect((10, 10), (250, 200)),
                item_list=self.player_skills,
                manager=self.manager,
                container=self.inventory_window
            )

    def show_level_complete(self, reward_skills):
        if type(reward_skills) is str:
            reward_skills = [reward_skills]
            
        if self.level_complete_window is None:
            self.level_complete_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect((350, 200), (400, 200)),
                manager=self.manager,
                window_display_title='Level Complete!'
            )
            
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 20), (350, 50)),
                text=f"Phần thưởng: Kỹ năng {', '.join(reward_skills)}",
                manager=self.manager,
                container=self.level_complete_window
            )
            
            self.next_level_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((125, 90), (150, 40)),
                text='Màn tiếp theo',
                manager=self.manager,
                container=self.level_complete_window
            )
            
            for skill in reward_skills:
                if skill not in self.player_skills:
                    self.player_skills.append(skill)
                    self.log(f"<font color='#FFFF00'>Đã mở khóa kỹ năng: {skill}</font>")
                    
            # Refresh skill list if it's open
            if self.skill_list:
                self.skill_list.set_item_list(self.player_skills)

    def show_victory_screen(self):
        if self.level_complete_window is None:
            self.level_complete_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect((350, 150), (400, 300)),
                manager=self.manager,
                window_display_title='Chiến thắng!'
            )
            
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 20), (350, 50)),
                text="Bạn đã thành công thoát khỏi mê cung!",
                manager=self.manager,
                container=self.level_complete_window
            )
            
            try:
                from core.utils import load_image, get_tile
                from core.settings import TILESET_PATH
                tileset_sheet = load_image(TILESET_PATH)
                trophy_img = get_tile(tileset_sheet, 0, 7)
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect((176, 80), (48, 48)),
                    image_surface=trophy_img,
                    manager=self.manager,
                    container=self.level_complete_window
                )
            except Exception as e:
                print("Could not load trophy image:", e)
            
            self.next_level_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((125, 180), (150, 40)),
                text='Đóng',
                manager=self.manager,
                container=self.level_complete_window
            )

    def process_events(self, event):
        action = None
        data = None

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.inventory_button:
                self.open_inventory()
            elif event.ui_element == self.run_skill_button:
                action = "RUN_SKILL"
                data = self.selected_skill
            elif event.ui_element == self.clear_log_button:
                action = "CLEAR_LOG"
            elif event.ui_element == self.next_level_button:
                action = "NEXT_LEVEL"
                if self.level_complete_window:
                    self.level_complete_window.kill()
                    self.level_complete_window = None
                    self.next_level_button = None
            elif event.ui_element == self.auto_move_button:
                action = "AUTO_MOVE"
            elif event.ui_element == self.reset_button:
                action = "RESET"
            elif event.ui_element == self.unlock_all_button:
                action = "UNLOCK_ALL"
            elif event.ui_element == self.pause_button:
                action = "PAUSE_TOGGLE"
                self.is_paused = not self.is_paused
                if self.is_paused:
                    self.pause_button.set_text('Resume')
                else:
                    self.pause_button.set_text('Pause')
            elif event.ui_element == self.sensor_button:
                action = "SENSOR_TOGGLE"
                self.sensor_on = not self.sensor_on
                if self.sensor_on:
                    self.sensor_button.set_text('Sensor: ON')
                else:
                    self.sensor_button.set_text('Sensor: OFF')

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.speed_slider:
                action = "SPEED_CHANGE"
                data = int(event.value)

        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.inventory_window:
                self.inventory_window = None
                self.skill_list = None
            elif event.ui_element == self.level_complete_window:
                self.level_complete_window = None
                self.next_level_button = None

        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.skill_list:
                self.selected_skill = event.text
                self.log(f"<font color='#00AAFF'>Đã chọn kỹ năng: {self.selected_skill}</font>")

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.level_selector:
                action = "SELECT_LEVEL"
                data = int(event.text.split()[1]) - 1 # 'Level 1' -> 0
        return action, data
