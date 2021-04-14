
def hasNumbers(string) -> bool:
    return any(char.isdigit() for char in string)


def convert_numbers_in_letters(string) -> str:
    
    for char in string:
        if char == "3":
            string = string.replace(char, "e")
        elif char == "4":
            string = string.replace(char, "a")
        else:
            pass
    return string

