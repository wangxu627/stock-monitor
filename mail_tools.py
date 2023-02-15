import smtplib
from email.mime.text import MIMEText


def send_mail(to_list, sub, content):
    mail_host = "smtp.qq.com"
    mail_user = "1525496905@qq.com"
    mail_pass = "mupzmesplzydiicd"

    me = f"<{mail_user}>"
    msg = MIMEText(content, _subtype="html", _charset="utf-8")
    msg["Subject"] = sub
    msg["From"] = me
    msg["To"] = ",".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False
