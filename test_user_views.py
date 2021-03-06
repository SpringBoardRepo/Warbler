
from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import Follows, db, connect_db, Message, User


os.environ['DATABASE_URL'] = "postgresql://localhost/warbler-test?user=postgres&password=postgresql"


app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class UserTestViews(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()
        self.client = app.test_client()

        user = User.signup(email="asdf@abc.com", username='test1120',
                           password='test1120', image_url=None)

        u1 = User.signup(email="test@test.com", username='xyz',
                         password="password", image_url=None)

        db.session.add_all([user, u1])

        user.id = 110
        self.user_id = user.id
        self.user = user

        u1.id = 777
        self.u1_id = u1.id
        self.u1 = u1
        db.session.commit()
        f1 = Follows(user_being_followed_id=self.user_id,
                     user_following_id=self.u1_id)

        db.session.add(f1)
        db.session.commit()

    def test_login_user_follower(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        res = c.get(f'/users/{self.user_id}/followers')

        self.assertEqual(res.status_code, 200)
        self.assertIn('@test', str(res.data))

    def test_login_user_following(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        res = c.get(f'/users/{self.u1_id}/following')

        self.assertEqual(res.status_code, 200)
        self.assertIn('@xyz', str(res.data))

    def test_unathorized_user_following(self):

        with self.client as c:
            res = c.get(f'/users/{self.user_id}/following',
                        follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn('@xyz', str(res.data))
            self.assertIn('Access unauthorized', str(res.data))

    def test_unathorized_user_follower(self):

        with self.client as c:
            res = c.get(f'/users/{self.user_id}/followers',
                        follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn('@test', str(res.data))
            self.assertIn('Access unauthorized', str(res.data))

    def test_add_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        res = c.post('/messages/new',
                     data={'text': 'Message to yourself'})

        self.assertEqual(res.status_code, 302)

    def test_delete_msg_when_user_logged_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

        msg = Message(text='Test User message', user_id=self.user_id)
        db.session.add(msg)
        msg.id = 121
        db.session.commit()

        res = c.post(f'/messages/{msg.id}/delete')

        self.assertEqual(res.status_code, 302)

    def test_delete_msg_when_user_logged_out(self):
        with self.client as c:
            msg = Message(text='Test User message', user_id=self.user_id)
            db.session.add(msg)
            msg.id = 121
            db.session.commit()

            res = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', str(res.data))

    def test_adding_msg_as_another_user(self):
        with self.client as c:

            res = c.post('/messages/new',
                         data={'text': 'Message as another user'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', str(res.data))

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
