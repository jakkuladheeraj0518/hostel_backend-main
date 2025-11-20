"""Safe email test helper.

Prints current SMTP/email configuration (masked) and shows the email content that would be
sent. Only attempts to send if `--send` is provided and the EmailService reports configured.

Usage:
  python -m scripts.send_test_email --to you@example.com --subject "Test" --body "Hello" [--send]
"""
import argparse
import sys
from app.services.email_service import EmailService
from app.config import settings


def mask(val: str | None) -> str | None:
    if not val:
        return None
    s = str(val)
    if len(s) <= 4:
        return "****"
    return s[:2] + "*" * (len(s) - 4) + s[-2:]


def print_config(svc: EmailService):
    print("EmailService.is_configured():", svc.is_configured())
    print("smtp_host:", getattr(settings, 'SMTP_HOST', None) or getattr(settings, 'EMAIL_HOST', None))
    print("smtp_port:", getattr(settings, 'SMTP_PORT', None) or getattr(settings, 'EMAIL_PORT', None))
    print("smtp_user:", mask(getattr(settings, 'SMTP_USERNAME', None) or getattr(settings, 'EMAIL_USER', None)))
    print("smtp_pass_present:", bool(getattr(settings, 'SMTP_PASSWORD', None) or getattr(settings, 'EMAIL_PASS', None)))
    print("from_email:", getattr(settings, 'SMTP_FROM_EMAIL', None) or getattr(settings, 'EMAIL_FROM', None))
    print("use_tls:", getattr(settings, 'SMTP_USE_TLS', None) if hasattr(settings, 'SMTP_USE_TLS') else getattr(settings, 'EMAIL_USE_TLS', False))
    print("use_ssl:", getattr(settings, 'SMTP_USE_SSL', None) if hasattr(settings, 'SMTP_USE_SSL') else getattr(settings, 'EMAIL_USE_SSL', False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--send", action="store_true", help="Actually attempt to send the email if configured")
    args = parser.parse_args()

    svc = EmailService()
    print_config(svc)
    print("\n--- Email Preview ---")
    print(f"To: {args.to}")
    print(f"From: {svc.from_email or '<not configured>'}")
    print(f"Subject: {args.subject}")
    print("Body:\n", args.body)
    print("--- End Preview ---\n")

    if args.send:
        if not svc.is_configured():
            print("Email service is not configured. Aborting send.")
            sys.exit(2)
        print("Attempting to send email...")
        ok = svc.send_email(args.to, args.subject, args.body, args.body)
        print("Send result:", ok)
        sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
