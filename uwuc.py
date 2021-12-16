### Imports ###
import sys
import subprocess
import re
import os

reg = 0
count = 0
assembly = """
.text
	.globl _start
_start:
"""

def counter(reset=False):
	global count
	if reset:
		count = 0
	count += 1
	return count - 1

T_PUSH = counter()
T_POP = counter()
T_EXIT = counter()

def write(s):
	global assembly
	assembly += s

def read_program_from_file(file):
	program = []
	with open(file) as f:
		text = f.read()
		tokens = text.split()
		instructions = {
			"uwu": T_PUSH,
			"UWU": T_POP,
			"UwU": T_EXIT
		}
		for i, token in enumerate(tokens):
			t = instructions.get(token)
			if t is not None:
				program.append(t)
			else:
				if all([c.isdigit() for c in token]):
					program.append(int(token))
				else:
					match = bool(re.match("'(.*)'", token))
					if match:
						program.append(ord(token[1]))
					else:
						raise ValueError(token)
	return program
					
def uwuc(program, filename):
	write(".text\n")
	write("\t.globl _start\n")
	write("_start:\n")
	ip = 0
	program_len = len(program)
	while ip < program_len:
		token = program[ip]
		write(f"i{ip}:\n")
		if token == T_PUSH:
			ip += 1
			byte = program[ip]
			write("/*\tPUSH\t*/\n")
			write("\tdec %rsp\n")
			write(f"\tmovb ${byte}, (%rsp)\n")

		elif token == T_POP:
			write("/*\tPOP\t*/\n")
			write("\tmovq (%rsp), %rdi\n")

		elif token == T_EXIT:
			ip += 1
			write("/*\tEXIT\t*/\n")
			write("\tmovq $60, %rax\n")
			write("\tsyscall\n")

		ip += 1
	asmpath = os.path.join("/tmp/", f"temp-{filename}.s")
	objpath = os.path.join("/tmp/", f"temp-{filename}.o")
	with open(asmpath, 'w') as f:
		f.write(assembly)
	ps = subprocess.run(["as", "-o", objpath, asmpath])
	if ps.stderr is not None:
		print("Assembling failed", ps.stderr)
	subprocess.run(["ld", "-s", "-o", "a.out", objpath])
	if ps.stderr is not None:
		print("Linking failed", ps.stderr)
	
	print("compiled successfully")

if __name__ == "__main__":
	args = sys.argv[1:]
	file = args.pop()
	program = read_program_from_file(file)
	uwuc(program, file)
