"""Grafici e tabelle dalla validazione esterna su C8 (file JSON prodotti da validazione_esterna.py).

Uso:  python app/grafici_esterna.py app/risultati_kaggle/validazione_esterna
Crea la sottocartella "grafici" con:
  - controllo.txt                stesse immagini nello stesso ordine per tutti i modelli, duplicati in C8
  - riepilogo.csv                accuratezza (con IC 95% bootstrap), richiami, calibrazione, classi non viste
  - mcnemar.csv                  confronto a coppie sulla mappatura principale (test esatto di McNemar)
  - disaccordo.txt               accuratezza quando i modelli concordano e quando no
  - matrice_c8_octdl.png         dove finiscono le immagini di ogni classe C8, per modello
  - confidenza_soglia.png        quota con confidenza > 0.9, classi note contro classi mai viste
  - calibrazione.png             diagramma di affidabilita' sulla mappatura estesa

Il modello "ensemble" (media delle probabilita') e' calcolato qui, a posteriori: va presentato
come analisi esplorativa, non come un modello scelto prima di vedere i risultati. Usa sempre i
cinque modelli della prima validazione esterna (MODELLI_ENSEMBLE), cosi' aggiungere altri file
alla cartella non cambia i suoi numeri.

I modelli addestrati con mascheratura (mask_ratio > 0, solo ViTMAE) compaiono con il valore nel
nome, es. "vitmae-heavy mask 0.75", per distinguerli dalla stessa architettura senza mascheratura.
"""
import csv
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import roc_auc_score

# stessi colori, stile e ordine dei modelli dei grafici della cross-validation
from grafici_kfold import COLORI, GRIGLIA, ORDINE, TESTO, TESTO_SECONDARIO, plt

# corrispondenza classe C8 -> classe OCTDL. La principale usa solo le classi con lo stesso nome,
# l'estesa aggiunge le classi con un corrispettivo clinico (CNV e drusen sono forme di AMD,
# il foro maculare e' una patologia dell'interfaccia vitreo-retinica)
MAPPATURE = {
    "principale": {"AMD": "AMD", "DME": "DME", "NORMAL": "NO"},
    "estesa": {"AMD": "AMD", "DME": "DME", "NORMAL": "NO", "CNV": "AMD", "DRUSEN": "AMD", "MH": "VID"},
}
NON_VISTE = ["CSR", "DR"]   # patologie di C8 assenti da OCTDL: nessuna risposta e' corretta
ORDINE_C8 = ["AMD", "CNV", "DRUSEN", "DME", "MH", "NORMAL", "CSR", "DR"]
SOGLIA = 0.9
RICAMPIONAMENTI = 2000
ENSEMBLE = "ensemble"
MODELLI_ENSEMBLE = ["resnet18", "densenet121", "efficientnet_b0", "vit", "retfound"]


def carica(cartella):
    risultati = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(cartella).glob("*.json"))]
    risultati = [r for r in risultati if "classi_c8" in r and not r.get("prova")]
    if not risultati:
        sys.exit(f"Nessun file JSON di validazione esterna in {cartella}")
    for r in risultati:
        # "architettura" resta il nome del modello, "modello" diventa l'etichetta mostrata
        r["architettura"] = r["modello"]
        if r.get("mask_ratio"):
            r["modello"] = f"{r['modello']} mask {r['mask_ratio']:g}"
    risultati.sort(key=lambda r: (ORDINE.index(r["architettura"]) if r["architettura"] in ORDINE else len(ORDINE),
                                  r.get("mask_ratio") or 0))
    nomi = [r["modello"] for r in risultati]
    if len(set(nomi)) < len(nomi):
        sys.exit(f"Due file con lo stesso modello e la stessa mascheratura: {nomi}")
    for r in risultati:
        r["probabilita"] = np.array(r["probabilita"])
        r["predizioni"] = r["probabilita"].argmax(axis=1)
        r["classi_c8"] = np.array(r["classi_c8"])
    return risultati


