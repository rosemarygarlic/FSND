import os
import random

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. 
    Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})
  
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """ 
    Helper to paginate question list:
    """
    def paginate(request, questions):
        page = request.args.get('page', 1, int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        if start > len(questions):
            abort(404)
        return [q.format() for q in questions[start:end]]

    """
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        """Returns list of all categories from the database."""
        all_categories = Category.query.all()
        return jsonify({
            'success': True,
            'categories': {c.id:c.type for c in all_categories}
        })

    """
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    """
    @app.route('/questions')
    def list_questions():
        """Return the list of all the questions from the database, 
        total number of questions,
        and list of all the categories 
        """
        all_questions = Question.query.all()
        all_categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'success': True,
            'questions': paginate(request, all_questions),
            'totalQuestions': len(all_questions),
            'categories': {c.id:c.type for c in all_categories},
        })

    """
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    """
    @app.route('/questions/<int:question_id>', methods = ['DELETE'])
    def delete_question(question_id):
        """Delete the given question from the database.
        Arguments:
        question_id -- id of the question to delete
        """
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(422)

            question.delete()
        except:
            abort(422)
        else:
            return jsonify({
                'success': True, 
                'questionId': question_id
            })

    """
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    """
    @app.route('/questions', methods = ['POST'])
    def create_question():
        """Search questions if searchTerm parameter is in the request body, 
        otherwise insert a new question with given parameters into database"""
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        
        search_term = body.get('searchTerm', None)

        if search_term is not None:
          search_results = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_term))).all()
          return jsonify({
              'success': True,
              'questions': paginate(request, search_results), 
              'totalQuestions': len(search_results),
          })

        if not all([new_question, new_answer, new_difficulty, new_category]):
          abort(400)

        try:
            question = Question(new_question, new_answer, 
                                new_category, new_difficulty)
            question.insert()        
        except:
            abort(422)
        else:
            return jsonify({
               'success': True, 
                'questionId': question.id
            })
      
    """
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    """

    """
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    """
    @app.route('/categories/<int:category_id>/questions')
    def show_category_questions(category_id):
      """Return all questions in a given category.
      Arguments:
      category_id -- id of the category
      """
      category = Category.query.get(category_id)

      if category is None:
        abort(404)

      questions = Question.query.filter(Question.category == category_id).all()

      return jsonify({
        'success': True,
        'questions': paginate(request, questions),
        'totalQuestions': len(questions),
        'currentCategory': Category.query.get(category_id).type
      })

    """
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_quesion():
        """Return a random question from a given category,
        which is not included in the list of given previous questions
        """
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if not quiz_category or quiz_category['id'] is None:
            abort(400)

        if int(quiz_category['id']) == 0:
            category_questions = Question.query.all()
        else:
            category = Category.query.get(quiz_category['id'])
            if not category:
                abort(422)
            category_questions = Question.query.filter(
                Question.category == quiz_category['id']).all()
      
        category_questions_ids = list(set([ q.id for q in category_questions]) 
                                      - set(previous_questions))
        
        if not category_questions_ids:
            return jsonify({'success': True})
        
        current_question = Question.query.get(
            random.choice(category_questions_ids))

        return jsonify({
            'success': True,
            'question': current_question.format() 
        })

    """
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
              'success': False,
              'error': 404,
              'message': 'resource not found'
        }), 404
    
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
              'success': False,
              'error': 422,
              'message': 'unprocessable request'
        }), 422

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
              'success': False,
              'error': 400,
              'message': 'bad request'
        }), 400
  
    return app

    