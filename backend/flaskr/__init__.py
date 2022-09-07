import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resource={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,PUT,PATCH'
        )
        return response

    @app.route('/api/v1.0/categories', methods=["GET"])
    def get_categories():
        '''an endpoint to handle GET request for all available categories'''
        try:
            categories = Category.query.order_by(Category.id).all()
            print(categories)
            dict_categories = {}
            for category in categories:
                dict_categories[category.id] = category.type
            return jsonify({
                'success': True,
                'categories': dict_categories
            })
        except Category.DoesNotExist:
            abort(404)

    @app.route('/api/v1.0/questions', methods=['GET'])
    def get_questions():
        """ Create an endpoint to handle GET requests for questions, """
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': {
                category.id: category.type
                for category in categories
            },
            'current_category': None
        })

    @app.route('/api/v1.0/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Create an endpoint to DELETE question using a question ID"""
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Question.DoesNotExist:
            abort(404)

    @app.route('/api/v1.0/questions', methods=['POST'])
    @cross_origin()
    def create_new_question():
        """  Create an endpoint to POST a new question,
        which will require the question and
        answer text,category, and difficulty score."""

        body = request.get_json()
        if body is None:
            abort(400)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        try:
            question = Question(question=new_question,
                                answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)

            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except:
            abort(422)

    @app.route('/api/v1.0/questions/search', methods=['POST'])
    @cross_origin()
    def search_for_questions():
        """
        Create a POST endpoint to get questions based on a search term
        """
        body = request.get_json()
        search_term = body.get('search_term', None)

        try:
            questions = Question.query.filter(
                Question
                .question.ilike(f'%{search_term}%')).all()
            return jsonify({
                'questions': [question.format() for question in questions],
                'Success': True,
                'total_questions': len(questions),
                'current_category': None
            })
        except Question.DoesNotExist:
            abort(404)

    @app.route('/api/v1.0/categories/<int:question_category>/questions')
    def get_question_under_a_category(question_category):
        ''' Get questions based on specified category'''
        try:
            questions_under_category = Question.query\
                .filter(Question.category == question_category)\
                .order_by('id').all()

            if len(questions_under_category) == 0:
                abort(404)

            return jsonify({
                'questions': [
                    question.format()
                    for question in questions_under_category
                ],
                'total_questions': len(questions_under_category),
                'current_category': question_category,
                'success': True,
            })

        except Question.DoesNotExist:
            abort(400)

    @app.route('/api/v1.0/quizzes', methods=['POST'])
    def next_question():
        """ Sends a post request in order to get the next question
        This endpoint should take category and previous question parameters
        and return a random questions within the given category
        """

        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if quiz_category['id'] == 0:
            questions = Question.query.all()
            question_list = [each_question.id for each_question in questions
                             if each_question.id not in previous_questions]

            random_question_id = random.choice(question_list)

            random_questions = Question.query.filter(
                Question.id == random_question_id).first()

            return jsonify({
                "success": True,
                "question": random_questions.format()
            })

        else:
            questions = Question.query.filter(
                Question.category == quiz_category['id']).all()

            question_list = [each_question.id for each_question in questions
                             if each_question.id not in previous_questions]

            random_question_id = random.choice(question_list)

            random_questions = Question.query.filter(
                Question.id == random_question_id).first()

            return jsonify({
                "success": True,
                "question": random_questions.format()
            })

# error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal service error"
        }), 500

    return app
