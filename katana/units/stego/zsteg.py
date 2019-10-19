import subprocess

from katana.unit import FileUnit, NotApplicable
from katana.manager import Manager
from katana.target import Target
import katana.util

permutations = ["b1,rgb,lsb,xy", "b1,r,lsb,xy", "b1,rgb,msb,yx",
		"b2,rgb,lsb,yx", "b2,rgb,lsb,xy", "b1,rgba,lsb,xy", "b1,r,lsb,xy",
		"b1,rgba,msb,yx", "b2,rgba,lsb,yx", "b2,rgba,lsb,xy", "b1,rgb,lsb,xy"]

class Unit(FileUnit):
	
	# Binary dependencies
	DEPENDENCIES = ['zsteg']
	# Moderately high priority for matching targets
	PRIORITY = 40
	# Groups we are in
	GROUPS = ['stego', 'image']

	def __init__(self, katana, target):
		super(Unit, self).__init__(katana, target, keywords=['png'])

	def evaluate(self, katana, case):
		for args in permutations:

			p = subprocess.Popen(['zsteg', self.target.path, args],
					stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			result = {
				"stdout": [],
				"stderr": [],
			}
			output = bytes.decode(p.stdout.read(), 'ascii')
			error = bytes.decode(p.stderr.read(), 'ascii')

			d = "\r"
			for line in output:
				s = [e + d for e in line.split(d) if e]

			for line in [l.strip() for l in output.split('\n') if l]:
				delimeter = '\r'
				lines = [e + d for e in line.split(d) if e]
				for temp_line in lines:
					if not temp_line.endswith(".. \r"):
						if katana.locate_flags(self, temp_line):
							self.completed = True
						result["stdout"].append(temp_line)

			for line in [l.strip() for l in error.split('\n') if l]:
				if katana.locate_flags(self, line):
					pass
				result["stderr"].append(line)

			if not len(result['stderr']):
				result.pop('stderr')
			if not len(result['stdout']) or '[=] nothing :(\r' in result['stdout']:
				result.pop('stdout')

			katana.add_results(self, result)
