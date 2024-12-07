import re
import string


printable = set(string.printable)
for i in "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ":
    printable.add(i)
    printable.add(i.lower())


def clean_text(s):
    # s = re.sub(r"(?<=[a-zа-яё])(?=[A-ZА-Я])|(?<=[A-ZА-Я])(?=[a-zа-яё])", " ", s)
    while "  " in s:
        s = s.replace("  ", " ")
    while "\n\n" in s:
        s = s.replace("\n\n", "\n")

    s = "".join(filter(lambda x: x in printable, s))
    s = re.sub(r"\[.*?\]", "", s)
    return s
