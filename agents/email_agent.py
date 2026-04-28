import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(user_message):
    # Use LLM to extract email details from user message
    from tools.llm_client import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = get_llm()
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

    # Parse the response
    lines = response.split("\n")
    to_email = ""
    subject = ""
    body = ""

    for line in lines:
        if line.startswith("TO:"):
            to_email = line.replace("TO:", "").strip()
        elif line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        elif line.startswith("BODY:"):
            body = line.replace("BODY:", "").strip()

    if not to_email:
        return "Sorry, I couldn't find an email address in your message."

    # Send email via Gmail SMTP
    try:
        from_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return f"✅ Email sent successfully to {to_email}!"

    except Exception as e:
        return f"❌ Failed to send email. Error: {str(e)}"