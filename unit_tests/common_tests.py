import numpy as np
import sys
sys.path.append('../src/')
import common

def test_number_to_letters():
	assert common.number_to_letters(0) == 'A'
	assert common.number_to_letters(1) == 'B'
	assert common.number_to_letters(26) == 'AA'

def test_letters_to_number():
	assert common.letters_to_number('A') == 0
	assert common.letters_to_number('B') == 1
	assert common.letters_to_number('AA') == 26
