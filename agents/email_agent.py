import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
import os

load_dotenv()

def handle_email(user_message, context: str = ""):
    """Main entry point — detects action and routes accordingly."""
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    # ── Validate credentials present ─────────────────────────────────────────
    if not os.getenv("EMAIL_ADDRESS") or not os.getenv("EMAIL_PASSWORD"):
        return "❌ Email credentials missing. Please add `EMAIL_ADDRESS` and `EMAIL_PASSWORD` to your `.env` file."

    try:
        llm = get_llm()

        # ── Detect email action ──────────────────────────────────────────────
        action_messages = [
            SystemMessage(content="""
            Classify the email request into one of:
            - send        (user wants to send/write/compose an email)
            - read        (user wants to read/check/view their general inbox)
            - read_from   (user wants to read the latest email FROM a specific person)
            - search      (user wants to find/search emails by keyword/subject)
            - reply       (user wants to reply to an email)

            Examples:
            "Send email to john@gmail.com"              -> send
            "Check my inbox"                            -> read
            "Show my recent emails"                     -> read
            "What did John say in his last email?"      -> read_from
            "Read the latest email from Rahul"          -> read_from
            "Show me the last message from my manager"  -> read_from
            "What's the latest email from boss@co.com"  -> read_from
            "Find emails about invoice"                 -> search
            "Search emails from HR"                     -> search
            "Reply to John's email saying I'll be late" -> reply

            Respond with just the single word: send, read, read_from, search, or reply.
            """),
            HumanMessage(content=user_message)
        ]
        action = llm.invoke(action_messages).content.strip().lower()
        if action not in ("send", "read", "read_from", "search", "reply"):
            action = "send"

        if action == "send":
            return send_email(user_message, llm)
        elif action == "read":
            return read_emails(count=5)
        elif action == "read_from":
            return read_from_person(user_message, llm)
        elif action == "search":
            return search_emails(user_message, llm)
        elif action == "reply":
            return reply_email(user_message, llm)
        else:
            return send_email(user_message, llm)

    except Exception as e:
        return f"⚠️ Email agent error: {str(e)}\n\nPlease check your credentials and try again."


