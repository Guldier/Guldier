
import random
import smtplib, ssl

#from exchangelib import Configuration, Account, DELEGATE
#from exchangelib import Message, Mailbox, Credentials
#from exchangelib import Account, Credentials, Message, Mailbox, ServiceAccount, DELEGATE
#from config import cfg
from email.message import EmailMessage
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from datetime import datetime
from django.core.mail import send_mail, get_connection
from django.core.mail.message import EmailMessage
from .models import (
    Dish, 
    AddOn,
    Composition,
    Cart,
    Orders,
    WeekDish
)


def create_list():
    today = datetime.today()
    today_orders=Orders.objects.filter(order_date__date=today.date())
    composition_list = {}
    money = 0
    
    for food in today_orders:
        if food.composition in composition_list:
            composition_list[food.composition] = composition_list.get(food.composition,0) + food.quantity
        else:
            composition_list[food.composition] = food.quantity
    
    message = 'PODUMOWANIE WSZYSTKICH DAŃ\n'

    for key in composition_list:
        message += f'{key} x {composition_list[key]}\n'

    message += '\nOsoby zamawiające\n'

    for orders in today_orders:
        message += f'{orders.user} - {orders.composition} - {orders.quantity}szt.\n'
        if orders.composition.dish.dish_type == 'special' and orders.composition.dish.price == 20:
            money += ((orders.composition.dish.price - 1) + orders.composition.addon.price) * orders.quantity
        else:
            money += ((orders.composition.dish.price - 1) + orders.composition.addon.price) * orders.quantity

    message += f'\nŁącznie do zapłaty: {money}zł\n'
    message += '\nPozdrawiamy\nLinetech'

    print(message)
    
    send_mail(
        f'Lista obiadów {today.date()}',
        message,
        None,
        ['biuro@hotel-trzykorony.pl','damian.jadacki@linetech.pl','michal.oszajca@linetech.pl','michal.borkowski@linetech.pl'],
        fail_silently=False,
    )