def aggiungi_ensemble(risultati):
    # media delle probabilita' dei modelli: possibile solo se tutti hanno predetto le stesse immagini
    membri = [r for r in risultati if r["modello"] in MODELLI_ENSEMBLE]
    if len(membri) < 2:
        return risultati
    base = membri[0]
    probabilita = np.mean([r["probabilita"] for r in membri], axis=0)
    return risultati + [{
        "modello": ENSEMBLE, "membri": membri, "classi": base["classi"], "immagini": base["immagini"],
        "classi_c8": base["classi_c8"], "probabilita": probabilita, "predizioni": probabilita.argmax(axis=1),
    }]


def colore(r):
    nome = r.get("architettura", r["modello"])
    return COLORI[ORDINE.index(nome)] if nome in ORDINE else TESTO_SECONDARIO


def controlla(risultati, uscita):
    righe = []
    riferimento = risultati[0]
    for r in risultati:
        stesse = r["immagini"] == riferimento["immagini"]
        righe.append(f"{r['modello']}: commit {r['commit']}, seed {r['seed']}, mask_ratio {r.get('mask_ratio')}, "
                     f"epoche {r['epoche']}, "
                     f"immagini di training {r['immagini_train']}, immagini C8 {len(r['immagini'])}, "
                     f"stesse immagini di {riferimento['modello']}: {stesse}")
        if not stesse:
            sys.exit("\n".join(righe) + "\nI modelli non hanno predetto le stesse immagini: confronto impossibile")

    # un'immagine duplicata nel test riceve lo stesso vettore di probabilita' da ogni modello
    gruppi = {}
    for i in range(len(riferimento["immagini"])):
        chiave = tuple(np.round(np.concatenate([r["probabilita"][i] for r in risultati]), 6))
        gruppi.setdefault(chiave, []).append(riferimento["immagini"][i])
    duplicati = [g for g in gruppi.values() if len(g) > 1]
    righe.append(f"\nGruppi di immagini con probabilita' identiche in tutti i modelli (probabili duplicati): {len(duplicati)}")
    righe += ["  " + ", ".join(g) for g in duplicati]

    testo = "\n".join(righe)
    (uscita / "controllo.txt").write_text(testo + "\n", encoding="utf-8")
    print(testo)


def mappa(r, nome_mappatura):
    # immagini coperte dalla mappatura e la loro classe OCTDL attesa (come indice)
    corrispondenza = MAPPATURE[nome_mappatura]
    selezione = np.isin(r["classi_c8"], list(corrispondenza))
    attese = np.array([r["classi"].index(corrispondenza[c]) for c in r["classi_c8"][selezione]])
    return selezione, attese


def intervallo_bootstrap(corrette, generatore):
    n = len(corrette)
    medie = [corrette[generatore.integers(0, n, n)].mean() for _ in range(RICAMPIONAMENTI)]
    return np.percentile(medie, [2.5, 97.5])


def errore_calibrazione(confidenza, corrette, intervalli=15):
    # ECE: distanza media tra confidenza dichiarata e accuratezza, pesata per numero di immagini
    bordi = np.linspace(0, 1, intervalli + 1)
    errore = 0.0
    for basso, alto in zip(bordi[:-1], bordi[1:]):
        dentro = (confidenza > basso) & (confidenza <= alto)
        if dentro.any():
            errore += dentro.mean() * abs(corrette[dentro].mean() - confidenza[dentro].mean())
    return errore


