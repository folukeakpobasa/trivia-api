import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgresql://{}@{}/{}".format(
            DB_USER, 'localhost:5432', DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get('/api/v1.0/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'], 3)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/api/v1.0/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)
        categories = Category.query.all()

        self.assertEqual(res.status_code, 200)
        self.assertTrue((categories[0], 1))
        self.assertTrue(categories[1], "History")

    def test_get_categories_fails(self):
        res = self.client().post('/api/v1.0/categories')
        data = json.loads(res.data)
        categories = Category.query.all()

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        res = self.client().delete('/api/v1.0/question/2')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_422_delete_question_failed(self):
        res = self.client().delete('/api/v1.0/question/500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_question(self):
        new_question = {
            'question': 'new question',
            'answer': 'answer',
            'category': 1,
            'difficulty': 1
        }
        res = self.client().post('/api/v1.0/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'], 30)

    def test_405_if_create_question_not_allowed(self):
        res = self.client().post('/api/v1.0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_200_sarch_question(self):
        new_search = {
            "search_term": "",
        }
        res = self.client().post('/api/v1.0/questions/search', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'], 45)

    def test_404_sarch_question(self):
        new_search = {
            "search_term": "",
        }
        res = self.client().get('/api/v1.0/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertTrue(data['message'], "resource not found")

    def test_retrieve_questions_based_on_category(self):
        res = self.client().get('/api/v1.0/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'], 10)

    def test_retrieve_questions_based_on_category_fails(self):
        res = self.client().get('/api/v1.0/categories/<one>/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_play_quiz_fails(self):
        next_play = {
        "previous question": [],
        "quiz_category": {
            "id": 1,
            "type": "Science"
            },
        }
        res = self.client().get('/api/v1.0/quizzes', json= next_play)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
