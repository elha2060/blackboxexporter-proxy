FROM python:3.7-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
RUN apk update \
    && apk add --virtual .build-deps \
        curl-dev gcc curl-dev musl-dev 
RUN python3 -m pip install --target="/install" tornado
FROM base
COPY --from=builder /install /app
COPY src /app
WORKDIR /app
RUN apk add --no-cache libcurl openssl
CMD ["python3", "proxy.py"]
EXPOSE 8888
