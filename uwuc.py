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
T_MOV = counter()
T_WRITE = counter()
T_READ = counter()
T_JMP = counter()
T_JNZ = counter()
T_ADD = counter()
T_SUB = counter()

def write(s):
	global assembly
	assembly += s + '\n'

def read_program_from_file(file):
    program = []
    with open(file) as f:
        text = f.read()
        tokens = text.split()
        instructions = {
            "uwu": T_PUSH,
            "UWU": T_POP,
            "UwU": T_EXIT,
            "Uwu": T_MOV,
            "UWu": T_WRITE,
            "uWU": T_READ,
            "uWu": T_JMP,
            "uwU": T_JNZ,
            "owo": T_ADD,
            "OWO": T_SUB
        }
        for i, token in enumerate(tokens):
            t = instructions.get(token)
            if t is not None:
                program.append(t)
            else:
                if all([c.isdigit() or c == '-' for c in token]):
                    program.append(int(token))
                else:
                    match = bool(re.match("'(.*)'", token))
                    if match:
                        program.append(ord(token[1]))
                    else:
                        if token == "reg":
                            program.append("%rdi")
                        else:
                            raise ValueError(token)
    return program
					
def uwuc(program, filename):
    ip = 0
    program_len = len(program)
    write(f"\tsubq ${program_len // 2 + 1}, %rsp")
    while ip < program_len:
        token = program[ip]
        write(f"i{ip}:")
        if token == T_PUSH:
            ip += 1
            byte = program[ip]
            write("/*\tPUSH\t*/")
            write("\tinc %rsp")
            write(f"\tmovb ${byte}, (%rsp)")

        elif token == T_POP:
            write("/*\tPOP\t*/")
            write("\tmovq (%rsp), %rdi")
            write("\tdec %rsp")

        elif token == T_EXIT:
            ip += 1
            write("/*\tEXIT\t*/")
            write("\tmovq $60, %rax")
            write("\tsyscall")

        elif token == T_MOV:
            ip += 1
            val = program[ip]
            write("/*\tMOV\t*/")
            write(f"\tmovq {val}, %rdi")

        elif token == T_WRITE:
            ip += 1
            count = program[ip]
            write("/*\tWRITE\t*/")
            write("\tmovq %rdi, 4(%rsp)")
            write(f"\tsubq ${count - 1}, %rsp")
            write("\tmovq $1, %rax")
            write("\tmovq $1, %rdi")
            write("\tmovq %rsp, %rsi")
            write(f"\tmovq ${count}, %rdx")
            write("\tsyscall")
            write(f"\taddq ${count - 1}, %rsp")
            write("\tmovq 4(%rsp), %rdi")

        ip += 1
    asmpath = os.path.join("/tmp/", f"temp-{filename}.s")
    objpath = os.path.join("/tmp/", f"temp-{filename}.o")
    with open(asmpath, 'w') as f:
        f.write(assembly)
    ps = subprocess.run(["as", "-o", objpath, asmpath])
    if ps.stderr is not None:
        print("Assembling failed", ps.stderr)
        quit(1)
    subprocess.run(["ld", "-s", "-o", "a.out", objpath])
    if ps.stderr is not None:
        print("Linking failed", ps.stderr)
        quit(1)
	
    print("compiled successfully")

if __name__ == "__main__":
	args = sys.argv[1:]
	file = args.pop()
	program = read_program_from_file(file)
	uwuc(program, file)
