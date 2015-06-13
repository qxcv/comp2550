#!/bin/bash

for dest in *.png; do
    convert "$dest" -shave 140x70 "$dest"
done
