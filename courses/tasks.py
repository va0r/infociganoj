from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_subscription_notification(user_email, course_name):
    subject = 'Вы успешно подписались на курс'
    message = f'Вы успешно подписались на курс "{course_name}". Спасибо за подписку!'
    from_email = None
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_unsubscription_notification(user_email, course_name):
    subject = 'Вы успешно отписались от курса'
    message = (f'Вы успешно отписались от курса "{course_name}". '
               f'Мы надеемся, что вы найдете другие интересные курсы у нас!')
    from_email = None
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_course_update_notification(course_name, user_emails):
    subject = 'Обновление курса'
    message = f'Курс "{course_name}" был обновлен. Проверьте новый материал!'
    from_email = None
    recipient_list = user_emails  # Список адресов получателей

    send_mail(subject, message, from_email, recipient_list)
