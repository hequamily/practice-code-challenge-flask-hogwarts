#!/usr/bin/env python3
from models import db, Student, Subject, SubjectEnrollment
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)
migrate = Migrate(app, db)

db.init_app(app)

class Students(Resource):
    def get(self):
        students = Student.query.all()
        response_body = [student.to_dict() for student in students]
        return make_response(jsonify(response_body), 200)
    
api.add_resource(Students, "/students")

class StudentById(Resource):
    def get(self, id):
        student = Student.query.filter(Student.id == id).first()
        if not student:
            response_body = {
                "error": "Student not found"
            }
            return make_response(jsonify(response_body), 404)
        
api.add_resource(StudentById, "/subjects/<int:id>") 

class Subject_Enrollment(Resource):
    def post(self):
        try:
            json_data = request.get_json()
            new_enrollment = Subject_Enrollment(enrollment_year=json_data.get("enrollment_year"), student_id=json_data.get("student_id"), subject_id=json_data.get("subject_id"))
            db.session.add(new_enrollment)
            db.session.commit()
            response_body = new_enrollment.to_dict()

            response_body.update({
                "student": new_enrollment.planet.to_dict(),
                "subject": new_enrollment.scientist.to_dict()

            })
            return make_response(jsonify(response_body), 201)
        except ValueError:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_body), 400)
        
api.add_resource(Subject_Enrollment, "/subject_enrollments")

class StudentEnrollmentById(Resource):
    def delete(self, id):
        try:
            student = Student.query.filter_by(id = id).first()
            
            db.session.delete(student)
            db.session.commit()
            
            return {}, 204
        except: 
            return {"error": "Student Enrollment not found"}, 404
        
api.add_resource(StudentEnrollmentById, "/subject_enrollment/<int:id>")

@app.route('/')
def home():
    return '<h1>🔮 Hogwarts Classes</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)
