from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Combine user data and timestamp to create a unique hash value
        return f"{user.pk}{timestamp}{user.is_active}"

email_verification_token = EmailVerificationTokenGenerator()
