BLD = '\033[1m'
DIM = '\033[2m'
GRN = '\033[32m'
YLW = '\033[33m'
BLU = '\033[34m'
RST = '\033[0m'

def print_separator(length=60, end="\n"):
    print(BLU + "~" * length + RST, end=end)

def print_warning(message, end="\n"):
    print(YLW + "(!) " + message + RST, end=end)

def print_success(message, end="\n"):
    print(GRN + message + RST, end=end)

def print_success_box(message, indent=' ', end='\n'):
    import textwrap
    length = len(message)

    # crea il box del messaggio
    top = "+---" + ('-'*length) + "---+ \n"
    cnt = "|   " +    message   + "   | \n"
    bot = "+---" + ('-'*length) + "---+ \n"

    print_success(textwrap.indent(top + cnt + bot, indent), end=end)

def print_list(items):
    for item in items:
        print(f"- {item}")

def print_info(message, end="\n"):
    print(BLU + "(i) " + message + RST, end=end)

def print_table(headings, rows, indent=' ', end='\n'):
    from functools import reduce
    import textwrap

    # crea un buffer per la stampa
    buffer = ""
    def buffer_append(string='', end='\n'): nonlocal buffer; buffer += (string + end)
    def buffer_prepend(string='', end='\n'): nonlocal buffer; buffer = (string + end) + buffer

    # controlla se la tabella è vuota
    if not rows: 
        buffer_append(" +-------------------+ \n"
                      " |  Tabella vuota... | \n"
                      " |-------------------| \n"
                      " +-------------------+ \n", end="")
        # stampa la tabella vuota (stampa indentata)
        print(textwrap.indent(buffer, indent), end=end)
        return

    # calcola la larghezza delle colonne
    column_widths = [max([len(str(row[i])) for row in rows]+[len(heading)]) for i, heading in enumerate(headings)]
    table_width = reduce(lambda tot,x: tot+x, column_widths) + len(headings)-1 + len(headings)*2

    # stampa la riga di intestazione
    buffer_append('+' + '-'*table_width + '+')
    buffer_append('|', end="")
    for heading, column_width in zip(headings, column_widths):
        buffer_append(f" {heading.upper():^{column_width}} |",end="")
    buffer_append()
    buffer_append('+' + '-'*table_width + '+')

    # stampa le righe della tabella
    for row in rows:
        buffer_append('|', end="")
        for attr, column_width in zip(row, column_widths):
            buffer_append(f" {str(attr):<{column_width}} |",end="")
        buffer_append()
    buffer_append('+' + '-'*table_width + '+')

    # stampa il buffer finale (indentato)
    print(textwrap.indent(buffer, indent), end=end)


def humanized(string):
    string = string.replace("_", " ")
    string = string if string.isupper() else string.capitalize()
    return string
    
def formatted(value, format):
    # il formato è una percentuale 
    if format.endswith('%'):
        sub_format = format.replace('%','')
        return f"{value*100:{sub_format}}%"

    # caso base
    return f"{value:{format}}"

def print_confusion_matrix(confusion_matrix, labels=None, show_warnings=True, indent=' ', end='\n'):
    import torch
    import textwrap

    # verifica se la matrice di confusione è valida
    if confusion_matrix is None: return

    # crea un buffer per la stampa
    buffer = ""
    def buffer_append(string='', end='\n'): nonlocal buffer; buffer += (string + end)
    def buffer_prepend(string='', end='\n'): nonlocal buffer; buffer = (string + end) + buffer
    pad = ' ' # padding tra etichetta e matrice

    # crea un tensore dalla matrice di confusione e ottiene le dimensioni
    cm = torch.tensor(confusion_matrix)
    rows, cols = cm.shape

    # controlla se le etichette sono valide, altrimenti usa etichette predefinite
    if labels is None or len(labels)!=rows:
        if show_warnings: print_warning("Numero di etichette non inserito o non corrispondente \nal numero di classi nella matrice di confusione.")
        labels = [str(i) for i in range(rows)]

    # calcola la larghezza delle celle
    cell_width = max([len(str(int(elem))) for elem in cm.view(-1)]) # dimensione massima tra tutti i dati
    cell_width = max(cell_width, max([len(str(lbl)) for lbl in labels])) # dimensione massima tra dati e etichette

    # stampa le righe della matrice di confusione
    for i in range(rows):

        # etichetta laterale
        side_label = f"{labels[i]:<{cell_width}}" + pad
        buffer_append(side_label, end='')

        # stampa la riga della matrice di confusione
        row = [BLD + f"{cm[i, j]:^{cell_width}}" + RST for j in range(cols)]
        buffer_append(' ' + " | ".join(row))

        # linea orizzontale di separazione
        if i < rows - 1: 
            buffer_append((' '*(len(side_label)))+
                          ('-'*(cell_width+2)+'+')*(cols-1)+
                          ('-'*(cell_width+2)))

    # intestazione della matrice di confusione
    headings = [f"{labels[i]:^{cell_width}}" for i in range(cols)]
    buffer_prepend((' '*(len(side_label)+1))+
                   ("   ".join(headings)))

    # stampa il buffer finale (indentato)
    print(textwrap.indent(buffer, indent), end=end)