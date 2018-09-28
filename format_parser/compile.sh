#!/bin/sh
rm SkeletonParser.class
javac -cp .:stanford-corenlp-3.9.1.jar SkeletonParser.java 
java -cp .:stanford-corenlp-3.9.1.jar SkeletonParser

