from openpyxl import Workbook, load_workbook
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        money += (orders.composition.dish.price + orders.composition.addon.price) * orders.quantity

    message += f'\nŁącznie do zapłaty: {money}zł\n'
    message += '\nPozdrawiamy\nLinetech'
    
    send_mail(
        f'Lista obiadów {today.date()}',
        message,
        None,
        ['damian.jadacki@linetech.pl','biuro@hotel-trzykorony.pl','michal.grebosz@linetech.pl','bartosz.wrobel@linetech.pl'],
        fail_silently=False,
    )

def create_list_rep():
    today = datetime.today()
    today_orders=Orders.objects.filter(order_date__date=today.date())
    composition_list = {}

    for food in today_orders:
        if food.user.is_stuff:
            if food.composition in composition_list:
                composition_list[food.composition] = composition_list.get(food.composition,0) + food.quantity
            else:
                composition_list[food.composition] = food.quantity
    
    message = 'Pani Zosiu,\n'
    message += 'Zamówienie:\n'

    for key in composition_list:
        message += f'{key} x {composition_list[key]}\n'

    message += '\nOsoby zamawiające\n'

    for orders in today_orders:
        message += f'{orders.user} - {orders.composition} - {orders.quantity}szt.\n'

    send_mail(
        f'Lista obiadów rep {today.date()}',
        message,
        None,
        ['damian.jadacki@linetech.pl'],
        fail_silently=False,
    )

def five_s():
    my_host = 'linetech.nazwa.pl'
    my_port = 587 
    my_username = 'damian.jadacki@linetech.pl'
    my_password = 'Dddddjjjjj12#$'
    my_use_tls = False
    my_use_ssl = False
    connection = get_connection(
        host=my_host,
        port=my_port,
        username=my_username,
        password=my_password,
        use_tls=my_use_tls,
        use_ssl=my_use_ssl)
    pracownicy = ['DAMIAN JADACKI', 'MICHAŁ GRĘBOSZ', 'BARTOSZ WRÓBEL', 'ŁUKASZ MAGDA']
    dzis = datetime.today()
    workbook = load_workbook(filename="/home/guldier/5S/5S RZE Engineering November 2020 (W46) 10.11.2020.xlsx")
    sheetnames = workbook.sheetnames
    sheet1 = workbook[sheetnames[0]]
    sheet2 = workbook[sheetnames[1]]
    sheet1["C6"].value = dzis.strftime("%B") + f' {dzis.strftime("%Y")} (W{dzis.isocalendar()[1]}) {dzis.strftime("%d")}.{dzis.strftime("%m")}.{dzis.strftime("%Y")}'
    sheet1["C12"].value = f'ENG / {pracownicy[random.randint(0,3)]}'
    losuj_dalej = True
    suma_pkt = 0
    while losuj_dalej:
        suma_pkt = 0
        for i in range(17,22):
            sheet1[f"I{i}"].value = random.randint(4,5)
            suma_pkt += sheet1[f"I{i}"].value

        for i in range(25,30):
            sheet1[f"I{i}"].value = random.randint(4,5)
            suma_pkt += sheet1[f"I{i}"].value

        for i in range(33,38):
            sheet1[f"I{i}"].value = random.randint(4,5)
            suma_pkt += sheet1[f"I{i}"].value

        for i in range(41,46):
            sheet1[f"I{i}"].value = random.randint(4,5)
            suma_pkt += sheet1[f"I{i}"].value

        for i in range(49,53):
            sheet1[f"I{i}"].value = random.randint(4,5)
            suma_pkt += sheet1[f"I{i}"].value

        if sheet1["C12"].value == f'ENG / {pracownicy[1]}':
            sheet1["I53"].value = 3
        else:
            sheet1["I53"].value = 1
    
        suma_pkt += sheet1["I53"].value
        if suma_pkt >= 119:
            losuj_dalej = False
        else:
            suma_pkt = 0

    free_column = 0
    free_row = 0
    for i in range(5,24):
        if sheet2.cell(row=31,column=i).value == None:
            free_column = i
            break
    if free_column == 0:
        for i in range(5,24):
            if sheet2.cell(row=33, column=i).value == None:
                free_column = i
                break
        sheet2.cell(row=33, column=free_column).value = dzis.date()
        sheet2.cell(row=34, column=free_column).value = suma_pkt
    else:
        sheet2.cell(row=31, column=free_column).value = dzis.date()
        sheet2.cell(row=32, column=free_column).value = suma_pkt
    filename_excel = f'5S RZE Engineering {dzis.strftime("%B")} {dzis.strftime("%Y")} (W{dzis.isocalendar()[1]}) {dzis.strftime("%d")}.{dzis.strftime("%m")}.{dzis.strftime("%Y")}.xlsx'
    workbook.save(filename=f'/home/guldier/5S/{filename_excel}')
    text = 'Kolejna to juz proba z signature'
    html = """\
    <html>
        <body>
            <table width = "600" cellspacing="0" cellpadding = "0" border = "0">
                <tr>
                    <td>
                        <p><b> Damian Jadacki |</b> Engineer</p>
                    </td>
                </tr>
            </table>
        </body>
    </html>
    """
    signature = MIMEText(html, "html")
    connection.open()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "5S"
    msg['From'] = 'damian.jadacki@linetech.pl'
    msg['To'] = 'bartosz.wrobel@linetech.pl'
    part1 = MIMEText(text, 'plain')

    #msg = EmailMessage(
    #    '5S',
    #    f'Czy to działa?\n {signature.as_string()}',
    #    'damian.jadacki@linetech.pl',
    #    ['bartosz.wrobel@linetech.pl'],
    #    connection=connection)

    #msg.attach_file('/home/guldier/5S/IMG_3622.JPG')
    #msg.attach_file(f'/home/guldier/5S/{filename_excel}')
    msg.attach(part1)
    msg.attach(signature)
    s = smtplib.SMTP('linetech.nazwa.pl', 587)
    s.login('damian.jadacki@linetech.pl','Dddddjjjjj12#$')
    s.sendmail('damian.jadacki@linetech.pl', 'bartosz.wrobel@linetech.pl', msg.as_string())
    s.quit()
    # msg.send()
    #connection.close()
