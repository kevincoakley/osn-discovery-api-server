#!/usr/bin/env python

from flask import Flask, request
from flask_caching import Cache
from flask_cors import CORS, cross_origin
import osn.buckets
import osn.bucket_ignore_list
import osn.credentials


app = Flask(__name__)
cors = CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"

# Configure cache
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app)


@app.route("/")
@cross_origin()
def index():
    return app.send_static_file("index.html")


@app.get("/v1.0/buckets")
@app.get("/buckets")
@cross_origin()
@cache.cached(timeout=86400)
def get_buckets():
    empty_buckets = bool(request.args.get("empty_buckets", False))

    creds = osn.credentials.get_credentials("creds.yaml")
    bucket_ignore_list = osn.bucket_ignore_list.get_bucket_ignore_list(
        "bucket-ignore-list.yaml"
    )
    all_buckets = osn.buckets.get_all_buckets(creds, bucket_ignore_list)
    return osn.buckets.get_read_buckets(all_buckets, empty_buckets)


@app.get("/v2.0/buckets")
@cross_origin()
@cache.cached(timeout=86400)
def get_buckets_with_details():
    empty_buckets = bool(request.args.get("empty_buckets", False))

    creds = osn.credentials.get_credentials("creds.yaml")
    bucket_ignore_list = osn.bucket_ignore_list.get_bucket_ignore_list(
        "bucket-ignore-list.yaml"
    )
    all_buckets = osn.buckets.get_all_buckets(creds, bucket_ignore_list)
    return osn.buckets.get_read_buckets_with_details(all_buckets, empty_buckets)


@app.get("/v2.0/details/<bucket>")
@app.get("/v1.0/details/<bucket>")
@app.get("/details/<bucket>")
@cross_origin()
def get_bucket_details(bucket):
    return osn.buckets.get_bucket_details(bucket)


@app.get("/v2.0/object-list/<bucket>")
@app.get("/v1.0/object-list/<bucket>")
@app.get("/object-list/<bucket>")
@cross_origin()
@cache.cached(timeout=600)
def get_object_list(bucket):
    prefix = request.args.get("prefix", "")

    return osn.buckets.get_object_list(bucket, prefix)


if __name__ == "__main__":
    app.run()
