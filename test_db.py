# coding: utf8
from arguments import make_app
app = make_app()
from arguments import db
from arguments.database.datamodel import *

db.drop_all()
db.create_all()

s = db.session

ug1 = UserGroup(name="Deppengruppe")

u1 = User(login_name="abc", display_name="testuser")

u2 = User(login_name="def", display_name="Egon")

ug1.users.extend([u1, u2])

t1 = Tag(tag="Tag1")
t2 = Tag(tag="Tag2")
t3 = Tag(tag="Täääg3")

q1 = Question(url="Q1", title="Ein Titel", details="blah")

q1_counter = Question(url="Q1Counter", title="Gegenantrag zu Q1", details="will was anderes")
q1_counter_assoc = QuestionAssociation(left=q1, right=q1_counter, association_type="counter")
s.add(q1_counter_assoc)

q1_counter_2 = Question(url="Q1Counter2", title="Noch ein Gegenantrag zu Q1", details="will was ganz anderes")
q1_counter_2_assoc = QuestionAssociation(left=q1, right=q1_counter_2, association_type="counter")
s.add(q1_counter_2_assoc)

q1_change = Question(url="Q1Change", title="Änderungsantrag zu Q1", details="will was ändern")
q1_change_assoc = QuestionAssociation(left=q1, right=q1_change, association_type="change")
s.add(q1_change_assoc)

arg1 = Argument(question=q1, author=u1, title="Ein Pro-Argument", url="dafür-ööö",
                abstract="dafür abstract", details="dafür", argument_type="pro")

ca1_1 = Argument(question=q1, author=u2, title="Gegenargument", url="ca1_1", 
                 argument_type="con", abstract="Abstract ca_1_1", details="mäh", parent=arg1)

arg2 = Argument(question=q1, author=u2, title="Ein zweites Pro-Argument", url="dafuer",
                abstract="dafür!!!", argument_type="pro")

arg3 = Argument(question=q1, author=u1, title="Ein Contra-Argument", url="dagegen-ää",
                abstract="dagegen abstract", details="dafür", argument_type="con")

q1.arguments.extend([arg1, arg2, arg3, ca1_1])
q1.tags.extend([t1, t2])
s.add(q1)

q2 = Question(url="A2", title="Noch Ein Titel", details="blah")
q2.tags.append(t3)
s.add(q2)

qv1 = QuestionVote(user=u1, question=q1)
s.add(qv1)
qv2 = QuestionVote(user=u1, question=q2)
s.add(qv2)
qv3 = QuestionVote(user=u2, question=q1)
s.add(qv3)

qv1 = ArgumentVote(user=u1, argument=arg1, value=1)
s.add(qv1)
qv2 = ArgumentVote(user=u1, argument=arg2, value=-1)
s.add(qv2)
qv3 = ArgumentVote(user=u2, argument=arg1, value=1)
s.add(qv3)

s.commit()
