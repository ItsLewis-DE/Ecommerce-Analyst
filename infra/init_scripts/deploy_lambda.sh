#!/bin/bash

awslocal lambda invoke \
    --function-name transform-function \
    response.json