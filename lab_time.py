import datetime
import pytz
import json
import requests
from wsgiref.simple_server import make_server
from urllib.parse import unquote_plus
from dateutil import parser
from html.parser import HTMLParser

BASE_URL = "http://localhost:8000/"


class MyHTMLParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.record_time = False

    def handle_data(self, data):
        if self.record_time == True:
            self.time = data
            self.record_time = False

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            if ("id", "time") in attrs:
                self.record_time = True


def test_get_cur_tz_time_server():  # GET /
    response = requests.get(BASE_URL)
    assert response.status_code == 200

    parser = MyHTMLParser()
    parser.feed(response.text)
    server_tz = datetime.datetime.now().astimezone().tzinfo
    server_tz_time = datetime.datetime.now(tz=server_tz).strftime("%H:%M")
    assert parser.time == server_tz_time


def test_get_cur_tz_time_tz():  # GET /<\tz name>
    tz_list = ["UTC", "Asia/Yerevan"]
    for tz in tz_list:
        url = BASE_URL + tz
        response = requests.get(url)
        assert response.status_code == 200

        parser = MyHTMLParser()
        parser.feed(response.text)
        req_tz = pytz.timezone(tz)
        req_tz_time = datetime.datetime.now(tz=req_tz).strftime("%H:%M")
        assert parser.time == req_tz_time
    url = BASE_URL + "/" + "qwerty"
    response = requests.get(url)
    assert response.status_code == 200
    parser = MyHTMLParser()
    parser.feed(response.text)
    server_tz = datetime.datetime.now().astimezone().tzinfo
    server_tz_time = datetime.datetime.now(tz=server_tz).strftime("%H:%M")
    assert parser.time == server_tz_time


def test_get_tz_info_time():  # POST /api/v1/time
    url = BASE_URL + "api/v1/time"
    tz_list = [b"UTC", b"Asia/Yerevan"]
    for tz in tz_list:
        response = requests.post(url=url, data=tz)
        assert response.status_code == 200
        time = response.json()["time"]

        req_tz = pytz.timezone(tz)
        req_tz_time = datetime.datetime.now(tz=req_tz).strftime("%H:%M")
        assert time == req_tz_time

    tz_list = [b"", b"qwerty"]
    for tz in tz_list:
        response = requests.post(url=url, data=tz)
        assert response.status_code == 200
        time = response.json()["time"]

        server_tz = datetime.datetime.now().astimezone().tzinfo
        server_tz_time = datetime.datetime.now(tz=server_tz).strftime("%H:%M")
        assert time == server_tz_time


def test_get_tz_info_date():  # POST /api/v1/date
    url = BASE_URL + "api/v1/date"
    tz_list = [b"UTC", b"Asia/Yerevan"]
    for tz in tz_list:
        response = requests.post(url=url, data=tz)
        assert response.status_code == 200
        time = response.json()["date"]

        req_tz = pytz.timezone(tz)
        req_tz_time = datetime.datetime.now(tz=req_tz).strftime("%d/%m/%y")
        assert time == req_tz_time

    tz_list = [b"", b"qwerty"]
    for tz in tz_list:
        response = requests.post(url=url, data=tz)
        assert response.status_code == 200
        time = response.json()["date"]

        server_tz = datetime.datetime.now().astimezone().tzinfo
        server_tz_time = datetime.datetime.now(tz=server_tz).strftime("%d/%m/%y")
        assert time == server_tz_time


def test_get_date_diff():  # POST /api/v1/datediff
    url = BASE_URL + "api/v1/datediff"
    data_list = [
        '{"start_date": {"date":"12.20.2021 22:21:05", "tz": "EST"}, "end_date": {"date":"12:30pm 2020-12-01", "tz": ""}}',
        '{"start_date": {"date":"12.20.2021 22:21:05", "tz": ""}, "end_date": {"date":"12:30pm 2020-12-01", "tz": "Europe/Moscow"}}',
        '{"start_date": {"date":"12.20.2021 22:21:05", "tz": ""}, "end_date": {"date":"12:30pm 2020-12-01", "tz": ""}}',
        '{"start_date": {"date":"12.20.2021 22:21:05"}, "end_date": {"date":"12:30pm 2020-12-01"}}',
    ]
    for data in data_list:
        response = requests.post(url=url, data=data)
        assert response.status_code == 200
        datediff = response.json()["datediff"]
        assert datediff == {
            "days": 384,
            "hours": 9,
            "minutes": 51,
            "seconds": 5,
            "total_seconds": 33213065.0,
        }

    data = '{"start_date": {"date":"12.20.2021 22:21:05", "tz": "EST"}, "end_date": {"date":"12:30pm 2020-12-01", "tz": "Europe/Moscow"}}'
    response = requests.post(url=url, data=data)
    assert response.status_code == 200
    datediff = response.json()["datediff"]
    assert datediff == {
        "days": 384,
        "hours": 17,
        "minutes": 51,
        "seconds": 5,
        "total_seconds": 33241865.0,
    }


