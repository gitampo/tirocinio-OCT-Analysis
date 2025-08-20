BLD = '\033[1m'
DIM = '\033[2m'
GRN = '\033[32m'
YLW = '\033[33m'
BLU = '\033[34m'
RST = '\033[0m'

def print_separator(length=60):
    print(BLU + "~" * length + RST)

def print_warning(message, end="\n"):
    print(YLW + "(!) " + message + RST, end=end)

def print_success(message, end="\n"):
    print(GRN + message + RST, end=end)

def print_success_box(message):
    length = len(message)

    # crea il box del messaggio
    top = "+---" + ('-'*length) + "---+ \n"
    cnt = "|   " +    message   + "   | \n"
    bot = "+---" + ('-'*length) + "---+ \n"

    print_success(top + cnt + bot, end="")

def print_info(message, end="\n"):
    print(DIM + message + RST, end=end)

def print_list(items):
    for item in items:
        print(f"- {item}")

def print_log(message, end="\n"):
    print(BLU + "(i) " + message + RST, end=end)