class Student:

    no_of_students = 0
    department_code = 'IT17'

    def __init__(self, name, regno):
        self.name = name
        self.regno = regno
        Student.no_of_students +=1


    def details(self):
        return 'Name: {}. Register Number: {}'.format(self.name,self.regno)
    @classmethod
    def from_string(cls,str1):
        first, last = str1.split(',')
        return cls(first, last)
    @staticmethod
    def stand_alone():
        return 'Thanks'

class Senate(Student):

    def __init__(self,name, regno, position):
        super().__init__(name, regno)
        self.position = position

class Teacher(Student):
    def __init__(self,name,regno,students = None):
        super().__init__(name,regno)

        if students is None:
            self.students = []
        else:
            self.students = students

    def add_student(self, student):
        if student not in self.students:
            self.students.append(student)

    def remove_student(self,student):
        if student in self.students:
            self.students.remove(student)

    def print_students(self):
        for stu in self.students:
            print('-->',stu.name)


student1 = Student('Suzannah','15PIT23')
print(Student.details(student1))

new_student = Student.from_string('Niranjana,16PIT13')
print(new_student.details())

print(Student.stand_alone())

new_student.department_code = 'IT18'

print(Student.department_code)
print(new_student.department_code);

print(new_student.__dict__)

print(Student.no_of_students)

senate1 = Senate('Helen','16VSC22','President')
print(senate1.__dict__)


teacher1 = Teacher('Shanthi','16CSC11',[senate1])
print(teacher1.name)

print(teacher1.print_students())
teacher1.add_student(new_student)
print(teacher1.print_students())
teacher1.add_student(student1)
teacher1.remove_student(new_student)
print(teacher1.print_students())












