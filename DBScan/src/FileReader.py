import numpy as np
from PyQt4.QtGui import QFileDialog, QApplication, QInputDialog
import fileinput

format_options = ['S1', 'S5', 'S10', 'S20', 'i1', 'i4', 'i8', 'f4', 'f8', 'f16']

format_dict = \
{'Channel Name': 'S20',
'X': 'f8',
'Y': 'f8',
'Xc': 'f8',
'Yc': 'f8',
'Height': 'f8',
'Area': 'f8',
'Width': 'f8',
'Ax': 'f8',
'BG': 'f8',
'I': 'f8',
'Frame': 'i4',
'Length': 'i4',
'Link': 'i4',
'Valid': 'i4',
'Z': 'f4',
'Zc': 'f4',
'Photons': 'f8',
'Phi': 'f8',
'Lateral Localization Accuracy': 'f8',
'Xw': 'f8',
'Yw': 'f8',
'Xwc': 'f8',
'Ywc': 'f8'
} # end

def get_format(name):
	if name in format_dict:
		return format_dict[name]
	form = QInputDialog.getItem(None, "Format for %s" % name, 'Pick a format', format_options)
	for line in fileinput.input():
		if line.endswith('# end'):
			print('\n\n} # end')
		else:
			print(line)
	return form

def file_to_array(filename):
	lines = [line.strip() for line in open(filename).readlines()]
	names = lines[0].split('\t')
	formats = [get_format(i) for i in names]
	data = np.loadtxt(filename, dtype={'names': names, 'formats': formats}, delimiter='\t', skiprows=1)
	return data

app = QApplication([])

if __name__ == '__main__':
	filename = QFileDialog.getOpenFileName()
