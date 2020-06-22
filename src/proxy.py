import tornado.ioloop
import tornado.web
import tornado.httpclient

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        target = self.get_argument('target', None)
        response = {'target': target}
        self.write(response)
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
            self.write(response.body)
        

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    #dockerhub autobuild testing comment
    import os, re
    proxy = os.getenv('HTTP_PROXY')
    splits = re.split('/|:|@',proxy)
    global proxy_username, proxy_password, proxy_host, proxy_port
    proxy_username = splits[3]
    proxy_password = splits[4]
    proxy_host = splits[5]
    proxy_port = splits[6] 
    app = make_app()
    app.listen(8888)
    tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    tornado.ioloop.IOLoop.current().start()
