from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import speedtest  # type: ignore
from icmplib import ping as icmp_ping, exceptions  # type: ignore
import asyncio
import logging
import os
import uvicorn

app = FastAPI(title="NetBenchmark", version="1.1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


async def run_speedtest():
    loop = asyncio.get_event_loop()
    st = speedtest.Speedtest()
    try:
        server = await loop.run_in_executor(None, st.get_best_server)
        download = await loop.run_in_executor(None, st.download)
        upload = await loop.run_in_executor(None, st.upload)

        return {
            "download": f"{round(download / 10**6, 2)} Mbps",
            "upload": f"{round(upload / 10**6, 2)} Mbps",
            "ping": f"{st.results.ping} ms",
            "server": {
                "name": server["name"],
                "sponsor": server["sponsor"],
                "country": server["country"],
            },
        }
    except speedtest.ConfigRetrievalError as e:
        logger.error("Error connecting to speedtest.net servers")
        raise HTTPException(
            status_code=503, detail="No connection to speedtest.net servers"
        ) from e
    except Exception as e:
        logger.error(f"Error during speedtest: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/speedtest", summary="Run internet speed test")
async def speedtest_endpoint():
    return await run_speedtest()


count_query = Query(4, ge=1, le=10, description="Number of packets (1-10)")
interval_query = Query(
    0.5, ge=0.1, le=2.0, description="Interval between packets (sec)"
)
timeout_query = Query(2, ge=1, le=5, description="Timeout (sec)")


@app.get("/ping/{host}", summary="Measure ping to host")
async def ping_endpoint(
    host: str,
    count: int = count_query,
    interval: float = interval_query,
    timeout: int = timeout_query,
):
    try:
        if not host.replace(".", "").replace(":", "").isalnum():
            raise ValueError("Invalid characters in host")

        result = icmp_ping(host, count=count, interval=interval, timeout=timeout)

        if not result.is_alive:
            raise HTTPException(status_code=400, detail="Host is unreachable")

        return {
            "host": host,
            "avg_ping": f"{round(result.avg_rtt, 2)} ms",
            "packet_loss": f"{result.packet_loss * 100:.1f}%",
            "jitter": f"{result.jitter:.2f} ms",
            "packets": {
                "sent": result.packets_sent,
                "received": result.packets_received,
            },
        }
    except exceptions.ICMPError as e:
        logger.warning(f"ICMP error for {host}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"ICMP error: {str(e)}") from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unknown ping error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
