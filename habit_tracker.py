from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.core.window import Window
import sqlite3
from datetime import date


#Database related functions
# Set the database name
DB_NAME = 'habits.db'

# Database setup
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            frequency TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            date TEXT,
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        )
    ''')
    conn.commit()
    conn.close()

#Helper Function to get all habits from the database
def get_all_habits():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, frequency FROM habits')
    habits = cursor.fetchall()
    print(habits)
    conn.close()
    return habits


# Function to insert a new habit into the database
def insert_habit(habit_name, frequency):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name, frequency) VALUES (?, ?)", (habit_name, frequency))
    conn.commit()
    conn.close()



class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Welcome to the Habit Tracker!", color = [0, 0, 0, 1]))
        layout.add_widget(Button(text="View Habits", on_press=self.goto_add_habit))
        layout.add_widget(Button(text="Go to Log Habits", on_press=self.goto_log_habits))
        layout.add_widget(Button(text="Go to View Habit Stats", on_press=self.goto_view_habit_stats))
        self.add_widget(layout)

    def goto_add_habit(self, instance):
        self.manager.current = 'view_habits'
    def goto_log_habits(self, instance):
        self.manager.current = 'log_habits'
    def goto_view_habit_stats(self, instance):
        self.manager.current = 'view_stats'


    

class ViewHabitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(Label(text="Welcome to the Habit Tracker.", size_hint_y=.1, color=[0, 0, 0, 1]))
        self.main_layout.add_widget(Label(text = "Current Habits",size_hint_y = .1, color = [0, 0, 0, 1]))

        self.tableLayout = AnchorLayout(size_hint_y=.6)
        self.table = None
        self.main_layout.add_widget(self.tableLayout)

        #self.tableLayout.add_widget(self.data_table)
        self.add_widget(self.main_layout)

        #Grid Layout for buttons
        self.grid_layout = GridLayout(cols=2, rows = 2, size_hint_y=.2)
        self.grid_layout.add_widget(Button(text="Add Habit", on_press=self.open_add_habit_popup, size_hint_y = .1))
        self.grid_layout.add_widget(Button(text="Edit Habit", on_press=self.open_edit_habit_popup, size_hint_y = .1))
        self.grid_layout.add_widget(Button(text="Delete Habit", on_press=self.open_delete_habit_popup, size_hint_y = .1))
        self.grid_layout.add_widget(Button(text="Go back", on_press=self.goto_home, size_hint_y = .1))
        self.main_layout.add_widget(self.grid_layout)
    
    #function to update a user selected habit in the database
    def update_habit_in_db(self, old_habit, new_habit, new_freq):
        conn = sqlite3.connect("habits.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE habits SET name = ?, frequency = ? WHERE name = ?",
            (new_habit, new_freq, old_habit)
        )
        conn.commit()
        conn.close()

    #function to delete a user selected habit from the database
    def delete_habit_from_db(self, habit_name):
        conn = sqlite3.connect("habits.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_name,))
        conn.commit()
        conn.close()
    
    def open_add_habit_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        habit_input = TextInput(hint_text='Habit Name', multiline=False)
        frequency_input = TextInput(hint_text='Frequency (daily, weekly, monthly)', multiline=False)
        submit_button = Button(text='Submit')

        content.add_widget(habit_input)
        content.add_widget(frequency_input)
        content.add_widget(submit_button)

        popup = Popup(title='Add New Habit',
                      content=content,
                      size_hint=(0.8, 0.5),
                      auto_dismiss=True)

        def on_submit(_):
            habit = habit_input.text.strip()
            frequency = frequency_input.text.strip()
            if habit and frequency:
                insert_habit(habit, frequency)
                popup.dismiss()
                self.load_habits()

        submit_button.bind(on_press=on_submit)
        popup.open()
    
    def open_edit_habit_popup(self, instance):
        if not hasattr(self, 'selected_row') or not self.selected_row:
            print("No row selected")
            return

        habit_name, frequency = self.selected_row

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        habit_input = TextInput(text=habit_name, multiline=False)
        freq_input = TextInput(text=frequency, multiline=False)

        submit_button = Button(text='Update')
        content.add_widget(habit_input)
        content.add_widget(freq_input)
        content.add_widget(submit_button)

        popup = Popup(title='Edit Habit',
                  content=content,
                  size_hint=(0.8, 0.5),
                  auto_dismiss=True)
        popup.open()

    
        def submit_edits(_):
            new_habit = habit_input.text.strip()
            if not new_habit:
                print("Habit name cannot be empty")
                return      
            new_freq = freq_input.text.strip()
            if new_habit and new_freq:
                self.update_habit_in_db(old_habit=habit_name, new_habit=new_habit, new_freq=new_freq)
                print("Habit updated:", new_habit, new_freq)
                popup.dismiss()
                self.load_habits()

        submit_button.bind(on_press=submit_edits)
            
    def open_delete_habit_popup(self, instance):
        if not hasattr(self, 'selected_row') or not self.selected_row:
            print("No row selected")
            return

        habit_name, _ = self.selected_row

        # Popup layout
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        message = Label(text=f"Are you sure you want to delete '{habit_name}' from the table?")

        buttons = BoxLayout(orientation='horizontal', spacing=10)
        yes_button = Button(text='Yes')
        no_button = Button(text='No')

        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)

        content.add_widget(message)
        content.add_widget(buttons)

        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )

        def confirm_delete(_):
            self.delete_habit_from_db(habit_name)
            popup.dismiss()
            self.load_habits()

        yes_button.bind(on_press=confirm_delete)
        no_button.bind(on_press=popup.dismiss)

        popup.open()

    def on_enter(self):
        self.load_habits()

    def load_habits(self):
        if self.table:
            self.tableLayout.remove_widget(self.table)

        habits = get_all_habits()

        #calculations for screen size
        screen_width = self.tableLayout.width
        print(screen_width)
        table_width = screen_width * 0.9  # 90% of screen width
         # Calculate column widths in dp
        col1_width = dp(table_width * 0.1)
        col2_width = dp(table_width * 0.1)

        self.table = MDDataTable(
            size_hint=(1, 1),
         
            check=True,
            use_pagination=True,
            column_data=[
                ("Habit", col1_width),
                ("Frequency", col2_width),
            ],
            
            row_data=[(str(h), str(f)) for h, f in habits]  # Ensure strings
        )
        self.table.bind(on_check_press=self.on_row_selected)
        self.tableLayout.add_widget(self.table)

    def on_row_selected(self, instance_table, current_row):
        self.selected_row = current_row
        # Also get selected index from MDDataTable (important!)



    def goto_home(self, instance):
        self.manager.current = 'home'

class LogHabitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Log your habits here."))
        layout.add_widget(Button(text="Go back", on_press=self.goto_home))
        self.add_widget(layout)

    def goto_home(self, instance):
        self.manager.current = 'home'

class ViewHabitStats(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="View stats for habits here."))
        layout.add_widget(Button(text="Go back", on_press=self.goto_home))
        self.add_widget(layout)
    
    def goto_home(self, instance):
        self.manager.current = 'home'


class HabitApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ViewHabitScreen(name='view_habits'))
        sm.add_widget(LogHabitsScreen(name='log_habits'))
        sm.add_widget(ViewHabitStats(name="view_stats"))
        return sm

if __name__ == '__main__':
    HabitApp().run()