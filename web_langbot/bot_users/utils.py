from datetime import datetime, timedelta
from django.conf import settings
from pytz import utc
from django.utils.timezone import now

def user_add_days(user, days):
    if settings.USE_TZ:
        # timeit shows that datetime.now(tz=utc) is 24% slower
        now_day = datetime.utcnow().replace(tzinfo=utc)
    else:
        now_day = datetime.now()

    if user.allowed_date >= now_day:
        user.allowed_date += timedelta(days=days)
    else:
        user.allowed_date = now_day + timedelta(days=days)
    user.save()
