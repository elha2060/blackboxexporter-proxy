import tornado.ioloop
import tornado.web
import tornado.httpclient
from urllib.parse import urlparse
import re

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        target = self.get_argument('target', None)
        proxy = self.get_argument('proxy', None)
        splits = re.split(':|@',str(proxy))
        proxy_username = splits[0]
        proxy_password = splits[1]
        proxy_host = splits[2]
        proxy_port = splits[3]
        http_client = tornado.httpclient.AsyncHTTPClient()        
        try:
            request = tornado.httpclient.HTTPRequest(method="GET",
                    url=str(target), \
                    connect_timeout=10, \
                    proxy_host=proxy_host, \
                    proxy_port=int(proxy_port), \
                    proxy_username=proxy_username, \
                    proxy_password=proxy_password, \
                    validate_cert=False, \
                    allow_ipv6=False)
            response = await http_client.fetch(request)
        except Exception as e:
            self.set_status(e.code)
            self.write(str(e))
        else:
            self.set_status(response.code)
            self.write(str(response.body))
    
    async def post(self):
        target = self.get_argument('target', None)
        proxy = self.get_argument('proxy', None)
        splits = re.split(':|@',str(proxy))
        proxy_username = splits[0]
        proxy_password = splits[1]
        proxy_host = splits[2]
        proxy_port = splits[3]
        headers = self.request.headers
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            request = tornado.httpclient.HTTPRequest(method="POST",
                    url=str(target), \
                    body=self.request.body, \
                    headers=headers, \
                    connect_timeout=10, \
                    proxy_host=proxy_host, \
                    proxy_port=int(proxy_port), \
                    proxy_username=proxy_username, \
                    proxy_password=proxy_password, \
                    validate_cert=False, \
                    allow_ipv6=False)
            response = await http_client.fetch(request)
        except Exception as e:
            self.set_status(e.code)
            self.write(str(e))
        else:
            self.set_status(response.code)
            if response.headers['Content-Type'] == 'application/json':
                self.write(tornado.escape.json_decode(response.body))
                body = tornado.escape.json_decode(response.body)
                access_token = body["access_token"]
                tld = re.split('\.|/|:',str(target))[5]
                if tld == 'com':
                    region = 'EMEA'
                elif tld == 'cn':
                    region = 'CN'
                elif tld == 'us':
                    region = 'US'
                elif tld == 'ru':
                    region = 'RU'
                filename='/data/'+region
                f = open(filename, "w")
                f.write(access_token)
                f.close()
            else:
                self.write(str(response.body))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    tornado.ioloop.IOLoop.current().start()
