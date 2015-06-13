#!/bin/bash

for dest in *.png; do
    convert "$dest" -shave 180x70 "$dest"
done