def riepilogo(risultati, uscita):
    generatore = np.random.default_rng(0)
    classi_estesa = list(MAPPATURE["estesa"])
    intestazione = ["modello"]
    for m in MAPPATURE:
        intestazione += [f"accuracy {m}", f"IC95 basso {m}", f"IC95 alto {m}", f"balanced accuracy {m}"]
    intestazione += [f"recall {c}" for c in classi_estesa]
    intestazione += ["ECE estesa", "confidenza media estesa", f"copertura conf>{SOGLIA}",
                     f"accuracy conf>{SOGLIA}", f"accuracy conf<={SOGLIA}",
                     f"quota note conf>{SOGLIA}", f"quota non viste conf>{SOGLIA}", "AUROC non viste"]

    with open(uscita / "riepilogo.csv", "w", newline="", encoding="utf-8") as file:
        scrittore = csv.writer(file)
        scrittore.writerow(intestazione)
        for r in risultati:
            riga = [r["modello"]]
            confidenza = r["probabilita"].max(axis=1)
            for m in MAPPATURE:
                selezione, attese = mappa(r, m)
                corrette = r["predizioni"][selezione] == attese
                basso, alto = intervallo_bootstrap(corrette, generatore)
                bilanciata = np.mean([corrette[attese == k].mean() for k in np.unique(attese)])
                riga += [f"{corrette.mean():.3f}", f"{basso:.3f}", f"{alto:.3f}", f"{bilanciata:.3f}"]
            selezione, attese = mappa(r, "estesa")
            corrette = r["predizioni"][selezione] == attese
            for c in classi_estesa:
                riga.append(f"{corrette[r['classi_c8'][selezione] == c].mean():.3f}")
            conf = confidenza[selezione]
            sopra = conf > SOGLIA
            non_viste = np.isin(r["classi_c8"], NON_VISTE)
            riga += [f"{errore_calibrazione(conf, corrette):.3f}", f"{conf.mean():.3f}", f"{sopra.mean():.3f}",
                     f"{corrette[sopra].mean():.3f}", f"{corrette[~sopra].mean():.3f}",
                     f"{(confidenza[selezione] > SOGLIA).mean():.3f}",
                     f"{(confidenza[non_viste] > SOGLIA).mean():.3f}",
                     # 1 - confidenza come punteggio di "estraneita'": 0.5 = caso
                     f"{roc_auc_score(non_viste[selezione | non_viste], 1 - confidenza[selezione | non_viste]):.3f}"]
            scrittore.writerow(riga)
            print(f"{r['modello']:12} " + "  ".join(f"{h} {v}" for h, v in zip(intestazione[1:], riga[1:])
                                                   if h.startswith(("accuracy p", "accuracy e", "AUROC"))))


def mcnemar(risultati, uscita):
    # due famiglie di confronti, ciascuna con la propria correzione di Bonferroni:
    # "principale" = i cinque modelli della prima validazione e il loro ensemble (tutte le coppie),
    # "altri" = ogni coppia che coinvolge almeno un modello aggiunto dopo (es. le varianti di ViTMAE)
    principali = [r for r in risultati if r["modello"] in MODELLI_ENSEMBLE + [ENSEMBLE]]
    famiglie = {"principale": list(combinations(principali, 2)),
                "altri": [(a, b) for a, b in combinations(risultati, 2)
                          if a not in principali or b not in principali]}
    with open(uscita / "mcnemar.csv", "w", newline="", encoding="utf-8") as file:
        scrittore = csv.writer(file)
        scrittore.writerow(["famiglia", "primo", "secondo", "corrette solo primo", "corrette solo secondo",
                            "p esatto", "soglia Bonferroni", "significativo"])
        for famiglia, confronti in famiglie.items():
            soglia = 0.05 / len(confronti) if confronti else 0.05
            for a, b in confronti:
                selezione, attese = mappa(a, "principale")
                giusto_a = a["predizioni"][selezione] == attese
                giusto_b = b["predizioni"][selezione] == attese
                solo_a, solo_b = int((giusto_a & ~giusto_b).sum()), int((~giusto_a & giusto_b).sum())
                p = binomtest(solo_a, solo_a + solo_b).pvalue if solo_a + solo_b else 1.0
                scrittore.writerow([famiglia, a["modello"], b["modello"], solo_a, solo_b, f"{p:.4g}",
                                    f"{soglia:.4f}", p < soglia])
                print(f"[{famiglia}] {a['modello']} vs {b['modello']}: solo il primo {solo_a}, "
                      f"solo il secondo {solo_b}, p {p:.4g}")


