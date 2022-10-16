from datetime import datetime, timedelta
import pytz
from operator import itemgetter
from math import ceil

@service
def ladestyring():
    finish_by = datetime.strptime(input_datetime.finish_charging_by, '%Y-%m-%d %H:%M:%S')
    timezone = pytz.timezone('Europe/Oslo')
    finish_by = timezone.localize(finish_by)
    prices = state.get('sensor.nordpool_kwh_trheim_nok_3_095_025')
    hourly_prices = prices.raw_today + prices.raw_tomorrow
    # cheapest = hourly_prices | sort()
    battery_size = float(input_number.batterysize)
    battery_charge = float(input_number.chargeremaining)
    charge_current = float(state.get('sensor.max_charging_power'))
    # def sortBy(e):
    #     return e['value']
    hours_needed = ceil((battery_size/100*battery_charge)/(charge_current*230/1000))

    log.debug(hours_needed)
    hourly_prices = sorted(hourly_prices, key=itemgetter('value'))
    charging_hours = []
    count = 0
    for hour in hourly_prices:
        if hour['end'] > datetime.now(tz=pytz.timezone('Europe/Oslo')) and hour['start'] < finish_by:
            charging_hours.append(hour)
    charge_now = False
    while count < hours_needed:
        log.debug(datetime.now(tz=pytz.timezone('Europe/Oslo')))
        log.debug(charging_hours[count]['start'])
        log.debug(charging_hours[count]['end'])
        log.debug(charging_hours[count]['start'] < datetime.now(tz=pytz.timezone('Europe/Oslo')))
        log.debug(charging_hours[count]['end'] > datetime.now(tz=pytz.timezone('Europe/Oslo')))
        if charging_hours[count]['start'] < datetime.now(tz=pytz.timezone('Europe/Oslo')) and charging_hours[count]['end'] > datetime.now(tz=pytz.timezone('Europe/Oslo')):
            charge_now = True
        count = count+1
    log.debug(sensor.ehx5cbb6_status)
    if sensor.ehx5cbb6_status == 'charging' and charge_now:
        log.info(f"Setter maks ladestrøm til {charge_current}A")
        easee.set_charger_dynamic_limit(charger_id='EHX5CBB6', current=charge_current)
    elif sensor.ehx5cbb6_status != 'charging' and charge_now:
        log.info(f"Starter lading")
        service.call("easee", "set_charger_dynamic_limit", blocking=True, charger_id='EHX5CBB6', current=charge_current)
        easee.resume(charger_id='EHX5CBB6')
    elif sensor.ehx5cbb6_status == 'charging' and not charge_now:
        log.info(f"Stopper lading")
        easee.pause(charger_id='EHX5CBB6')

    log.debug(f"Chare now: {charge_now}")
    log.debug(f"Ladestyring: finish by: {finish_by} battery_size: {battery_size}, battery_charge{battery_charge}, charge_current{charge_current}")