def ar_status():

    sender = 'engineering@linetechpolska.pl'
    reciever = ['checkleaders@linetech.pl','planning.rze@linetech.pl','logistic.rze@linetech.pl','rafal.komaniecki@linetech.pl','engineering.rze@linetech.pl','tariq.albraikat@linetech.pl']
    password = 'JYG8$*$<N@'

    ac_reg = ['9H-QCT','EI-GSI','D-AILW']
    link = ['https://linetech365-my.sharepoint.com/:x:/g/personal/djadacki_linetech_com_pl/EXFiHXIHn1tKrDm-UkLl0OwBPKVr-J_e4W-xYRK3SPX_Fw?e=L3VDxb','https://linetech365-my.sharepoint.com/:x:/g/personal/djadacki_linetech_com_pl/Eapqhn6djr1Jok8Xe0KGloUBUw8kfu4YCpG-J3vczi6g8Q?e=wi3eXL','https://linetech365-my.sharepoint.com/:x:/g/personal/djadacki_linetech_com_pl/EUQYI93_S4lBtxKgCl2ii4oBXjCyHtNDDeZvh9y-QbsR-g?e=CCw5Ge']
 
    for i in range(len(ac_reg)):
        msg = MIMEMultipart("alternative")
        msg['Subject'] = f'{ac_reg[i]} all OEM cases: AR list {datetime.today().date()}'
        msg['From'] = 'engineering.rze@linetech.pl'
        msg['To'] = ", ".join(reciever)

        message = f"""\
        Hi everyone, <br> 
        Please see attached <a href="{link[i]}"> AR LIST </a>
        for {ac_reg[i]} {datetime.today().date()} . <br>"""

        html = """\
        <!DOCTYPE html>
        <html lang = "pl-PL">
            <head>
                <meta http - equiv ="Content-Language" content ="pl">
                <meta charset = "UTF-8">
            </head>
            <body>
                <style>
                table {font-family: Segoe UI,sans-serif;background: transparent;}
                p.a {font-size: 14px; color:#482960;}
                p.b {font-size: 11px; color:#482960;}
                p.c {font-size: 11px; color:#737373;}
                p.rodo {font-size: 8px; color:#737373; text-align: justify;};
                a:link {font-size: 11px; text-decoration: none; color: #737373;}
                a:visited {font-size: 11px; text-decoration: none; color: #737373;}
                a:active {font-size: 11px; text-decoration: none; color: #737373;}
                a:hover {font-size: 11px; text-decoration: none; color: #737373;}
                tbody.a {background: transparent;background-color:transparent}
                </style>
                <table width = "600" cellspacing="0" cellpadding = "0 " border = "0 ">
                    <tbody class="a">
                        <tr>
                            <td>
                                <p class="a"><b> Damian Jadacki |</b> Engineer</p>
                            </td>
                            <td rowspan="2">

                        </td>
                        <td  colspan= "5" rowspan="2">
                            <a href="http://aviaprime.eu"><img  style = "border:none" src = "http://ftp.linetech.nazwa.pl/stopka/avia.png"></a>
                        </td>
                        <td rowspan="2">

                        </td>
                        <td rowspan="2">

                        </td>
                        <td rowspan="2">

                        </td>
                    </tr>
                    <tr>
                        <td>
                            <p class="b">LINETECH Aircraft Maintenance </p>
                        </td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td colspan=" 6" height=" 20 "> 
                            <br /> <br />
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <p><a href="tel:+48887 400 189">+48 603 955 708 </a></p>
                        </td>
                        <td></td>
                        <td rowspan="3" width = "65">
                            <a href="http://www.linkedin.com/company/linetech-aircraft-maintenance"><img style = "border:none" width = "25" height = "25" src = "http://ftp.linetech.nazwa.pl/stopka/linkedin.png"></a>
                        </td>
                        <td rowspan="3" width = "65">
                            <a href="http://twitter.com/linetech_mro"><img style = "border:none" width = "25" height = "25" src = "http://ftp.linetech.nazwa.pl/stopka/twitter.png"></a>
                        </td>
                        <td rowspan="3" width = "65">
                            <a href="http://instagram.com/linetech_mro"><img style = "border:none" width = "25" height = "25" src = "http://ftp.linetech.nazwa.pl/stopka/instagram.png"></a>
                        </td>
                        <td rowspan="3" width = "20">
                            <a href="https://www.youtube.com/channel/UCS2tZyT9Mn0ArxIy41LVjYw"><img style = "border:none" width = "25" height = "25" src = "http://ftp.linetech.nazwa.pl/stopka/youtube.png"></a>
                        </td>                
                    </tr>
                    <tr>
                        <td>
                            <p> <a href="malito:michal.grebosz@linetech.pl"> damian.jadacki@linetech.pl </a></p>
                        </td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>
                            <p><a href="www.aviaprime.eu"> www.aviaprime.eu </a></p>
                        </td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
            <br>    
            <table width ="600">
                <tr>
                    <a href="http://seemore.aviaprime.eu"<img width = "600" height = "80" src = "http://ftp.linetech.nazwa.pl/stopka/Banner.png" alt = "Instagram" style = "border:none"></a>
                </tr>
                <tr>
                    <p class="rodo">Note: Under the General Data Protection Regulation (GDPR) (EU) 2016/679, we have a legal duty to protect any information we collect from you. Information contained in this email and any attachments may be privileged or confidential and intended for the exclusive use of the original recipient. If the reader of this e-mail is not the intended recipient or an agent responsibility for delivering it to the intended recipient, you are hereby notified that you have received this document in error and that any review, dissemination, distribution or coping of this message is strictly prohibited. If you have received this e-mail in error, please notify office@linetech.pl immediately. Linetech S.A. is 100% compliant with the General Data Protection Regulation (GDPR) .To learn more about how we collect, keep, and process your private information in compliance with GDPR, please view our privacy policy or contact us at iod@linetech.pl</p>
                </tr>
            </table>
        </body>
    </html>
    """
#.format(table_html=table_html)

        message += html

        part1 = MIMEText(message, "html")

        msg.attach(part1)

        ip = '192.168.17.135'
        context = ssl.create_default_context()
        weekday = datetime.today().weekday()
        if weekday < 5:
            server = smtplib.SMTP('192.168.17.135')
            server.login(sender, password)
            server.sendmail(sender, reciever, msg.as_string())
        else:
            pass
