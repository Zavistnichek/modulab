from celery import shared_task
import speedtest
from .models import SpeedTestResult


@shared_task
def run_speedtest(user_id, ip_address):
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1024 / 1024
    upload_speed = st.upload() / 1024 / 1024
    ping = st.results.ping

    result = SpeedTestResult(
        user_id=user_id,
        download_speed=download_speed,
        upload_speed=upload_speed,
        ping=ping,
        ip_address=ip_address,
    )
    result.save()
    return result.id
