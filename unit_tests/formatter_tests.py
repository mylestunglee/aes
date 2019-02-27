import sys
sys.path.append('..')
import src.formatter as formatter

def test_number_to_letters():
	assert formatter.number_to_letters(0) == 'A'
	assert formatter.number_to_letters(1) == 'B'
	assert formatter.number_to_letters(26) == 'AA'

def test_letters_to_number():
	assert formatter.letters_to_number('A') == 0
	assert formatter.letters_to_number('B') == 1
	assert formatter.letters_to_number('AA') == 26
