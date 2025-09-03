import argparse
import textwrap
import sys
from deeplearning import (
    DEFAULT_DATASET, 
    DEFAULT_SEED,
    DEFAULT_KFOLDS
)
from deeplearning.availables import (
    available_checkpoints, 
    available_models, 
    available_datasets
)
from utils.print import BLD, DIM, RST, print_info, print_list

# costanti per la formattazione dell'help
description_WIDTH = 45
INDENT_INCREMENT = 3
HELP_INDENTATION_SIZE = 10
HELP_INDENTATION = ' ' * HELP_INDENTATION_SIZE
EXAMPLES_INDENTATION = ' ' * INDENT_INCREMENT
PROG = sys.argv[0]

def help_formatter(prog):
    return argparse.RawTextHelpFormatter(prog, indent_increment=INDENT_INCREMENT, max_help_position=0)

def description(text):
    # formatta correttamente la descrizione
    return BLD + text + RST

def help(text):
    # formatta correttamente la descrizione dell'help
    # 1) divide il testo in righe; 2) applica il wrapping per riga; 3) applica l'indentazione
    text_list = text.split('\n')
    text_list = [textwrap.fill(text, width=description_WIDTH) for text in text_list]
    text = textwrap.indent('\n'.join(text_list), HELP_INDENTATION)
    return text

def epilog(example_list):
    # formatta correttamente gli esempi
    text_examples = ''
    for (example, description) in example_list:
        text_examples += DIM + f"# {description}\n" + RST
        text_examples += f"{example}\n\n"

    text = 'examples:\n' + textwrap.indent(text_examples, EXAMPLES_INDENTATION)

    return text

def setup_train_parser(subparsers):
    # costruzione del comando train
    train_parser = subparsers.add_parser(
        'train', 
        description=description("Comando per l'esecuzione del training di un modello"),
        help=help("Comando per l'esecuzione del training di un modello"),
        formatter_class=help_formatter,
        epilog=epilog([(f"python {PROG} train --from-scratch vitmae-light","Training da zero"), 
                         (f"python {PROG} train --from-checkpoint vitmae-light/base","Training da checkpoint"),
                         (f"python {PROG} train -s vitmae-light --dataset OCTDL -S 1234","Training da zero con dataset e seed specificati")]),
        add_help=False)

    # help del comando train
    train_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help=help('Mostra questo messaggio di help.')
    )

    # costruzione degli argomenti del comando train
    train_mode = train_parser.add_mutually_exclusive_group(required=True)
    train_mode.add_argument(
        '-s','--from-scratch',
        action='store',
        metavar='MODEL',
        choices=available_models(),
        help=help('Avvia il training da zero, del modello specificato.\n(vedi anche "list --models")')
    )
    train_mode.add_argument(
        '-c','--from-checkpoint',
        action='store',
        metavar='CHECKPOINT',
        choices=available_checkpoints(),
        help=help('Avvia il training a partire dal checkpoint specificato.\n(vedi anche "list --checkpoints")')
    )
    train_parser.add_argument(
        '-d','--dataset',
        action='store',
        metavar='DATASET',
        default=DEFAULT_DATASET,
        choices=available_datasets(),
        help=help(f'Specifica il dataset da utilizzare per il training. \n(vedi anche "list --datasets") \n(default: "{DEFAULT_DATASET}")')
    )
    train_parser.add_argument(
        '-S','--seed',
        action='store',
        metavar='SEED',
        default=DEFAULT_SEED,
        type=int,
        help=help(f'Specifica il seed da utilizzare nel training, a scopo di riproducibilità. \n(default: {DEFAULT_SEED})')
    )

def setup_test_parser(subparsers):
    # costruzione del comando test
    test_parser = subparsers.add_parser(
        'test', 
        description=description("Comando per l'esecuzione del testing di un modello"),
        help=help("Comando per l'esecuzione del testing di un modello"), 
        formatter_class=help_formatter,
        epilog=epilog([(f"python {PROG} test --checkpoint vitmae-light/base","Testing del checkpoint selezionato"),
                         (f"python {PROG} test -c vitmae-light/base --dataset OCTDL -S 1234","Testing del checkpoint su dataset e seed specificati")]),
        add_help=False)

    # help del comando test
    test_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help=help('Mostra questo messaggio di help.')
    )

    # costruzione degli argomenti del comando test
    test_parser.add_argument(
        '-c','--checkpoint',
        required=True,
        action='store',
        metavar='CHECKPOINT',
        choices=available_checkpoints(),
        help=help('Carica i checkpoints prima del testing. \n(vedi anche "list --checkpoints")')
    )
    test_parser.add_argument(
        '-d','--dataset',
        action='store',
        metavar='DATASET',
        default=DEFAULT_DATASET,
        choices=available_datasets(),
        help=help(f'Specifica il dataset da utilizzare per il testing. \n(vedi anche "list --datasets") \n(default: "{DEFAULT_DATASET}")')
    )
    test_parser.add_argument(
        '-S','--seed',
        action='store',
        metavar='SEED',
        default=DEFAULT_SEED,
        type=int,
        help=help(f'Specifica il seed da utilizzare nel testing, a scopo di riproducibilità. \n(default: {DEFAULT_SEED})')
    )

