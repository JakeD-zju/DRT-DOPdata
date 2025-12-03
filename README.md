# DRT-DOPdata
This project aims to achieve high-throughput EIS testing and DRT-DOP analysis for various electrochemical workstations such as Solartron workstation, Gamma workstation, especially CHI workstation. The project is based on hybdrt related work https://github.com/jdhuang-csm/hybrid-drt.

DRT-DOP requires the mittag-leffler package. hybrid-drt also requires the following packages:
· numpy
· matplotlib
· scipy
· pandas
· cvxopt
· scikit-learn
· galvani

The processed file will be saved in the selected folder starting with DRT_Fit_SResults_{filename}.

The processing will output a graphical interface displaying the DRT-DOP fitting results, Nyquist plot fitting results, and real part fitting residuals
