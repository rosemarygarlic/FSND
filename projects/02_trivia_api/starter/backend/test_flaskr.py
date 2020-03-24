import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import upgrade

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
        self.db = setup_db(self.app, self.database_path)
 
        # binds the app to the current context
        with self.app.app_context():
            #self.db = SQLAlchemy()
            #self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            #config.set_main_option("script_location", "migrations")
            #command.upgrade(config, "head")

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
            Question('Question to find 8', 'Answer 8',  2, 4),
            Question('Question 9', 'Answer 9', 1, 4),
            Question('Question 10', 'Answer 10',  2, 4),
            Question('Question to find 11', 'Answer 11',  2, 4),
            Question('Question 12', 'Answer 9', 1, 4),
            Question('Question 13', 'Answer 9', 1, 4),
            Question('Question 14', 'Answer 9', 1, 4),
            Question('Question 15', 'Answer 9', 1, 4),
            Question('Question to find 16', 'Answer 9', 1, 4),
            Question('Question 17', 'Answer 9', 1, 4),
            Question('Question 18', 'Answer 9', 1, 4),
            Question('Question 19', 'Answer 9', 1, 4),

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

    def test_404_if_beyond_results(self):
        res = self.client().get('/questions?page=100')

        self.assertEqual(res.status_code, 404)


    def test_get_questions_in_category(self):
        res = self.client().get('/categories/1/questions')
        
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)

        self.assertEqual(len(data['questions']), 12)
        self.assertEqual(data['totalQuestions'], 12)
        self.assertTrue(data['currentCategory'], 'Science')

    def test_404_if_wrong_category(self):
        res = self.client().get('/categories/100/questions')
        self.assertEqual(res.status_code, 404)

    def test_delete_question_successfully(self):
        question_id = 5
        res = self.client().delete('/questions/{}'.format(question_id))
        question = Question.query.get(question_id)
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questionId'], question_id)

    def test_422_if_delete_nonexistent_question(self):
        question_id = 1000
        res = self.client().delete('/questions/{}'.format(question_id))

        self.assertEqual(res.status_code, 422)

    def test_get_categories(self):
        res = self.client().get('/categories')

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)

        self.assertEqual(len(data['categories']), len(self.test_categories))
    
    def test_post_question(self):
        question = 'Added question?'
        res = self.client().post('/questions', json = { 'question' : question,
                                                         'answer' : 'Answer',                      
                                                          'difficulty' : 3,
                                                           'category': 2})

        question = Question.query.filter(Question.question == question).one_or_none()

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questionId'])
        self.assertTrue(question)

    

    def test_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'find'})    

        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['totalQuestions'], 3)
    

    def test_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'nothingtofind'})    

        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['totalQuestions'], 0)









# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()