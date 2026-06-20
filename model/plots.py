"""
File with codes for all the plots
"""
import matplotlib.pyplot as plt
import arviz as az

from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

from config import TARGET, THRESHOLD


# adjusting the data -> we can only display two can be seen that two features have too little power to predict the model
def plot_training_data(df):
    plt.figure(figsize=(7, 5))

    df0 = df[df[TARGET] == 0]
    df1 = df[df[TARGET] == 1]

    plt.scatter(
        df0["precip_hourly_mm"],
        df0["elevation_m"],
        alpha=0.35,
        s=25,
        color="blue",
        label="No landslide (0)",
    )

    plt.scatter(
        df1["precip_hourly_mm"],
        df1["elevation_m"],
        alpha=0.9,
        s=70,
        color="orange",
        marker="x",
        label="Landslide (1)",
    )

    plt.xlabel("Hourly precipitation [mm]")
    plt.ylabel("Elevation [m]")
    plt.title("Hourly precipitation vs elevation")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_traceplots(idata):
    az.plot_trace(idata, var_names=["alpha", "beta"])
    plt.tight_layout()
    plt.show()


def plot_posterior_distributions(idata):
    az.plot_posterior(
        idata,
        var_names=["alpha", "beta"],
        hdi_prob=0.95,
    )
    plt.tight_layout()
    plt.show()


def plot_confusion_matrix(y_test, predictions, threshold=THRESHOLD):
    y_prob = predictions["p_landslide_mean"].values
    y_pred = (y_prob >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(5, 4))
    plt.imshow(cm)
    plt.colorbar(label="Count")

    plt.xticks([0, 1], ["Pred 0", "Pred 1"])
    plt.yticks([0, 1], ["True 0", "True 1"])

    for i in range(2):
        for j in range(2):
            plt.text(j, i, cm[i, j], ha="center", va="center")

    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.title(f"Confusion Matrix, threshold={threshold}")
    plt.tight_layout()
    plt.savefig("Confusion_matrix.pdf")
    plt.show()


def plot_roc_curve(y_test, predictions):
    y_prob = predictions["p_landslide_mean"].values
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"Bayesian model, AUC = {auc:.2f}")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random classifier")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.show()


def make_all_plots(df, idata, y_test, predictions):
    plot_training_data(df)
    plot_traceplots(idata)
    plot_posterior_distributions(idata)
    plot_confusion_matrix(y_test, predictions)
    plot_roc_curve(y_test, predictions)