# ── SEND ─────────────────────────────────────────────────────────────────────
def send_email(user_message, llm=None):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    if llm is None:
        llm = get_llm()

    try:
        messages = [
            SystemMessage(content="""
            Extract email details from the user message and respond
            in this exact format, nothing else:
            TO: email@example.com
            SUBJECT: subject here
            BODY: body text here

            Example:
            User: "Send email to john@gmail.com saying hello how are you"
            TO: john@gmail.com
            SUBJECT: Hello
            BODY: Hello, how are you?
            """),
            HumanMessage(content=user_message)
        ]

        response = llm.invoke(messages).content.strip()
        lines = response.split("\n")
        to_email = subject = body = ""

        for line in lines:
            if line.startswith("TO:"):
                to_email = line.replace("TO:", "").strip()
            elif line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                body = line.replace("BODY:", "").strip()

        if not to_email:
            return "❌ I couldn't find a recipient email address. Try: *\"Send email to john@example.com saying hello\"*"

        from_email = os.getenv("EMAIL_ADDRESS")
        password   = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()
        msg["From"]    = from_email
        msg["To"]      = to_email
        msg["Subject"] = subject or "(No subject)"
        msg.attach(MIMEText(body or "(Empty message)", "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())

        return (
            f"✅ **Email sent successfully!**\n"
            f"📬 To: {to_email}\n"
            f"📝 Subject: {subject or '(No subject)'}\n"
            f"💬 Body: {body[:100]}{'...' if len(body) > 100 else ''}"
        )

    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Check your `EMAIL_PASSWORD` (use an App Password for Gmail)."
    except smtplib.SMTPException as e:
        return f"❌ Failed to send email: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error sending email: {str(e)}"


# ── READ INBOX ────────────────────────────────────────────────────────────────
def read_emails(count: int = 5):
    try:
        email_address = os.getenv("EMAIL_ADDRESS")
        password      = os.getenv("EMAIL_PASSWORD")

        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_address, password)
        mail.select("inbox")

        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return "📭 Your inbox is empty."

        latest_ids = mail_ids[-count:][::-1]
        output = f"📬 **Your {min(count, len(mail_ids))} most recent emails:**\n\n"

        for uid in latest_ids:
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject_raw, encoding = decode_header(msg["Subject"])[0]
            subject = (
                subject_raw.decode(encoding or "utf-8")
                if isinstance(subject_raw, bytes)
                else (subject_raw or "(No subject)")
            )
            sender = msg.get("From", "Unknown")
            date   = msg.get("Date", "")[:25]

            body_preview = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_preview = part.get_payload(decode=True).decode(errors="ignore")[:120]
                        break
            else:
                body_preview = msg.get_payload(decode=True).decode(errors="ignore")[:120]

            output += (
                f"📧 **{subject}**\n"
                f"   👤 From: {sender}\n"
                f"   🕐 {date}\n"
                f"   💬 {body_preview.strip()}...\n\n"
            )

        mail.logout()
        return output

    except imaplib.IMAP4.error:
        return "❌ Could not connect to email server. Check your credentials."
    except Exception as e:
        return f"⚠️ Error reading emails: {str(e)}"


# ── SEARCH EMAILS ─────────────────────────────────────────────────────────────
def search_emails(user_message: str, llm=None):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    if llm is None:
        llm = get_llm()

    try:
        kw_messages = [
            SystemMessage(content="""
            Extract the search keyword or sender name from the user's email search request.
            Respond with just the keyword, nothing else.
            Examples:
            "Find emails from john" -> john
            "Search emails about invoice" -> invoice
            """),
            HumanMessage(content=user_message)
        ]
        keyword = llm.invoke(kw_messages).content.strip()

        if not keyword:
            return "❓ I couldn't find a search keyword. Try: *\"Find emails from John\"* or *\"Search emails about invoice\"*"

        email_address = os.getenv("EMAIL_ADDRESS")
        password      = os.getenv("EMAIL_PASSWORD")

        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_address, password)
        mail.select("inbox")

        _, data = mail.search(None, f'(OR SUBJECT "{keyword}" FROM "{keyword}")')
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return f"🔍 No emails found matching **{keyword}**."

        output = f"🔍 **Emails matching '{keyword}':**\n\n"
        for uid in mail_ids[-5:][::-1]:
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject_raw, encoding = decode_header(msg["Subject"])[0]
            subject = (
                subject_raw.decode(encoding or "utf-8")
                if isinstance(subject_raw, bytes)
                else (subject_raw or "(No subject)")
            )
            sender = msg.get("From", "Unknown")
            date   = msg.get("Date", "")[:25]

            output += f"📧 **{subject}**\n   👤 {sender}  |  🕐 {date}\n\n"

        mail.logout()
        return output

    except imaplib.IMAP4.error:
        return "❌ Could not search emails. Check your credentials."
    except Exception as e:
        return f"⚠️ Error searching emails: {str(e)}"


