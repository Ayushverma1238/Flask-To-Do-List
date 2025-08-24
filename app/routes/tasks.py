from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Task, User

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/")
def view_tasks():
    if 'user_id' not in session:
        flash("Please login to view this page", 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id = user_id).all()
    return render_template("tasks.html", tasks = tasks)

@tasks_bp.route("/add", methods = ["POST"])
def add_tasks(): 
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    title = request.form.get('title')
    user_id = session['user_id']
    if title:
        new_task = Task(title = title, status = 'Pending', user_id = user_id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully", 'success')
    else:
        flash("Task title cannot be empty.", 'danger') 
    return redirect(url_for('tasks.view_tasks'))


@tasks_bp.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_status(task_id):
    if 'user_id' not in session:
        return redirect(url_for("auth.login"))

    task = Task.query.get(task_id)

    if task and task.user_id == session['user_id']:
        # Uses capitalized strings to match the database default "Pending"
        if task.status == 'Pending':
            task.status = "Working"
        elif task.status == 'Working': 
            task.status = "Done"
        else:
            task.status = "Pending"
            
        db.session.commit()
        
    return redirect(url_for('tasks.view_tasks'))

@tasks_bp.route("/clear", methods = ["POST"])
def clear_tasks():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    Task.query.filter_by(user_id = session['user_id']).delete()
    db.session.commit()
    flash("All tasks cleared!", 'info')
    return redirect(url_for("tasks.view_tasks"))




# for delet a specific node



@tasks_bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    # 1. Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to perform this action.", "warning")
        return redirect(url_for('auth.login'))
        
    # 2. Find the task by its ID
    task_to_delete = Task.query.get(task_id)

    # 3. Check if the task exists AND if it belongs to the current user
    if task_to_delete and task_to_delete.user_id == session['user_id']:
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            flash("Task deleted successfully.", 'success')
        except:
            db.session.rollback() # Rollback the session in case of an error
            flash("There was an issue deleting the task.", 'danger')
    elif task_to_delete:
        # Task exists, but doesn't belong to the user
        flash("You do not have permission to delete this task.", 'danger')
    else:
        # Task does not exist
        flash("Task not found.", 'danger')

    return redirect(url_for('tasks.view_tasks'))
