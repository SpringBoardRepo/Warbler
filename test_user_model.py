"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database


from sqlalchemy import exc
from app import app
from unittest import TestCase
from models import db, User, Message, Follows
import os

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        user1 = User.signup(email='Testuser1@gmail.com',
                            username='Testuser1', password='Testuser1pass', image_url=None)

        db.session.add(user1)
        db.session.commit()
        user1.id = 111
        user1_id = user1.id

        user2 = User.signup(email='Testuser2@gmail.com',
                            username='Testuser2', password='Testuser2pass', image_url=None)

        db.session.add(user2)
        db.session.commit()

        user2.id = 112
        user2_id = user2.id

        u1 = User.query.get(user1_id)
        u2 = User.query.get(user2_id)

        self.user1_id = user1_id
        self.u1 = u1
        self.user2_id = user2_id
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        """User is following another user """

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_user_signup(self):

        testuser = User.signup(email='testtestuser@gmail.com',
                               username='Testsignup', password='usersignup', image_url=None)

        db.session.add(testuser)
        db.session.rollback()
        db.session.commit()

        testuser.id = 222222

        self.assertEqual(testuser.id, 222222)
        self.assertEqual(testuser.username, 'Testsignup')
        self.assertEqual(testuser.email, 'testtestuser@gmail.com')
        self.assertTrue(testuser.password.startswith('$2b$'))

    def test_user_signup_fail_invalid_username(self):

        test = User.signup(email='testtestuser@gmail.com',
                           username=None, password='usersignup', image_url=None)

        db.session.add(test)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_signup_fail_invalid_email(self):

        testemail = User.signup(email=None,
                                username='testtesttest', password='usersignup', image_url=None)

        db.session.add(testemail)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authrentication(self):

        u = User.query.get(self.user1_id)

        u.authenticate(username=u.username, password=u.password)
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user1_id)

    def test_authrentication_fail(self):
        self.assertFalse(User.authenticate(
            username="worng", password='wrongpass'))
