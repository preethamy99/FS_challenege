from flask import Flask, jsonify, request, Response
import datetime
import time
import threading
from gevent.events import subscribers
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from emil.minme.multipart import MIMEMultipart

app = Flask(__name__)
tasks = [
    {'id': 1, 'title': 'Grocery Shopping', 'completed': False, 'due_date': '2024-03-15'},
    {'id': 2, 'title': 'Pay Bills', 'completed': False, 'due_date': '2024-03-20'},
]
next_task_id = 3  # For assigning new task IDs


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    # If using a Database like MongoDB.
    # try:
    #     with MongoClient('mongodb://localhost:27017/') as db:
    #         collection = db['DB_name']['Collection_name']
    #         result = collection.find()
    #         l = []
    #         if result:
    #             for i in result:
    #                 l.append(i)
    #             return jsonify(l), 200
    #         else:
    #             return jsonify('No Data present'), 200
    # except:
    #     app.logger.info(f"There is a error while fetching the task details: {e}")
    #     return jsonify('error'), 500
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def create_task():
    global next_task_id
    data = request.get_json()
    new_task = {
        'id': next_task_id,
        'title': data['title'],
        'completed': False,
        'due_date': data.get('due_date') or datetime.date.today().strftime("%Y-%m-%d")
    }
    next_task_id += 1
    tasks.append(new_task)
    # if we use mongodb we insert the document using
    # gobal mongo_connstr
    # try:
    #     with MongoCleint('mongodb://localhost:27017/') as db:
    #         collection = db[DB_name][Collection_name]
    #         result = collection.insert_one(new_task)
    #         if result:
    #             return jsonify('Document inserted succesfully'), 201
    #         else:
    #             return jsonify('Can't insert the document'), 201
    # except:
    #     app.logger.info(f"There is a error while adding the task: {e}")
    #     return jsonify('error'), 500
    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    for task in tasks:
        if task['id'] == task_id:
            task.update(data)  # Update task attributes
            # Send notification asynchronously
            # with MongoClient('mongodb://localhost:27017/') as dbh:
                # db = dbh['your_database']
                # collection = db['your_collection']
                # Example code
                # task_id = 1
                # update_fields = {
                #     'title': 'Updated Task Title',
                #     'completed': True,
                #     'due_date': '2024-04-01'
                # }
                # result = collection.updateOne(
                #     {'task_id': task_id},
                #     {'$set': update_fields}
                # )
            threading.Thread(target=send_notification, args=(task_id,)).start()
            return jsonify(task), 200
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            del tasks[i]
            # with MongoClient('mongodb://localhost:27017/') as dbh:
                # db = dbh['your_database']
                # collection = db['your_collection']
                # result = collection.deleteOne({'task_id': task_id})
                # if result.deleted_count > 0:
                #     return jsonify({'message': 'Task deleted'}), 204
            return jsonify({'message': 'Task deleted'}), 204
    return jsonify({'error': 'Task not found'}), 404


def send_notification(task_id):
    time.sleep(2)  # Simulate some work (e.g., sending email)
    # Email configuration
    sender_email = "vamsi.preetham.140@gamil.com"
    receiver_email = "vamsi.preetham.140@gamil.com"
    subject = f"Task {task_id} Updated"
    body = f"Notification: Task {task_id} has been updated."
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        # Send the email via SMTP server
        with smtplib.SMTP('localhost', 587) as server:
            server.starttls()
            server.login(sender_email, "your_password")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Notification sent for task {task_id}")
    except Exception as e:
        print(f"Failed to send notification for task {task_id}: {e}")


@app.route('/api/updates')
def updates():
    def event_stream():
        while True:
            if subscribers:
                for subscriber in subscribers:
                    yield f"data: Task updated\n\n"
                time.sleep(1)  # some delay between events

    return Response(event_stream(), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)