import speedtest
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SpeedTestResult
from .serializers import SpeedTestResultSerializer


class SpeedTestView(APIView):
    def get(self, request):
        st = speedtest.Speedtest()
        st.get_best_server()
        print("Selected server:", st.best)
        download_speed = st.download(threads=4) / 1024 / 1024  # In MB/s
        upload_speed = st.upload(threads=4) / 1024 / 1024  # In MB/s
        ping = st.results.ping  # In ms

        result = SpeedTestResult(
            user=request.user if request.user.is_authenticated else None,
            download_speed=download_speed,
            upload_speed=upload_speed,
            ping=ping,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        result.save()

        serializer = SpeedTestResultSerializer(result)
        return Response(serializer.data)
