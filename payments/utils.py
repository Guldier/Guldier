from payments import models as pay_models


def get_current_prices():
    return [(price.amount, str(price.amount) + ' za ' + f'{price.get_discounted_price:.2f}')
            if price.promotion.active_dates.date_within_range
            and price.promotion.active else (price.amount, price.amount)
            for price in pay_models.Price.objects.all().order_by('amount')]
