#!/bin/bash

echo 'type n user_time max_memory'

for n in {0..1000}
do
	/usr/bin/time -f "full $n %U %M" python3 src/main.py -r $n -R -e -o temp
done

exit 0

for n in {0..1000}
do
	/usr/bin/time -f "partial $n %U %M" python3 src/main.py -r $n -R -e --partial -o temp
done

rm -f temp
