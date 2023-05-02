from csv import reader
import matplotlib.pyplot as plt
from numpy import array


class Iris:
    def __init__(self):
        self.data_file = reader(open('iris.txt'), delimiter="\t")
        self.data = [linha for linha in self.data_file]
        self.setosa = [linha for linha in self.data if 'setosa' in linha[-1]]
        self.versicolor = [linha for linha in self.data if 'versicolor' in linha[-1]]
        self.virginica = [linha for linha in self.data if 'virginica' in linha[-1]]
        self.zdata = list(zip(*self.data))
        self.zset = list(zip(*self.setosa))
        self.zver = list(zip(*self.versicolor))
        self.zvir = list(zip(*self.virginica))
        print(self.data)

    def plot(self, x=0, y=1):
        plt.scatter(self.zset[x], self.zset[y], color='red')
        plt.scatter(self.zver[x], self.zver[y], color='blue')
        plt.scatter(self.zvir[x], self.zvir[y], color='green')

        plt.show()

    def make_skl_dataset(self):
        target_names = list("setosa versicolor virginica".split())
        skl_dataset = dict(
            data=array([[float(ft) for ft in feature[1:-1]] for feature in self.data]),
            target_names=array(target_names),
            target=array([target_names.index(feature[-1][1:-1]) for feature in self.data]),
            dtype='<U10'
        )
        from sklearn.naive_bayes import GaussianNB
        from sklearn.datasets import load_iris
        ids = load_iris()
        print(ids)

        clf = GaussianNB()
        clf.fit(skl_dataset["data"], skl_dataset["target"])
        print(clf.predict([[6.7, 3. , 5.2, 2.3]]))
        print(clf.predict_proba([[6.7, 3., 5.2, 2.3]]))
        return skl_dataset


if __name__ == '__main__':
    Iris().plot(4, 2)
    # print(Iris().make_skl_dataset())
