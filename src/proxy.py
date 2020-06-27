import tornado.ioloop
import tornado.web
import tornado.httpclient
import os, datetime, subprocess
from urllib.parse import urlparse

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        target = self.get_argument('target', None)
        network_location = str(urlparse(target).netloc)
        now = datetime.datetime.now()
        if(network_location not in ledger or ledger[network_location]["lasttick"] < now - datetime.timedelta(days=1)):
            proxy_string = proxy_host + ":" + proxy_port
            p1 = subprocess.Popen(["echo"], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["openssl", "s_client", "-servername", network_location, "-showcerts", "-connect", network_location, "-proxy", proxy_string], stdin=p1.stdout, stdout=subprocess.PIPE)
            p3 = subprocess.Popen(["openssl", "x509", "-enddate", "--noout"], stdin=p2.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            p2.stdout.close()
            output = p3.communicate()[0].decode()
            date_string = (re.split('=',output)[1]).rstrip("\n")
            date_format = "%b %d %H:%M:%S %Y %Z"
            date = datetime.datetime.strptime(date_string, date_format)
            expiry = (date - now).days
            ledger[network_location] = {"lasttick":now, "expiry":expiry}
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            request = tornado.httpclient.HTTPRequest(url=str(target), \
                    connect_timeout=10, \
                    proxy_host=proxy_host, \
                    proxy_port=int(proxy_port), \
                    proxy_username=proxy_username, \
                    proxy_password=proxy_password, \
                    validate_cert=False, \
                    allow_ipv6=False)
            response = await http_client.fetch(request)
        except Exception as e:
            self.write(str(e))
        else:
            self.write({"original_response":str(response.body), "ssl_cert_expiry":ledger[network_location]["expiry"]})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    import re
    proxy = os.getenv('HTTP_PROXY')
    global ledger
    ledger = {}
    splits = re.split('/|:|@',proxy)
    global proxy_username, proxy_password, proxy_host, proxy_port, timer
    proxy_username = splits[3]
    proxy_password = splits[4]
    proxy_host = splits[5]
    proxy_port = splits[6]
    app = make_app()
    app.listen(8888)
    tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    tornado.ioloop.IOLoop.current().start()
