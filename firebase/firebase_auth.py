import pyrebase
from firebase_admin import auth, credentials, initialize_app
import firebase_admin
from .firebase_config import FIREBASE_CONFIG

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Pyrebase
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth_instance = firebase.auth()

class FirebaseAuth:
    @staticmethod
    def sign_up_with_email(email, password):
        """
        Sign up a new user with email and password
        """
        try:
            # Create user in Firebase
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False
            )
            
            # Send email verification
            verification_link = auth.generate_email_verification_link(email)
            # Here you would typically send this link via your email service
            
            return {
                "success": True,
                "user_id": user.uid,
                "verification_link": verification_link
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def sign_in_with_email(email, password):
        """
        Sign in with email and password
        """
        try:
            user = auth_instance.sign_in_with_email_and_password(email, password)
            # Check if email is verified
            user_info = auth.get_user(user['localId'])
            
            if not user_info.email_verified:
                return {
                    "success": False,
                    "error": "Email not verified. Please verify your email first."
                }
                
            return {
                "success": True,
                "user": user
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def verify_email(verification_code):
        """
        Verify email with verification code
        """
        try:
            # Check if the verification code is valid
            info = auth.verify_id_token(verification_code)
            user = auth.get_user(info['uid'])
            
            # Update user's email verification status
            auth.update_user(
                user.uid,
                email_verified=True
            )
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def sign_in_with_google(id_token):
        """
        Sign in with Google
        """
        try:
            # Verify the Google ID token
            decoded_token = auth.verify_id_token(id_token)
            
            # Get or create user
            try:
                user = auth.get_user_by_email(decoded_token['email'])
            except:
                user = auth.create_user(
                    email=decoded_token['email'],
                    email_verified=True,
                    display_name=decoded_token.get('name'),
                    photo_url=decoded_token.get('picture')
                )
            
            # Create custom token for the client
            custom_token = auth.create_custom_token(user.uid)
            
            return {
                "success": True,
                "user": user,
                "token": custom_token
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def sign_out(id_token):
        """
        Sign out user
        """
        try:
            # Revoke refresh tokens for user
            decoded_token = auth.verify_id_token(id_token)
            auth.revoke_refresh_tokens(decoded_token['uid'])
            
            return {
                "success": True,
                "message": "Successfully signed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