# ── READ LATEST EMAIL FROM A SPECIFIC PERSON ──────────────────────────────────
def read_from_person(user_message: str, llm=None):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    if llm is None:
        llm = get_llm()

    try:
        name_messages = [
            SystemMessage(content="""
            Extract the sender's name or email address the user wants to read from.
            Respond with just the name or email, nothing else.
            Examples:
            "What did John say in his last email?"      -> John
            "Read the latest email from rahul@gmail.com" -> rahul@gmail.com
            "Show me the last message from my manager"  -> manager
            "What's the latest from Priya?"             -> Priya
            """),
            HumanMessage(content=user_message)
        ]
        person = llm.invoke(name_messages).content.strip()

        if not person:
            return "❓ I couldn't identify who you want to read from. Try: *\"What did John say in his last email?\"*"

        email_address = os.getenv("EMAIL_ADDRESS")
        password      = os.getenv("EMAIL_PASSWORD")

        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_address, password)
        mail.select("inbox")

        _, data = mail.search(None, f'FROM "{person}"')
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return f"📭 No emails found from **{person}** in your inbox."

        _, msg_data = mail.fetch(mail_ids[-1], "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject_raw, encoding = decode_header(msg["Subject"])[0]
        subject = (
            subject_raw.decode(encoding or "utf-8")
            if isinstance(subject_raw, bytes)
            else (subject_raw or "(No subject)")
        )

        sender = msg.get("From", "Unknown")
        date   = msg.get("Date", "")[:35]

        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    body_text = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body_text = msg.get_payload(decode=True).decode(errors="ignore")

        body_text = body_text.strip()
        if len(body_text) > 800:
            body_text = body_text[:800] + "\n\n_...message truncated. Ask me to reply if needed._"

        mail.logout()

        return (
            f"📧 **Latest email from {person}**\n\n"
            f"👤 **From:** {sender}\n"
            f"📝 **Subject:** {subject}\n"
            f"🕐 **Date:** {date}\n\n"
            f"─────────────────────────\n\n"
            f"{body_text or '(Empty message)'}"
        )

    except imaplib.IMAP4.error:
        return f"❌ Could not read email from **{person}**. Check your credentials."
    except Exception as e:
        return f"⚠️ Error reading email from {person}: {str(e)}"


# ── REPLY ─────────────────────────────────────────────────────────────────────
def reply_email(user_message: str, llm=None):
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    if llm is None:
        llm = get_llm()

    try:
        reply_messages = [
            SystemMessage(content="""
            Extract reply details from the user message.
            Respond in this exact format:
            TO: name or email to reply to
            BODY: reply body text

            Example:
            User: "Reply to John's email saying I'll be there at 5pm"
            TO: John
            BODY: I'll be there at 5pm.
            """),
            HumanMessage(content=user_message)
        ]
        parsed = llm.invoke(reply_messages).content.strip()
        to_name = body = ""
        for line in parsed.split("\n"):
            if line.startswith("TO:"):
                to_name = line.replace("TO:", "").strip()
            elif line.startswith("BODY:"):
                body = line.replace("BODY:", "").strip()

        if not to_name:
            return "❓ I couldn't identify who to reply to. Try: *\"Reply to John saying I'll be there at 5pm\"*"

        email_address = os.getenv("EMAIL_ADDRESS")
        password      = os.getenv("EMAIL_PASSWORD")

        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_address, password)
        mail.select("inbox")

        _, data = mail.search(None, f'FROM "{to_name}"')
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return f"❌ No emails found from **{to_name}** to reply to."

        _, msg_data = mail.fetch(mail_ids[-1], "(RFC822)")
        raw = msg_data[0][1]
        original = email.message_from_bytes(raw)

        to_email  = original.get("From")
        subject_raw, encoding = decode_header(original["Subject"])[0]
        orig_subject = (
            subject_raw.decode(encoding or "utf-8")
            if isinstance(subject_raw, bytes)
            else (subject_raw or "(No subject)")
        )
        reply_subject = f"Re: {orig_subject}" if not orig_subject.startswith("Re:") else orig_subject

        mail.logout()

        msg = MIMEMultipart()
        msg["From"]    = email_address
        msg["To"]      = to_email
        msg["Subject"] = reply_subject
        msg.attach(MIMEText(body or "(Empty reply)", "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(email_address, password)
            server.sendmail(email_address, to_email, msg.as_string())

        return (
            f"✅ **Reply sent!**\n"
            f"📬 To: {to_email}\n"
            f"📝 Subject: {reply_subject}\n"
            f"💬 {body[:100]}{'...' if len(body) > 100 else ''}"
        )

    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Check your `EMAIL_PASSWORD`."
    except imaplib.IMAP4.error:
        return "❌ Could not find email to reply to. Check your credentials."
    except Exception as e:
        return f"⚠️ Error sending reply: {str(e)}"
