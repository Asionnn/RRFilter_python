import os
from tkinter import *
from tkinter import filedialog

import heartpy as hp
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hrvanalysis import get_time_domain_features
from hrvanalysis import remove_outliers, remove_ectopic_beats, interpolate_nan_values
from scipy.signal import butter, lfilter


class RRWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master


file_name = ""
dst = ""
parent_dir = '.'


# set up window
window = Tk()
app = RRWindow(window)
window.geometry("800x600")
window.title("RRFilter")
window.configure(background='white')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y


def reject_outliers(data):
    np_array = np.array(data)
    mean = np.mean(np_array, axis=0)
    sd = np.std(np_array, axis=0)
    final_list = list()

    for i in range(len(data)):
        if data[i] > (mean - 2 * sd):
            final_list.append(data[i])

    indexes = []
    for j in range(len(final_list)):
        if not final_list[j] < (mean + 2 * sd):
            indexes.append(j)

    for k in range(len(indexes)):
        final_list[indexes[k]] = -1

    complete_list = []
    for pos in range(len(final_list)):
        if final_list[pos] != -1:
            complete_list.append(final_list[pos])

    '''
    final_list = [x for x in data if (x > mean - 2 * sd)]
    final_list = [x for x in final_list if (x < mean + 2 * sd)]
    '''

    return complete_list


def import_btn_press():
    global parent_dir
    global file_name
    window.filename = filedialog.askopenfilename(initialdir=parent_dir, title="Select file", filetypes=(("Data files", "*.data"), ("all files", "*.*")))
    parent_dir = window.filename
    file_name = os.path.basename(window.filename)
    fname = Label(window, text="File Name: " + file_name)
    lfont = ('arial', 20, 'bold')
    fname.config(font=lfont, background="white")
    fname.place(x=150, y=150, height=30, width=500)


def filter_btn_press():
    global file_name
    global dst
    if window.filename and dst:
        data = pd.read_csv(
            window.filename,
            skiprows=[0, 1, 2, 3, 4, 5, 6, 7], sep='\t')
        del data[" "]
        del data[' .1']
        del data[' Filtered Current ']

        filtered = butter_bandpass_filter(data[" Current "], 0.4, 2, 500, order=3)

        # rejects outliers, passed through 3 times
        np_removed_outliers = reject_outliers(filtered)
        np_removed_outliers = reject_outliers(np_removed_outliers)
        np_removed_outliers = reject_outliers(np_removed_outliers)

        # set up RR data
        np_removed_outliers = np.array(np_removed_outliers)
        working_data, measures = hp.process(np_removed_outliers, 500, report_time=True, freq_method="fft")

        # filter RR outliers
        rr_intervals_list = working_data['RR_list']
        rr_removed_outliers = remove_outliers(rr_intervals=rr_intervals_list, low_rri=600, high_rri=1200, verbose=False)
        rr_interpolated = interpolate_nan_values(rr_intervals=rr_removed_outliers, interpolation_method="linear")
        nn_intervals = remove_ectopic_beats(rr_intervals=rr_interpolated, method="malik")
        nn_interpolated = interpolate_nan_values(rr_intervals=nn_intervals)

        # removes all NaN
        nn_interpolated = [x for x in nn_interpolated if not math.isnan(x)]

        # convert all to ints
        nn_interpolated = [int(x) for x in nn_interpolated]

        # set correct bpm
        RR_plot = hp.plotter(working_data, measures, show=False)
        RR_plot.title("Initial HR Data Before Additional Filtering")
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(15, 8)
        legend = RR_plot.legend()
        time_domain_features = get_time_domain_features(nn_interpolated)
        legend.get_texts()[1].set_text("HR: ~" + str(int(time_domain_features['mean_hr'])) + " bpm")

        dst_file_path = dst + "/RR_" + file_name.replace(".data", ".txt")

        print(dst_file_path)
        if os.path.exists(dst_file_path):
            os.remove(dst_file_path)

        f = open(dst_file_path, "a")

        # write to file
        for x in range(len(nn_interpolated)):
            f.write(str(int(nn_interpolated[x])) + "\n")
        f.flush()
        os.fsync(f.fileno())
        f.close()

        RR_plot.show()

        del data

    else:
        print("error check here")


def dst_btn_press():
    global dst
    dst = filedialog.askdirectory()


if __name__ == "__main__":
    import_btn = Button(window, text="Import", command=import_btn_press)
    import_btn.place(x=150, y=0, height=50, width=100)

    filter_btn = Button(window, text="Filter", command=filter_btn_press)
    filter_btn.place(x=350, y=0, height=50, width=100)

    dst_btn = Button(window, text="Destination", command=dst_btn_press)
    dst_btn.place(x=550, y=0, height=50, width=100)

    window.mainloop()