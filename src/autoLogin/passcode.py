# coding=utf8
import poplib
from email import parser

USER = ""
HOST = ""
PASSWORD = ""


def is_essh_email(content):
    for piece in content:
        if piece.startswith('Subject: Essh Passcode Mail'):
            return True
    return False


def get_passcode_from_email(host, username, password):
    """Retrieve the last essh passcode

    :rtype : str
    """
    pp = poplib.POP3(host)
    pp.user(username)
    pp.pass_(password)

    count, size = pp.stat()

    passcode = ""
    mails = range(count - 12, count + 1)[::-1]
    for mail in mails:
        message = pp.retr(mail)[1]
        if is_essh_email(message):
            # Concat message pieces:
            message = "\n".join(message)
            # Parse message into an email object:
            message = parser.Parser().parsestr(message)
            # content format: user: username passcode: 000111
            content = message.get_payload(decode=True)
            pos = content.find("passcode: ")
            if pos > 0:
                passcode = content[pos + len("passcode:"):].strip()
                break
    pp.quit()
    return passcode


def set_user(user):
    global USER
    USER = user


def set_host(host):
    global HOST
    HOST = host


def set_password(pwd):
    global PASSWORD
    PASSWORD = pwd


