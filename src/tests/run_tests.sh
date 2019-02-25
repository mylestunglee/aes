for i in {01..02}
do
	python3 ../main.py -p test$i.problem -s test$i.schedule -e > actual$i.txt
	if [[ $(diff expected$i.txt actual$i.txt) ]]; then
		echo "Test $i failed"
	else
		echo "Test $i passed"
	fi
done
