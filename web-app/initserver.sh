#!/bin/bash
python3 manage.py makemigrations package
python3 manage.py migrate package
python3 manage.py makemigrations users
python3 manage.py migrate users
python3 manage.py makemigrations
python3 manage.py migrate
res="$?"
while [ "$res" != "0" ]
do
    sleep 3;
    python3 manage.py migrate
    res="$?"
done

