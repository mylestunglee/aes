def number_to_letters(x):
	x += 1
	letters = []
	while x > 0:
		x, remain = divmod(x - 1, 26)
		letters.append(chr(remain + ord('A')))
	return ''.join(reversed(letters))

def letters_to_number(letters):
	x = 0
	for letter in letters:
		x = x * 26 + ord(letter) - ord('A') + 1
	return x - 1
