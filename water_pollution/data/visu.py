import matplotlib.pyplot as plt
import water_pollution.data.preproc as pp

param_labels = pp.PARAM_LABELS


def plot_params(df, param_labels=param_labels):
    """Plots all the params of the df
    Takes the dict with param_id:label correspondance"""

    with plt.style.context('fivethirtyeight'):

        for col in df.columns :
            plt.figure(figsize=(12,5))
            plt.plot(df.index,df[col])
            plt.title(param_labels[int(col)])
            plt.show()

        plt.show()
