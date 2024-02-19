import re

str = "This is a test"
newStr = re.sub(r"t.*t", "drill", str)
print(newStr)