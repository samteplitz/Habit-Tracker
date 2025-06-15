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
import sqlite3
from datetime import date

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

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Welcome to the Habit Tracker!"))
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

#Helper Function to get all habits from the database
def get_all_habits():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT name, frequency FROM habits')
    habits = cursor.fetchall()
    conn.close()
    return habits

# Function to insert a new habit into the database
def insert_habit(habit_name, frequency):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name, frequency) VALUES (?, ?)", (habit_name, frequency))
    conn.commit()
    conn.close()
    

class ViewHabitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Welcome to the Habit Tracker."))
        layout.add_widget(Label(text = "Current Habits"))
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10 )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        layout.add_widget(Button(text="Add Habit", on_press=self.open_add_habit_popup))
        layout.add_widget(Button(text="Go back", on_press=self.goto_home))
        self.add_widget(layout)
    
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

    def on_enter(self):
        self.load_habits()

    def load_habits(self):
        self.grid.clear_widgets()
        habits = get_all_habits()
        for name, frequency in habits:
            label = Label(text=f"Habit: {name} Frequency: {frequency}", size_hint_y=None, height=40)
            self.grid.add_widget(label)
    
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


class HabitApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ViewHabitScreen(name='view_habits'))
        sm.add_widget(LogHabitsScreen(name='log_habits'))
        sm.add_widget(ViewHabitStats(name="view_stats"))
        return sm

if __name__ == '__main__':
    HabitApp().run()