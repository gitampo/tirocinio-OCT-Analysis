"""Grafici e tabelle dai risultati della cross-validation (file JSON prodotti da kfoldcv).

Uso:  python app/grafici_kfold.py app/risultati_kaggle/b7806f9
Crea la sottocartella "grafici" con:
  - controllo_fold.txt            stessi fold tra modelli e pazienti mai in due fold
  - distribuzione_classi.csv      pazienti e immagini per classe in ogni fold
  - riepilogo.csv                 media e deviazione standard per modello
  - boxplot_fold.png              variabilita' tra i fold, per modello
  - <modello>_confusione.png      matrice di confusione sommata sui 5 fold
  - <modello>_roc_pr.png          curve ROC e precision-recall one-vs-rest
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import auc, average_precision_score, confusion_matrix, precision_recall_curve, roc_curve

# colori in ordine fisso (palette validata per daltonismo) e stili di linea come seconda codifica
COLORI = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
LINEE = ["-", "--", "-.", ":", "-", "--", "-."]
TESTO, TESTO_SECONDARIO, GRIGLIA = "#0b0b0b", "#52514e", "#e4e3df"

# ordine fisso dei modelli: prima le CNN, poi i transformer, poi RETFound.
# Il colore di un modello e' legato alla sua posizione qui, quindi non cambia tra un grafico e l'altro
ORDINE = ["resnet18", "densenet121", "efficientnet_b0", "vit", "vitmae-light", "vitmae-heavy", "retfound"]


def posizione(r):
    return ORDINE.index(r["modello"]) if r["modello"] in ORDINE else len(ORDINE)


METRICHE = {
    "eval_accuracy": "Accuracy",
    "eval_balanced_accuracy": "Balanced accuracy",
    "eval_f1_score_macro": "F1 macro",
    "eval_MCC": "MCC",
}

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": TESTO_SECONDARIO, "axes.labelcolor": TESTO,
    "xtick.color": TESTO_SECONDARIO, "ytick.color": TESTO_SECONDARIO, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRIGLIA, "grid.linewidth": 0.8,
    "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def carica(cartella):
    risultati = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(cartella).rglob("*.json"))]
    if not risultati:
        sys.exit(f"Nessun file JSON in {cartella}")
    return sorted(risultati, key=posizione)

def controlla_fold(risultati, uscita):
    righe = []
    riferimento = risultati[0]
    for r in risultati:
        stessi = [f["immagini"] for f in r["fold"]] == [f["immagini"] for f in riferimento["fold"]]
        pazienti = [set(f["pazienti"]) for f in r["fold"]]
        disgiunti = all(a.isdisjoint(b) for i, a in enumerate(pazienti) for b in pazienti[i + 1:])
        righe.append(
            f"{r['modello']}: commit {r['commit']}, stessi fold di {riferimento['modello']}: {stessi}, "
            f"pazienti mai in due fold: {disgiunti}, pazienti {len(set().union(*pazienti))}, "
            f"immagini {sum(len(f['immagini']) for f in r['fold'])}"
        )
    testo = "\n".join(righe)
    (uscita / "controllo_fold.txt").write_text(testo + "\n", encoding="utf-8")
    print(testo)

def distribuzione_classi(risultati, uscita):
    # i fold sono gli stessi per tutti i modelli (vedi controllo_fold.txt), quindi basta il primo
    r = risultati[0]
    classi = r["classi"]
    righe = []
    for f in r["fold"]:
        conteggi = np.bincount(f["etichette"], minlength=len(classi))
        righe.append((f"Fold {f['fold']}", len(set(f["pazienti"])), conteggi))
    pazienti_totali = len(set().union(*(f["pazienti"] for f in r["fold"])))
    righe.append(("Totale", pazienti_totali, sum(conteggi for _, _, conteggi in righe)))

    with open(uscita / "distribuzione_classi.csv", "w", newline="", encoding="utf-8") as file:
        scrittore = csv.writer(file)
        scrittore.writerow(["fold", "pazienti", "immagini"] + classi + [f"% {c}" for c in classi])
        for nome, pazienti, conteggi in righe:
            percentuali = conteggi / conteggi.sum() * 100
            scrittore.writerow([nome, pazienti, conteggi.sum()] + conteggi.tolist()
                               + [f"{p:.1f}" for p in percentuali])
            print(f"{nome:8} pazienti {pazienti:3}  immagini {conteggi.sum():4}  "
                  + "  ".join(f"{c} {n:4}" for c, n in zip(classi, conteggi)))



def dati_aggregati(r):
    # predizioni dei 5 fold concatenate: ogni immagine compare una sola volta
    etichette = np.concatenate([f["etichette"] for f in r["fold"]])
    predizioni = np.concatenate([f["predizioni"] for f in r["fold"]])
    probabilita = np.concatenate([f["probabilita"] for f in r["fold"]])
    return etichette, predizioni, probabilita


def riepilogo(risultati, uscita):
    intestazione = ["modello"]
    for nome in METRICHE.values():
        intestazione += [f"{nome} media", f"{nome} dev.std"]
    classi = risultati[0]["classi"]
    intestazione += [f"AUC {c}" for c in classi] + ["AUC macro"]

    with open(uscita / "riepilogo.csv", "w", newline="", encoding="utf-8") as file:
        scrittore = csv.writer(file)
        scrittore.writerow(intestazione)
        for r in risultati:
            riga = [r["modello"]]
            for chiave in METRICHE:
                valori = [f["metriche"][chiave] for f in r["fold"]]
                riga += [f"{np.mean(valori):.3f}", f"{np.std(valori, ddof=1):.3f}"]
            etichette, _, probabilita = dati_aggregati(r)
            aree = []
            for k in range(len(classi)):
                fpr, tpr, _ = roc_curve(etichette == k, probabilita[:, k])
                aree.append(auc(fpr, tpr))
            riga += [f"{a:.3f}" for a in aree] + [f"{np.mean(aree):.3f}"]
            scrittore.writerow(riga)


def boxplot_fold(risultati, uscita):
    modelli = [r["modello"] for r in risultati]
    figura, assi = plt.subplots(1, len(METRICHE), figsize=(3.2 * len(METRICHE), 3.6), sharey=False)
    fuori_scala = False
    for asse, (chiave, nome) in zip(assi, METRICHE.items()):
        valori = [[f["metriche"][chiave] for f in r["fold"]] for r in risultati]
        scatola = asse.boxplot(valori, widths=0.5, patch_artist=True, showfliers=False,
                               medianprops={"color": TESTO, "linewidth": 1.5})
        for i, (patch, punti, r) in enumerate(zip(scatola["boxes"], valori, risultati)):
            colore = COLORI[posizione(r)]
            patch.set_facecolor(colore + "40")
            patch.set_edgecolor(colore)
            # i 5 fold come punti, perche' con 5 valori la scatola da sola dice poco
            x = np.full(len(punti), i + 1) + np.linspace(-0.12, 0.12, len(punti))
            asse.scatter(x, punti, s=22, color=colore, edgecolor="white", linewidth=0.8, zorder=3)

        # un fold anomalo (molto sotto tutti gli altri) schiaccerebbe l'asse e nasconderebbe
        # le differenze tra i modelli: l'asse si ferma sopra di lui e il fold e' segnato con
        # un triangolo sul bordo e il suo valore
        tutti = np.concatenate(valori)
        q1, q3 = np.percentile(tutti, [25, 75])
        soglia = q1 - 3 * (q3 - q1)
        if (tutti < soglia).any():
            fuori_scala = True
            fondo = tutti[tutti >= soglia].min() - 0.02
            asse.set_ylim(bottom=fondo)
            for i, (punti, r) in enumerate(zip(valori, risultati)):
                for v in punti:
                    if v < soglia:
                        asse.scatter(i + 1, fondo, marker="v", s=45, color=COLORI[posizione(r)],
                                     clip_on=False, zorder=4)
                        asse.annotate(f"{v:.2f}", (i + 1, fondo), xytext=(6, 2), textcoords="offset points",
                                      fontsize=8, color=TESTO_SECONDARIO)

        asse.set_title(nome, color=TESTO)
        asse.set_xticks(range(1, len(modelli) + 1), modelli, rotation=30, ha="right")
        asse.grid(axis="x", visible=False)
    titolo = "Variabilita' tra i 5 fold (ogni punto e' un fold"
    titolo += "; \u25bc = fold fuori scala, con il suo valore)" if fuori_scala else ")"
    figura.suptitle(titolo, color=TESTO)
    figura.tight_layout()
    figura.savefig(uscita / "boxplot_fold.png")
    plt.close(figura)


def matrice_confusione(r, uscita):
    etichette, predizioni, _ = dati_aggregati(r)
    classi = r["classi"]
    conteggi = confusion_matrix(etichette, predizioni, labels=range(len(classi)))
    percentuali = conteggi / conteggi.sum(axis=1, keepdims=True)

    figura, asse = plt.subplots(figsize=(6, 5.2))
    immagine = asse.imshow(percentuali, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(classi)):
        for j in range(len(classi)):
            colore = "white" if percentuali[i, j] > 0.6 else TESTO
            asse.text(j, i, f"{conteggi[i, j]}\n{percentuali[i, j]:.0%}", ha="center", va="center",
                      fontsize=8, color=colore)
    asse.set_xticks(range(len(classi)), classi)
    asse.set_yticks(range(len(classi)), classi)
    asse.set_xlabel("Classe predetta")
    asse.set_ylabel("Classe vera")
    asse.grid(False)
    asse.set_title(f"{r['modello']}: matrice di confusione (5 fold sommati)", color=TESTO)
    barra = figura.colorbar(immagine, ax=asse, fraction=0.046)
    barra.set_label("Frazione della classe vera (recall per riga)")
    figura.savefig(uscita / f"{r['modello']}_confusione.png")
    plt.close(figura)


def curve_roc_pr(r, uscita):
    etichette, _, probabilita = dati_aggregati(r)
    classi = r["classi"]
    figura, (asse_roc, asse_pr) = plt.subplots(1, 2, figsize=(11, 4.8))
    for k, classe in enumerate(classi):
        vero = etichette == k
        stile = {"color": COLORI[k], "linestyle": LINEE[k], "linewidth": 2}
        fpr, tpr, _ = roc_curve(vero, probabilita[:, k])
        asse_roc.plot(fpr, tpr, label=f"{classe} (AUC {auc(fpr, tpr):.3f}, n={vero.sum()})", **stile)
        precisione, richiamo, _ = precision_recall_curve(vero, probabilita[:, k])
        ap = average_precision_score(vero, probabilita[:, k])
        asse_pr.plot(richiamo, precisione, label=f"{classe} (AP {ap:.3f}, prev. {vero.mean():.2f})", **stile)
    asse_roc.plot([0, 1], [0, 1], color=TESTO_SECONDARIO, linestyle=":", linewidth=1)
    asse_roc.set(xlabel="Tasso di falsi positivi", ylabel="Tasso di veri positivi (recall)",
                 title="ROC one-vs-rest", xlim=(0, 1), ylim=(0, 1.01))
    asse_pr.set(xlabel="Recall", ylabel="Precision", title="Precision-recall one-vs-rest",
                xlim=(0, 1), ylim=(0, 1.01))
    asse_roc.legend(loc="lower right", fontsize=8)
    asse_pr.legend(loc="lower left", fontsize=8)
    figura.suptitle(f"{r['modello']}: predizioni dei 5 fold di validazione unite", color=TESTO)
    figura.tight_layout()
    figura.savefig(uscita / f"{r['modello']}_roc_pr.png")
    plt.close(figura)


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python app/grafici_kfold.py <cartella con i file JSON>")
    cartella = Path(sys.argv[1])
    uscita = cartella / "grafici"
    uscita.mkdir(exist_ok=True)

    risultati = carica(cartella)
    controlla_fold(risultati, uscita)
    distribuzione_classi(risultati, uscita)    
    riepilogo(risultati, uscita)
    boxplot_fold(risultati, uscita)
    for r in risultati:
        matrice_confusione(r, uscita)
        curve_roc_pr(r, uscita)
    print(f"Grafici e tabelle salvati in {uscita}")


if __name__ == "__main__":
    main()
