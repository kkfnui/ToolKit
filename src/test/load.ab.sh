#!/usr/bin/env bash

# post_loc.txt contains the json you want to post
# -p means to POST it
# -H adds an Auth header (could be Basic or Token)
# -T sets the Content-Type
# -c is concurrent clients
# -n is the number of requests to run in the test

ab -p post_loc.txt -T application/json -H 'Authorization: Token abcd1234' -c 10 -n 2000 http://example.com/api/v1/locations/