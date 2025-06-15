from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
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
        layout.add_widget(Button(text="Go to Add Habit", on_press=self.goto_add_habit))
        layout.add_widget(Button(text="Go to View Habit Stats", on_press=self.goto_view_habit_stats))
        self.add_widget(layout)

    def goto_add_habit(self, instance):
        self.manager.current = 'add_habit'

class AddHabitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Add a new habit here."))
        layout.add_widget(Button(text="Go back", on_press=self.goto_home))
        self.add_widget(layout)

    def goto_home(self, instance):
        self.manager.current = 'home'

class ViewHabitStats(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Add a new habit here."))
        layout.add_widget(Button(text="Go back", on_press=self.goto_home))
        self.add_widget(layout)

class HabitApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddHabitScreen(name='add_habit'))
        sm.add_widget(ViewHabitStats(name="view_stats"))
        return sm

if __name__ == '__main__':
    HabitApp().run()