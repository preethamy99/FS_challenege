import unittest
import json
from flask import Flask
from flask.testing import FlaskClient
from threading import Thread
import time

# Assuming the provided Flask app code is in a module named 'app_module'
from app_module import app, tasks, next_task_id, send_notification

class TaskManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.testing = True

    def test_get_tasks(self):
        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), len(tasks))

    def test_create_task(self):
        global next_task_id
        new_task = {
            'title': 'Test Task',
            'due_date': '2024-04-01'
        }
        response = self.client.post('/api/tasks', data=json.dumps(new_task), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['id'], next_task_id - 1)
        self.assertEqual(response.json['title'], new_task['title'])
        self.assertEqual(response.json['due_date'], new_task['due_date'])

    def test_update_task(self):
        task_id = 1
        updated_task = {
            'title': 'Updated Task',
            'completed': True
        }
        response = self.client.put(f'/api/tasks/{task_id}', data=json.dumps(updated_task), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], task_id)
        self.assertEqual(response.json['title'], updated_task['title'])
        self.assertEqual(response.json['completed'], updated_task['completed'])

    def test_delete_task(self):
        task_id = 1
        response = self.client.delete(f'/api/tasks/{task_id}')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/tasks')
        task_ids = [task['id'] for task in response.json]
        self.assertNotIn(task_id, task_ids)

    def test_send_notification(self):
        task_id = 1
        thread = Thread(target=send_notification, args=(task_id,))
        thread.start()
        thread.join()
        # Check if the notification was sent (this is a simple print statement in the provided code)
        # In a real-world scenario, we would check the actual notification mechanism (e.g., email sent)

if __name__ == '__main__':
    unittest.main()