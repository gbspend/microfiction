#!/bin/sh
#This will spit out *.depparse.txt files in format_parser (which are gitignored) so make sure to move them if you want to keep them.
set -e
rm SkeletonParser.class || true
javac -cp .:stanford-corenlp-3.9.1.jar SkeletonParser.java 
java -cp .:stanford-corenlp-3.9.1.jar SkeletonParser

