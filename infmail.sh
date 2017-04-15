#!/bin/bash

while true; do python multimicro.py sad_JJ 5 | sendemail -f "bradcompscimail@gmail.com" -t "lessthan1337@gmail.com" -u "SWS Report" -o tls=yes -o timeout=0 -s smtp.gmail.com:587 -xu bradcompscimail@gmail.com -xp byucompsci; sleep 1; done
