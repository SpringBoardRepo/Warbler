from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from models import Likes, db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql://localhost/warbler-test?user=postgres&password=postgresql"


db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class MessageTestModel(TestCase):

    def setUp(self):

        User.query.delete()
        Message.query.delete()

        user = User.signup(email='test111@gmail.com',
                           username='test1111', password='test111', image_url=None)

        db.session.add(user)
        db.session.commit()
        user.id = 111
        user_id = user.id

        self.user_id = user_id
        self.user = user

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):

        msg = Message(text="Hello!! test message", user_id=self.user_id)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "Hello!! test message")

    def test_messsage_likes(self):

        msg1 = Message(text="c", user_id=self.user_id)

        msg2 = Message(text="test message", user_id=self.user_id)

        db.session.add_all([msg1, msg2])
        db.session.commit()
        msg1.id = 101
        msg_id = msg1.id
        self.user.likes.append(msg1)
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == self.user_id).all()
        self.assertEqual(len(self.user.likes), 1)
        self.assertEqual(like[0].message_id, msg_id)
