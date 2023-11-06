count = 0
string = ""
for i in range(16):
	for j in range(16):
		string = string + " " + str(count)
		count = count + 1
	string = string + "\n"
print(string)
