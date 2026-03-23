import click
from db import create_tables, preload_data
from habit import User, Habit
import analyze
import bcrypt
from db import get_db_connection

create_tables()
preload_data()

@click.group()
def cli(): pass

@cli.command()
@click.option('--email', prompt=True)
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def register(email, username, password):
    User.register_user(email, username, password)
    click.echo("✅ User registered!")

@cli.command()
@click.option('--user', prompt='Username')
@click.option('--name', prompt='Habit name')
@click.option('--description', prompt='Description')
@click.option('--periodicity', prompt='daily or weekly')
def habit_create(user, name, description, periodicity):
    user_id = get_user_id(user)
    habit_id = Habit.create_habit(user_id, name, description, periodicity)
    click.echo(f"✅ Habit created (ID: {habit_id})")

@cli.command()
@click.option('--user', prompt='Username')
@click.option('--habit_name', prompt='Habit name')
def complete(user, habit_name):
    user_id = get_user_id(user)
    habit_id = get_habit_id(user_id, habit_name)
    from datetime import datetime
    conn = get_db_connection()
    conn.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                 (habit_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    click.echo("✅ Completion logged!")

@cli.command()
@click.option('--user', prompt='Username')
def longest_global(user):
    streak = analyze.longest_global_streak(get_user_id(user))
    click.echo(f"🏆 Global longest streak: {streak}")

def get_user_id(username):
    conn = get_db_connection()
    row = conn.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row["user_id"] if row else None

def get_habit_id(user_id, name):
    conn = get_db_connection()
    row = conn.execute("SELECT habit_id FROM habits WHERE user_id = ? AND name = ?", (user_id, name)).fetchone()
    conn.close()
    return row["habit_id"] if row else None

if __name__ == '__main__':
    cli()