def disaccordo(risultati, uscita):
    ensemble = next(r for r in risultati if r["modello"] == ENSEMBLE)
    modelli = ensemble["membri"]
    predizioni = np.array([r["predizioni"] for r in modelli])
    discordi = ~(predizioni == predizioni[0]).all(axis=0)
    selezione, attese = mappa(ensemble, "principale")
    corrette = ensemble["predizioni"][selezione] == attese
    d = discordi[selezione]
    non_viste = np.isin(ensemble["classi_c8"], NON_VISTE)
    note = np.isin(ensemble["classi_c8"], list(MAPPATURE["estesa"]))
    testo = (
        f"Modelli: {', '.join(r['modello'] for r in modelli)}\n"
        f"Mappatura principale ({selezione.sum()} immagini):\n"
        f"  concordano su {(~d).sum()} immagini ({(~d).mean():.1%}), ensemble corretto nel {corrette[~d].mean():.1%}\n"
        f"  discordano su {d.sum()} immagini ({d.mean():.1%}), ensemble corretto nel {corrette[d].mean():.1%}\n"
        f"Disaccordo come rilevatore di classi mai viste: quota sulle note {discordi[note].mean():.1%}, "
        f"sulle mai viste {discordi[non_viste].mean():.1%}, "
        f"AUROC {roc_auc_score(non_viste[note | non_viste], discordi[note | non_viste]):.3f}\n"
    )
    (uscita / "disaccordo.txt").write_text(testo, encoding="utf-8")
    print(testo)


def matrice_c8_octdl(risultati, uscita):
    modelli = [r for r in risultati if r["modello"] != ENSEMBLE]
    classi = modelli[0]["classi"]
    attese = MAPPATURE["estesa"]
    figura, assi = plt.subplots(1, len(modelli), figsize=(3.6 * len(modelli), 4.6), sharey=True)
    assi = np.atleast_1d(assi)
    for asse, r in zip(assi, modelli):
        conteggi = np.array([[np.sum((r["classi_c8"] == c) & (r["predizioni"] == k)) for k in range(len(classi))]
                             for c in ORDINE_C8])
        percentuali = conteggi / conteggi.sum(axis=1, keepdims=True)
        asse.imshow(percentuali, cmap="Blues", vmin=0, vmax=1, aspect="auto")
        for i, c in enumerate(ORDINE_C8):
            for j in range(len(classi)):
                if percentuali[i, j] >= 0.05:
                    asse.text(j, i, f"{percentuali[i, j] * 100:.0f}", ha="center", va="center", fontsize=8,
                              color="white" if percentuali[i, j] > 0.6 else TESTO)
            if c in attese:   # cella della risposta attesa
                j = classi.index(attese[c])
                asse.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=TESTO, linewidth=1.5))
        asse.axhline(len(ORDINE_C8) - len(NON_VISTE) - 0.5, color=TESTO_SECONDARIO, linestyle="--", linewidth=1)
        asse.set_xticks(range(len(classi)), classi, fontsize=8)
        asse.set_yticks(range(len(ORDINE_C8)), ORDINE_C8)
        asse.grid(False)
        asse.set_title(r["modello"], color=TESTO)
        asse.set_xlabel("Classe OCTDL predetta")
    assi[0].set_ylabel("Classe C8 (sotto la linea: mai viste)")
    figura.suptitle("% delle immagini di ogni classe C8 assegnata a ciascuna classe OCTDL (bordo = classe attesa)",
                    color=TESTO)
    figura.tight_layout()
    figura.savefig(uscita / "matrice_c8_octdl.png")
    plt.close(figura)


