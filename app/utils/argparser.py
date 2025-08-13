import argparse
from deeplearning.training import train
from deeplearning.testing import test
from deeplearning.utils import available_checkpoints, available_models

def help_formatter(prog):
    return argparse.HelpFormatter(prog, max_help_position=35, width=75)

def get_args():
    # istanzia il parser
    parser = argparse.ArgumentParser(
        description='CLI di OCT-Analysis, progetto di analisi delle immagini OCT per scopi medici.',
        formatter_class=help_formatter,
        add_help=False
    )

    # imposta gli argument disponibili
    parser.add_argument('-h', '--help', action='help', help='Mostra questo messaggio di help')
    
    # sottoparser per dividere comandi
    subparsers = parser.add_subparsers(dest='command')

    # definisce le scelte per i comandi
    checkpoints_choices = '{'+', '.join(available_checkpoints())+'}' if available_checkpoints() else "(nessun checkpoint disponibile)"
    models_choices = '{'+', '.join(available_models())+'}' if available_models() else "(nessun modello disponibile)"

    # parser per il comando di training
    train_parser = subparsers.add_parser(
        'train', 
        description='Comando per l\'esecuzione del training di un modello',
        help='Comando per l\'esecuzione del training di un modello', 
        formatter_class=help_formatter,
        add_help=False)
    train_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help='Mostra questo messaggio di help')
    train_parser.add_argument(
        '-m','--model',
        required=True,
        action='store',
        metavar='MODEL',
        choices=available_models(),
        help=f'Il modello di cui eseguire il training.'
    )
    train_mode = train_parser.add_mutually_exclusive_group(required=True) 
    train_mode.add_argument(
        '-s', '--from-scratch',
        action='store_true',
        help='Esegue il training da zero'
    )
    train_mode.add_argument(
        '-l','--load',
        action='store',
        metavar='CHCKPNT',
        choices=available_checkpoints(),
        help=f"Carica i checkpoints prima del training."
    )

    # parser per il comando di testing
    test_parser = subparsers.add_parser(
        'test', 
        description='Comando per l\'esecuzione del testing di un modello',
        help='Comando per l\'esecuzione del testing di un modello', 
        formatter_class=help_formatter,
        add_help=False)
    test_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help='Mostra questo messaggio di help')
    test_parser.add_argument(
        '-m','--model',
        required=True,
        action='store',
        metavar='MODEL',
        choices=available_models(),
        help=f'Il modello di cui eseguire il testing'
    )
    test_parser.add_argument(
        '-l','--load',
        required=True,
        action='store',
        metavar='CHCKPNT',
        choices=available_checkpoints(),
        help=f'Carica i checkpoints prima del testing'
    )

    # parser per il comando di listing
    list_parser = subparsers.add_parser(
        'list', 
        description='Comando per elencare i modelli e i checkpoints disponibili',
        help='Comando per elencare i modelli e i checkpoints disponibili', 
        formatter_class=help_formatter,
        add_help=False)
    list_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help='Mostra questo messaggio di help')
    list_what = list_parser.add_mutually_exclusive_group(required=True)
    list_what.add_argument(
        '-m','--models',
        action='store_true',
        help=f'Lista i checkpoints disponibili e caricabili'
    )
    list_what.add_argument(
        '-c','--checkpoints',
        action='store_true',
        help=f'Lista i checkpoints disponibili e caricabili'
    )

    # ottiene gli argument
    args = parser.parse_args()

    return args

def check_model_and_checkpoint(args):
    if args.from_scratch: return
    if args.model != args.load.split('/')[0]:
        raise ValueError(f"Il modello '{args.model}' non corrisponde al checkpoint '{args.load}'")

def handle_args(args):
    # gestisce gli arguments per il comando di training
    if args.command == 'train':
        check_model_and_checkpoint(args)
        checkpoint_to_load = args.load if args.from_scratch else None
        train(model=args.model, checkpoint_name=checkpoint_to_load)

    # gestisce gli arguments per il comando di testing
    elif args.command == 'test':
        check_model_and_checkpoint(args)
        test(model=args.model, checkpoint_name=args.load)

    # gestisce gli arguments per il comando di listing
    elif args.command == 'list':
        if args.models:
            print("Modelli disponibili:")
            for model in available_models():
                print(f"- {model}")
            print('Info: usarli con il flag -m o --model (es. -m model)')
        elif args.checkpoints:
            print("Checkpoints disponibili:")
            for checkpoint in available_checkpoints():
                print(f"- {checkpoint}")
            print('Info: usarli con il flag -l o --load (es. -l model/checkpoint)')

    # se ha eseguito un comando termina l'esecuzione, altrimenti continua
    if args.command: exit(0)