html = """
<html lang="en">
<head>
<meta charset="UTF-8">
<title>python lab: Time WebApp</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {
    font-family: 'Courier New', monospace;
    background-color: rgb(255, 252, 240);
    color: rgb(16, 15, 15);
  }
  .grid-container {
    display: grid;
    grid-template-columns: 250px 1fr 1fr;
    gap: 2rem; 
    margin-block: 2em;
  }
  h1 {
    font-weight: normal;
    background-color: rgb(242, 240, 229);
  }
  p {
    margin-top: 0em;
  }
  button, input {
    margin-bottom: 1em;
  }
  input[type=text] {
    box-sizing: border-box;
    border: 2px solid rgb(230, 228, 217);
    border-radius: 4px;
    font-size: 16px;
    font-family: 'Courier New', monospace;
    background-color: rgb(255, 252, 240);
    color: rgb(16, 15, 15);
    padding: 5px;
  }
  button {
    box-sizing: border-box;
    border: 0px solid rgb(40, 39, 38);
    border-radius: 4px;
    font-size: 16px;
    font-family: 'Courier New', monospace;
    background-color: rgb(16, 15, 15);
    color: rgb(255, 252, 240);
    padding: 5px 15px 5px 15px;
    cursor: pointer;
  }
  button:hover {
    background-color: rgb(218, 112, 44);
  }
  a {
    color: rgb(16, 15, 15);
  }
</style>
</head>
<body>
 
<h1>GET</h1>
<div class="grid-container">
  <div>
  <p>GET /</p>
  <p>GET /<&bsol;tz name></p>
  </div>
  <div>
    <p id="time" style="font-size: 40px; font-weight: bold; margin-block-end: 0em">%(cur_time)s</p>
    <p id="tz" style="font-size: 40px; font-weight: bold;">%(cur_tz)s</p>
  </div>
  <div>
    <p><a href="http://localhost:8000" target="_self">localhost:8000</a></p>
    <p><a href="http://localhost:8000/EST" target="_self">localhost:8000/EST</a></p>
  </div>
</div>

<h1>POST</h1>
<div class="grid-container">
  <p>
    POST /api/v1/time
  </p>
  <p>
    <b>find current time in a specified timezone.</b><br><br>server tz is used if left empty
  </p>
  <form method="post" action="/api/v1/time">
    <label for="tz_time">tz</label>
    <input type="text" name="tz_time" placeholder="EST">
    <button type="submit"> get .json</button>
  </form>

</div>
<div class="grid-container">
  <p>
    POST /api/v1/date
  </p>
  <p>
    <b>find current date in a specified timezone.</b><br><br>server tz is used if left empty
  </p>
  <form method="post" action="/api/v1/date">
    <label for="tz_date">tz</label>
    <input type="text" name="tz_date" placeholder="EST">
    <button type="submit"> get .json</button>
  </form>
</div>
<div class="grid-container">
  <p>
    POST /api/v1/datediff
  </p>
  <p>
    <b>find time difference between 2 dates.</b><br><br>usage example: {"date":"12.20.2021 22:21:05", "tz": "EST"}<br><br>tz is not required.<br>to use tz — both start date tz and end date tz should be specified
  </p>
  <form method="post" action="/api/v1/datediff">
    <label for="start_date">start date, tz </label>
    <input type="text" name="start_date" value="" placeholder='{"date":"12.20.2021 22:21:05", "tz": "EST"}' required>
    <br>
    <label for="end_date">end date, tz </label>
    <input type="text" name="end_date" value="" placeholder='{"date":"12:30pm 2020-12-01", "tz": "Europe/Moscow"}' required>
    <br>
    <button type="submit"> get .json</button>
  </form>
</div>
</body>
</html>
"""


