from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from ml.features.preprocessing import scale_data

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_extra_tree(stock_data):

    X = stock_data.drop(['Target'], axis=1)
    train_x, test_x, train_y, test_y = train_test_split(X, stock_data['Target'], test_size=0.20, random_state=42)
    #train_x, test_x = scale_data(train_x, test_x)

    etc = ExtraTreesClassifier(n_estimators=2000, random_state=42)
    etc.fit(train_x, train_y)
    y_pred = etc.predict(test_x)
    accuracy = accuracy_score(test_y, y_pred)
    print(f"Modellname: {etc.__class__.__name__}")
    print(f"Genauigkeit: {accuracy}")

    # Confusion Matrix
    plot_confusion_matrix(test_y, y_pred)
    return etc, accuracy


def plot_confusion_matrix(test_y, y_pred):
    cm = confusion_matrix(test_y, y_pred)
    plt.figure(figsize=(10, 8))
    heatmap = sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Konfusionsmatrix', pad=20)
    plt.ylabel('Tatsächliche Werte', labelpad=10)
    plt.xlabel('Vorhergesagte Werte', labelpad=10)
    plt.show()
    plt.savefig('konfusionsmatrix.png')