def setup_kfoldcv_parser(subparsers):
    # costruzione del comando kfoldcv
    kfoldcv_parser = subparsers.add_parser(
        'kfoldcv', 
        description=description("Comando per l'esecuzione del K-Fold Cross Validation di un modello"),
        help=help("Comando per l'esecuzione del K-Fold Cross Validation di un modello"),
        formatter_class=help_formatter,
        epilog=epilog([(f"python {PROG} kfoldcv --model vitmae-light",f"K-Fold del modello selezionato (k={DEFAULT_KFOLDS})"),
                         (f"python {PROG} kfoldcv --model vitmae-light -k 7 -S 1234","K-Fold a sette fold, con seed 1234")]),
        add_help=False)

    # help del comando kfoldcv
    kfoldcv_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help=help('Mostra questo messaggio di help.')
    )

    kfoldcv_parser.add_argument(
        '-m','--model',
        action='store',
        metavar='MODEL',
        required=True,
        choices=available_models(),
        help=help('Specifica il modello da utilizzare per il K-Fold Cross Validation. \n(vedi anche "list --models")')
    )
    kfoldcv_parser.add_argument(
        '-k', '--num-folds',
        action='store',
        metavar='KFOLDS',
        default=DEFAULT_KFOLDS,
        type=int,
        help=help(f'Specifica il numero di fold da utilizzare nel K-Fold Cross Validation. \n(default: {DEFAULT_KFOLDS})')
    )
    kfoldcv_parser.add_argument(
        '-S','--seed',
        action='store',
        metavar='SEED',
        default=DEFAULT_SEED,
        type=int,
        help=help(f'Specifica il seed da utilizzare nel K-Fold Cross Validation, a scopo di riproducibilità. \n(default: {DEFAULT_SEED})')
    )

def setup_list_parser(subparsers):
    # costruzione del comando list
    list_parser = subparsers.add_parser(
        'list', 
        description=description('Comando per elencare modelli, checkpoints e dataset disponibili'),
        help=help('Comando per elencare modelli, checkpoints e dataset disponibili'), 
        formatter_class=help_formatter,
        epilog=epilog([(f"python {PROG} list --checkpoints","Listing dei checkpoint disponibili")]),
        add_help=False)
    
    # help del comando list
    list_parser.add_argument(
        '-h', '--help', 
        action='help', 
        help=help('Mostra questo messaggio di help.')
    )

    # costruzione delle possibilità di listing
    list_what = list_parser.add_mutually_exclusive_group(required=True)
    list_what.add_argument(
        '-m','--models',
        action='store_true',
        help=help('Lista dei modelli disponibili.')
    )
    list_what.add_argument(
        '-c','--checkpoints',
        action='store_true',
        help=help('Lista dei checkpoints disponibili.')
    )
    list_what.add_argument(
        '-d','--datasets',
        action='store_true',
        help=help('Lista dei dataset disponibili.')
    )

def get_args():
    # istanzia il parser
    parser = argparse.ArgumentParser(
        description=description('CLI di OCT-Analysis, progetto di analisi delle immagini OCT per scopi medici.'),
        formatter_class=help_formatter,
        add_help=False
    )

    # help principale
    parser.add_argument('-h', '--help', action='help', help=help('Mostra questo messaggio di help.'))

    # oggetto per costruire i comandi attraverso appositi sotto-parser
    subparsers = parser.add_subparsers(dest='command', metavar='COMMAND')

    # setup dei comandi
    setup_train_parser(subparsers)
    setup_test_parser(subparsers)
    setup_kfoldcv_parser(subparsers)
    setup_list_parser(subparsers)

    # ottiene gli argument
    args = parser.parse_args()

    return args

def check_model_and_checkpoint(args):
    # verifica che il modello e il checkpoint corrispondano
    if not args.load: return
    if args.model != args.load.split('/')[0]:
        raise ValueError(f"Il modello '{args.model}' non corrisponde al checkpoint '{args.load}'")

def handle_args(args):

    # gestisce il comando di training
    if args.command == 'train':
        # training da zero
        if args.from_scratch:
            from deeplearning.training import train # lazy loading
            train(model_name=args.from_scratch,
                  dataset_name=args.dataset or DEFAULT_DATASET,
                  from_scratch=True)
            
        # training da checkpoint
        elif args.from_checkpoint:
            from deeplearning.training import train # lazy loading

            model_name, checkpoint_name = args.from_checkpoint.split('/') # <model/checkpoint>
            train(model_name=model_name,
                  checkpoint_name=checkpoint_name,
                  dataset_name=args.dataset,
                  seed=args.seed,
                  from_scratch=False)
            
    # gestisce il comando di testing
    elif args.command == 'test':
        from deeplearning.testing import test # lazy loading

        model_name, checkpoint_name = args.checkpoint.split('/') # <model/checkpoint>
        test(model_name=model_name,
              checkpoint_name=checkpoint_name,
              dataset_name=args.dataset,
              seed=args.seed)

    # gestisce il comando di kfoldcv
    elif args.command == 'kfoldcv':
        from deeplearning.kfoldcv import kfold_cv # lazy loading

        kfold_cv(model_name=args.model,
                  seed=args.seed,
                  num_folds=args.num_folds)

    # gestisce il comando di listing
    elif args.command == 'list':
        if args.models:
            print('Modelli disponibili:')
            print_list(available_models())
            print_info('Info: usarli con il flag -model o --from-scratch (es. --model <model>)')
        elif args.checkpoints:
            print('Checkpoints disponibili:')
            print_list(available_checkpoints())
            print_info('Info: usarli con il flag -c o --from-checkpoint (es. -c <model/checkpoint>)')
        elif args.datasets:
            print('Datasets disponibili:')
            print_list(available_datasets())
            print_info('Info: usarli con il flag -d o --dataset (es. -d <dataset>)')

    # se ha eseguito un comando termina l'esecuzione, altrimenti continua
    if args.command: exit(0)