class WebApp:
    def __init__(self, environ, response):
        self.environ = environ
        self.response = response

    def __iter__(self):
        method = self.environ["REQUEST_METHOD"]
        path = self.environ["PATH_INFO"]

        if method == "POST":
            input = self.environ["wsgi.input"]
            data = unquote_plus(
                input.read(int(self.environ["CONTENT_LENGTH"])).decode()
            )
            if path == "/api/v1/time":
                tz = data.lstrip("tz_time=").strip()
                response_body = self.get_tz_info(tz, "time")
            elif path == "/api/v1/date":
                tz = data.lstrip("tz_date=").strip()
                response_body = self.get_tz_info(tz, "date")
            elif path == "/api/v1/datediff":
                print(data)
                timestamps = []
                if data.strip().startswith("start_date="):  # if data is from html form
                    timestamps = data.strip().split("&")
                    timestamps[0] = json.loads(timestamps[0].lstrip("start_date="))
                    timestamps[1] = json.loads(timestamps[1].lstrip("end_date="))
                else:  # if data is json as a str
                    t_dict = json.loads(data)
                    timestamps.insert(0, t_dict["start_date"])
                    timestamps.insert(1, t_dict["end_date"])
                response_body = self.get_date_diff(timestamps)

            status = "200 OK"  # HTTP Status
            response_headers = [
                ("Content-type", "application/json"),
                ("Content-Length", str(len(response_body))),
            ]  # HTTP Headers
        else:
            tz = path.lstrip("/")
            response_body = self.get_cur_tz_time(tz)

            status = "200 OK"  # HTTP Status
            response_headers = [
                ("Content-type", "text/html"),
                ("Content-Length", str(len(response_body))),
            ]  # HTTP Headers

        self.response(status, response_headers)
        yield response_body.encode()

    def get_tz_info(self, tz, info):
        if info == "time":
            strf = "%H:%M"
        elif info == "date":
            strf = "%d/%m/%y"

        if tz in pytz.all_timezones:
            req_tz = pytz.timezone(tz)
            req_info = datetime.datetime.now(tz=req_tz).strftime(strf)
        elif tz == "":
            server_tz = datetime.datetime.now().astimezone().tzinfo
            req_info = datetime.datetime.now(tz=server_tz).strftime(strf)
        else:
            req_info = ""
        return json.dumps({info: req_info})

    def get_cur_tz_time(self, tz):
        if tz in pytz.all_timezones:
            req_tz = pytz.timezone(tz)
        else:
            req_tz = datetime.datetime.now().astimezone().tzinfo
        req_tz_time = datetime.datetime.now(tz=req_tz).strftime("%H:%M")
        return html % {"cur_time": req_tz_time, "cur_tz": req_tz}

    def get_date_diff(self, timestamps):
        dt = datetime.datetime.now()

        start_info = timestamps[0]
        end_info = timestamps[1]

        if (
            "tz" in start_info
            and "tz" in end_info
            and start_info["tz"]
            and end_info["tz"]
        ):
            start_tz = pytz.timezone(start_info["tz"])
            start_tz_loc = start_tz.localize(dt)
            start_str = start_info["date"] + " " + start_tz_loc.tzname()
            start_tz_info = {start_tz_loc.tzname(): start_tz_loc.tzinfo}

            end_tz = pytz.timezone(end_info["tz"])
            end_tz_loc = end_tz.localize(dt)
            end_str = end_info["date"] + " " + end_tz_loc.tzname()
            end_tz_info = {end_tz_loc.tzname(): end_tz_loc.tzinfo}
        else:
            start_str = start_info["date"]
            start_tz_info = None

            end_str = end_info["date"]
            end_tz_info = None

        start_obj = parser.parse(timestr=start_str, tzinfos=start_tz_info)
        end_obj = parser.parse(timestr=end_str, tzinfos=end_tz_info)

        delta = abs(end_obj - start_obj)
        h, m, s = str(datetime.timedelta(seconds=delta.seconds)).split(":")
        datediff = {
            "days": delta.days,
            "hours": int(h),
            "minutes": int(m),
            "seconds": int(s),
            "total_seconds": delta.total_seconds(),
        }
        return json.dumps({"datediff": datediff})


with make_server("", 8000, WebApp) as httpd:
    print("Serving on port 8000...")
    # Serve until process is killed
    httpd.serve_forever()
