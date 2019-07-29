# RRFilter_python

# Python Version Used
* 3.7

# Important Python libraries used
* [Heartpy](https://pypi.org/project/heartpy/)
* [hrvanalysis](https://pypi.org/project/hrv-analysis/)

# Implementation
* A .data file containting nanosensor data is imported and extracted
* The data is passed through a butter-bandpass filter with sampling rate at 500, lowcut at 0.4 hz, highcut at 2 hz, and order at 3
* The data is passed through an 3 times outlier rejection formula from this [source](https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html)
* The data is passed into Heartpy, which calculates the RR intervals
* The intervals data are passed through the [methods defined in hrvanalysis](https://robinchampseix.github.io/hrvanalysis/hrvanalysis.html#module-hrvanalysis.preprocessing)
* Finally, the filtered intervals are written to a user defined location.

# Questions?
* contact me at li2718@purdue.edu if you have any questions