def confidenza_soglia(risultati, uscita):
    figura, asse = plt.subplots(figsize=(7.5, 0.7 * len(risultati) + 1.4))
    for i, r in enumerate(risultati):
        confidenza = r["probabilita"].max(axis=1)
        note = (confidenza[np.isin(r["classi_c8"], list(MAPPATURE["estesa"]))] > SOGLIA).mean() * 100
        non_viste = (confidenza[np.isin(r["classi_c8"], NON_VISTE)] > SOGLIA).mean() * 100
        y = len(risultati) - 1 - i
        asse.plot([note, non_viste], [y, y], color=GRIGLIA, linewidth=2.5, zorder=1)
        asse.scatter(note, y, s=70, color=TESTO_SECONDARIO, zorder=2, label="classi note" if i == 0 else None)
        asse.scatter(non_viste, y, s=70, color=COLORI[0], zorder=3, label="classi mai viste" if i == 0 else None)
        asse.annotate(f"{note:.0f}", (note, y), xytext=(0, 8), textcoords="offset points", ha="center",
                      fontsize=8, color=TESTO_SECONDARIO)
        asse.annotate(f"{non_viste:.0f}", (non_viste, y), xytext=(0, -14), textcoords="offset points",
                      ha="center", fontsize=8, color=TESTO)
    asse.set_yticks(range(len(risultati)), [r["modello"] for r in reversed(risultati)])
    asse.set_xlim(0, 100)
    asse.set_ylim(-0.7, len(risultati) - 0.3)
    asse.set_xlabel(f"% di immagini con probabilita' massima > {SOGLIA}")
    asse.grid(axis="y", visible=False)
    asse.legend(loc="lower left", fontsize=8)
    asse.set_title("Le patologie mai viste ricevono la stessa confidenza di quelle note", color=TESTO)
    figura.tight_layout()
    figura.savefig(uscita / "confidenza_soglia.png")
    plt.close(figura)


def calibrazione(risultati, uscita, intervalli=10):
    figura, assi = plt.subplots(1, len(risultati), figsize=(3.2 * len(risultati), 3.6), sharey=True)
    assi = np.atleast_1d(assi)
    bordi = np.linspace(0, 1, intervalli + 1)
    for asse, r in zip(assi, risultati):
        selezione, attese = mappa(r, "estesa")
        confidenza = r["probabilita"].max(axis=1)[selezione]
        corrette = r["predizioni"][selezione] == attese
        centri, accuratezze, quote = [], [], []
        for basso, alto in zip(bordi[:-1], bordi[1:]):
            dentro = (confidenza > basso) & (confidenza <= alto)
            if dentro.any():
                centri.append(confidenza[dentro].mean())
                accuratezze.append(corrette[dentro].mean())
                quote.append(dentro.mean())
        asse.plot([0, 1], [0, 1], color=TESTO_SECONDARIO, linestyle=":", linewidth=1)
        # area del punto proporzionale alla quota di immagini nell'intervallo
        asse.scatter(centri, accuratezze, s=np.array(quote) * 400 + 8, color=colore(r), zorder=3,
                     clip_on=False)
        asse.plot(centri, accuratezze, color=colore(r), linewidth=1.5)
        asse.set(xlim=(0, 1), ylim=(0, 1), xlabel="Confidenza dichiarata",
                 title=f"{r['modello']} (ECE {errore_calibrazione(confidenza, corrette):.2f})")
    assi[0].set_ylabel("Accuratezza effettiva")
    figura.suptitle("Calibrazione su C8, mappatura estesa (punti piu' grandi = piu' immagini; diagonale = perfetta)",
                    color=TESTO)
    figura.tight_layout()
    figura.savefig(uscita / "calibrazione.png")
    plt.close(figura)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python app/grafici_esterna.py <cartella con i file JSON della validazione esterna>")
    cartella = Path(sys.argv[1])
    uscita = cartella / "grafici"
    uscita.mkdir(exist_ok=True)

    risultati = carica(cartella)
    controlla(risultati, uscita)
    con_ensemble = aggiungi_ensemble(risultati)
    riepilogo(con_ensemble, uscita)
    mcnemar(con_ensemble, uscita)
    if any(r["modello"] == ENSEMBLE for r in con_ensemble):
        disaccordo(con_ensemble, uscita)
    matrice_c8_octdl(risultati, uscita)
    confidenza_soglia(con_ensemble, uscita)
    calibrazione(con_ensemble, uscita)
    print(f"Grafici e tabelle salvati in {uscita}")


if __name__ == "__main__":
    main()
