import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "sqlite://"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
           # self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.test_categories = [
            Category('Science'),
            Category('Art')
        ]    

        for c in self.test_categories:
            c.insert()
        
        self.test_questions = [
            Question('Question 1', 'Answer 1',  2, 4),
            Question('Question 2', 'Answer 2',  1, 4),
            Question('Question 3', 'Answer 3',  1, 4),
            Question('Question 4', 'Answer 4',  2, 4),
            Question('Question 5', 'Answer 5',  2, 4),
            Question('Question 6', 'Answer 6',  1, 4),
            Question('Question 7', 'Answer 7',  2, 4),
            Question('Question 8', 'Answer 8',  2, 4),
            Question('Question 9', 'Answer 9', 1, 4),
            Question('Question 10', 'Answer 10',  2, 4),
            Question('Question 11', 'Answer 11',  2, 4)

        ]

          

        for q in self.test_questions:
            q.insert()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get('/questions?page=1')

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)

        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['totalQuestions'], len(self.test_questions))
        self.assertEqual(len(data['categories']), len(self.test_categories))
        self.assertTrue(data['currentCategory'])

    def test_404_if_beyond_results(self):
        res = self.client().get('/questions?page=100')

        self.assertEqual(res.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()