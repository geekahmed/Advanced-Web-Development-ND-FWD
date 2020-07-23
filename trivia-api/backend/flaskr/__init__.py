import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Paginating Data Handler
def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    currentQuestions = questions[start:end]

    return currentQuestions

# Utility to get random questions
def getRandomQuestion(questions):
    return random.choice(questions)

# Utility to check if question appears once before
def checkQuestionUsage(question, previous):
    used = False
    for q in previous:
        if q == question.id:
            used = True
    return used

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    # set up CORS, allowing all origins
    CORS(app, resources={r"/": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH, OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def getCategories():
        # Get all categories from the database
        selection = Category.query.order_by(Category.id).all()
        categories = [category.format() for category in selection]
        if len(selection) == 0:
            abort(404)

        # Returning the desired output
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
    '''

    # Get Request Handler for all questions
    @app.route('/questions', methods=['GET'])
    def getQuestions():
        selection = Question.query.order_by(Question.id).all()
        currentQuestions = paginate_books(request, selection)

        if len(currentQuestions) == 0:
            abort(404)

        cats = Category.query.all()
        categoriesName = [cat.type for cat in cats]

        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'categories': categoriesName,
            'total_questions': len(selection)
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def deleteQuestion(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
    '''
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
    '''

    @app.route('/questions', methods=['POST'])
    def createQuestion():
        body = request.get_json()
        try:
            search = body.get('search', None)
            if search:
                selection = Question.query.filter(Question.question.ilike("%{}%".format(search))).all()
                if len(selection) == 0:
                    abort(404)
                currentQuestions = paginate_books(request, selection)
                return jsonify({
                    'success': True,
                    'questions': currentQuestions,
                    'total_questions': len(Question.query.all())
                })
            else:
                questionText = body.get('question')
                answerText = body.get('answer')
                categoryText = body.get('category')
                difficultyNo = int(body.get('difficulty'))
                if (questionText is None) or (categoryText is None) or (answerText is None) or (difficultyNo is None):
                    abort(400)

                question = Question(question=questionText, answer=answerText, category=categoryText,
                                    difficulty=difficultyNo)
                question.insert()
                selection = Question.query.order_by(Question.id).all()
                currentQuestions = paginate_books(request, selection)

                return jsonify({
                    'success': True,
                    'questions': currentQuestions,
                    'total_questions': len(selection)
                })
        except:
            abort(422)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def getCategoryQuestions(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        currentQuestions = paginate_books(request, questions)

        if len(currentQuestions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'total_questions': len(Question.query.all())
        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
    '''

    @app.route('/play', methods=['POST'])
    def playQuizGame():
        body = request.get_json()
        previousQuestions = body.get('previous_questions')
        category = body.get('quiz_category')
        if (category is None) or (previousQuestions is None):
            abort(400)

        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        totalQuestions = len(questions)

        randQuestion = getRandomQuestion(questions)
        while checkQuestionUsage(randQuestion, previousQuestions):
            randQuestion = getRandomQuestion(questions)
            if len(previousQuestions) == totalQuestions:
                return jsonify({
                    'success': True
                })
        return jsonify({
            'success': True,
            'question': randQuestion.format()
        })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
    '''

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
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def notAllowedMethod(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'not allowed method'
        }), 405

    return app
