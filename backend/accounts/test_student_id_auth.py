"""
Test for Student ID authentication functionality
"""
from django.test import TestCase
from django.contrib.auth import authenticate
from accounts.models import User


class StudentIDAuthenticationTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            student_id='CS2023001',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )

    def test_authenticate_with_username(self):
        """Test authentication using username"""
        user = authenticate(username='testuser', password='testpassword123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.student_id, 'CS2023001')

    def test_authenticate_with_student_id(self):
        """Test authentication using student_id"""
        user = authenticate(username='CS2023001', password='testpassword123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.student_id, 'CS2023001')

    def test_authenticate_with_wrong_password(self):
        """Test authentication with wrong password"""
        user = authenticate(username='testuser', password='wrongpassword')
        self.assertIsNone(user)
        
        user = authenticate(username='CS2023001', password='wrongpassword')
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_user(self):
        """Test authentication with non-existent user"""
        user = authenticate(username='nonexistent', password='testpassword123')
        self.assertIsNone(user)
        
        user = authenticate(username='NONEXISTENT001', password='testpassword123')
        self.assertIsNone(user)

    def test_case_insensitive_authentication(self):
        """Test case-insensitive authentication"""
        # Test username case insensitive
        user = authenticate(username='TESTUSER', password='testpassword123')
        self.assertIsNotNone(user)
        
        # Test student_id case insensitive
        user = authenticate(username='cs2023001', password='testpassword123')
        self.assertIsNotNone(user)

    def test_inactive_user_authentication(self):
        """Test authentication with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        user = authenticate(username='testuser', password='testpassword123')
        self.assertIsNone(user)
        
        user = authenticate(username='CS2023001', password='testpassword123')
        self.assertIsNone(user)

    def test_duplicate_student_id_handling(self):
        """Test handling of potential duplicate student IDs (should not occur due to unique constraint)"""
        # This should raise an IntegrityError due to unique constraint
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                student_id='CS2023001',  # Duplicate student_id
                email='test2@example.com',
                password='testpassword123'
            )
