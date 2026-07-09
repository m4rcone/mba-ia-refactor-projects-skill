import logging
import smtplib

from config.settings import MailConfig
from utils.dates import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host or MailConfig.HOST
        self.port = port or MailConfig.PORT
        self.user = user or MailConfig.USER
        self.password = password or MailConfig.PASSWORD
        self.notifications = []

    def send_email(self, to, subject, body):
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.user, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception:
            logger.exception("Erro ao enviar email para %s", to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
        self.notifications.append(
            {
                "type": "task_assigned",
                "user_id": user.id,
                "task_id": task.id,
                "timestamp": utcnow(),
            }
        )

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n["user_id"] == user_id]
