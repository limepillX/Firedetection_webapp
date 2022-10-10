import random
import time
import numpy as np

from faker import Faker

from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime

from django.views.generic import UpdateView
from rest_framework import generics
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from .models import *
from .forms import *
import smtplib
import telegram
import telegram_send


def Login(request):
    form = AuthForm

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user = request.user
            api_key = '5731188606:AAHxtwB5CJ16Z9pN3yPNyQmoYK2YDb4K3_E'
            user_id = user.telegram
            last_login = datetime.strftime(user.last_login, "%d.%m.%Y (%H:%M)")
            message_text = f'Здравствуйте, {user.first_name} {user.last_name}.\n{last_login} в вашу учётную запись выполнен вход. Если это были не Вы, обратитесь к администратору для смены пароля.'
            # message_text = f'Внимание, {user.first_name} {user.last_name}.\n{last_login} в помещении 1 (камера 1) обнаружено возгорание. Примите необходимые меры!.'

            bot = telegram.Bot(token=api_key)
            bot.send_message(chat_id=user_id, text=message_text)
            connection = smtplib.SMTP('smtp.gmail.com', 587)
            connection.starttls()
            connection.login(
                user='select.issnotify@gmail.com',
                password='wtapqvfobhblwqin'
            )
            user_email = str(user.email)
            from_addr = 'select.issnotify@gmail.com'
            to_addr = user_email
            subj = 'Оповещение системы безопасности'
            msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (from_addr, to_addr, subj, message_text)
            connection.sendmail(from_addr, to_addr, msg.encode('utf-8'))
            connection.close()
            return redirect('camera')
    user = request.user
    if request.user.is_authenticated:
        return redirect('camera')
    data = {'form': form, 'user': user}
    return render(request, 'login.html', data)


def Logout(request):
    logout(request)
    return redirect('login')


def Settings(request):
    if request.user.is_anonymous:
        return redirect('login')

    user = request.user
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            return redirect('settings/1')
        super(Event, self).save(*args, **kwargs)
    data = {'form': form}

    return render(request, 'settings.html', data)


class ProfileUpdate(UpdateView):
    form_class = ProfileForm
    model = User
    template_name = 'settings.html'
    current_user = int()

    def dispatch(self, request, *args, **kwargs):
        print(request.user.pk)
        self.current_user = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.current_user
        print(self.current_user)
        return context


def Camera(request):
    if request.user.is_anonymous:
        return redirect('login')
    return render(request, 'camera.html')


from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading


@gzip.gzip_page
def Cam(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'cam.html')


# to capture video class
class VideoCamera(object):

    def __init__(self):
        CameraStatus.objects.all().delete()
        self.TG_MESSAGES = True
        self.MOVEMENT_DETECTION = True
        self.SENSITIVITY = 1
        self.count = 0
        self.times_count = 0
        self.times_in_sec = 0
        self.start = time.time()
        self.send_flag = True
        self.seconds = 0
        self.first_time = True
        self.img_prev = 0
        self.time_after_move = 0
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.fire_cascade = cv2.CascadeClassifier('main/models/cascade_1.xml')
        CameraStatus(message="Мониторинг запущен", importance=1, time=datetime.now().time()).save()
        (self.grabbed, self.frame) = self.cap.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.cap.release()

    def get_frame(self):

        if time.time() - self.start >= 1:
            self.time_after_move += 1
            self.start = time.time()
            self.seconds += 1
            if self.seconds > 2:
                self.send_flag = True
            self.times_count = 0
            self.times_in_sec = 0
        ret, img = self.cap.read()
        img = cv2.resize(img, (1280, 960), interpolation=cv2.INTER_AREA)

        cv2.putText(img, f'Sensitivity={self.SENSITIVITY}', (0, 50), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2, 2)

        if self.MOVEMENT_DETECTION:
            cv2.putText(img, f'MOVEMENT DETECTION ON', (0, 80), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2, 2)
        cv2.putText(img, f'Detections/sec={self.times_in_sec}', (0, 110), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2,
                    2)

        fire = self.fire_cascade.detectMultiScale(img, 12, 5)

        for (x, y, w, h) in fire:

            self.times_count += 1
            self.times_in_sec += 1

            if self.times_count >= 1 * 10 * 0.01:
                self.count += 1
                CameraStatus(message=f'[{self.count}]Обнаружен огонь!', importance=4, time=datetime.now().time()).save()
                cv2.putText(img, 'Fire', (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2, 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # highlight the area of image with fire
                times_count = 0

                if self.TG_MESSAGES:
                    if self.send_flag:
                        self.send_flag = False
                        self.seconds = 0
                        bot = telegram.Bot(token="5731188606:AAHxtwB5CJ16Z9pN3yPNyQmoYK2YDb4K3_E")
                        pic_name = f"alert-{time.time()}"
                        CameraStatus(importance=3, message='Пользователь оповещён', time=datetime.now().time())
                        cv2.imwrite(f'main/telegram_photos/{pic_name}.png', img)
                        send_img = open(f"main/telegram_photos/{pic_name}.png", 'rb')
                        text = f"""Внимание, Даниил.
{datetime.now().date()} {str(datetime.now().time())[:8]} в помещении 1 (камера 1) обнаружено возгорание. Примите необходимые меры!"""
                        bot.send_photo('1308943241', caption=text, parse_mode="HTML", photo=send_img)

                        connection = smtplib.SMTP('smtp.gmail.com', 587)
                        connection.starttls()
                        connection.login(
                            user='select.issnotify@gmail.com',
                            password='wtapqvfobhblwqin'
                        )
                        user_email = 'only1avetrill@gmail.com'
                        from_addr = 'select.issnotify@gmail.com'
                        to_addr = user_email
                        subj = 'Оповещение системы безопасности'
                        msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (from_addr, to_addr, subj, f"""Внимание, Даниил.
{datetime.now().date()} {str(datetime.now().time())[:8]} в помещении 1 (камера 1) обнаружено возгорание. Примите необходимые меры!""")
                        connection.sendmail(from_addr, to_addr, msg.encode('utf-8'))
                        connection.close()

        if self.MOVEMENT_DETECTION and not self.first_time :

            err = np.sum((self.img_prev.astype("float") - img.astype("float")) ** 2)
            err /= float(self.img_prev.shape[0] * img.shape[1])
            if err > 3000 and self.time_after_move > 3:
                self.time_after_move = 0
                print("movement!")
                CameraStatus(time=datetime.now().time(), message="Замечено движение", importance=5).save()
        self.first_time = False
        self.img_prev = img

        time.sleep(1 / 30)

        _, jpeg = cv2.imencode('.jpg', img)
        self.first_time = False
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.cap.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


class GetStatus(generics.ListAPIView):
    def get(self, request):
        print("Get found")
        text = ''
        # CameraStatus(importance = random.randint(1, 5), message=f"{Faker().name()}", time = datetime.now()).save()
        # CameraStatus.objects.all().delete()
        for status in CameraStatus.objects.all().order_by('-pk')[:27]:
            color = "black"
            if status.importance == 1:
                color = '#26BD02'
            elif status.importance == 2:
                color = '#0270BD'
            elif status.importance == 3:
                color = "#BABD02"
            elif status.importance == 4:
                color = "#BD02BD"
            elif status.importance == 5:
                color = "#BD0202"
            text += f"&nbsp;&nbsp;[{str(status.time)[:8]}] <span style=\"color:{color};\">{status.message}</span><br>"
        return Response(text)
