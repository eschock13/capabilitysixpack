import matplotlib.pyplot as plt
from statistics import *
from matplotlib.patches import Rectangle
import probscale
from math import *
from scipy import stats
import numpy as np

class Plot:
    def __init__(self, data, lsl, usl, specnum=0, sixpack=False):
        self.specNum = specnum
        self.data = data
        self.usl = usl
        self.lsl = lsl
        self.mR_data = [abs(self.data[x] - self.data[x-1]) for x in range(1, len(self.data))]
        self.within = mean(self.mR_data) / 1.128
        self.pp = (self.usl - self.lsl) / (6 * stdev(self.data))
        self.ppk = min((mean(self.data) - self.lsl) / (3 * stdev(self.data)), (self.usl - mean(self.data)) / (3 * stdev(self.data)))
        self.cp = (self.usl - self.lsl) / (6 * self.within)
        self.cpk = min((mean(self.data) - self.lsl) / (3 * self.within), (self.usl - mean(self.data)) / (3 * self.within))
        self.fig = plt.figure(constrained_layout=True, figsize=(13,10))
        self.ax = self.fig.add_gridspec()
        self.numPlots = 0
        self.plotList = []
        if sixpack is True:
            plt.suptitle('Process Capability Sixpack Report For ' + str(int(self.specNum)) + ' ' + str(lsl) + '-' + str(usl), fontsize=25)

    def I_Chart(self, row, col):
        ucl = (mean(self.data)+(2.66*mean(self.mR_data)))
        lcl = (mean(self.data)-(2.66*mean(self.mR_data)))
        hlist = []
        plist = []
        c = 1
        for i in self.data:
            if lcl <= i <= ucl:
                c +=1
            else:
                hlist.append(i)
                plist.append(c)
                c += 1
        ax1 = self.fig.add_subplot(self.ax[row, col])
        ax1.plot(range(1, len(self.data) + 1), self.data, linestyle='-', marker='o', color='blue')
        ax1.plot(plist, hlist, 'rs')
        ax1.set_xlim(0, len(self.data) + 1)
        ax1.axhline(mean(self.data), color = 'green', xmin=1 / (len(self.data) + 2), xmax = 1 / (len(self.data) + 2) * (len(self.data) + 1))
        ax1.axhline(ucl, color='red', xmin=1 / (len(self.data) + 2), xmax = 1 / (len(self.data) + 2) * (len(self.data) + 1))
        ax1.axhline(lcl, color='red', xmin=1 / (len(self.data) + 2), xmax = 1 / (len(self.data) + 2) * (len(self.data) + 1))
        ax1.set_title('I Chart')
        ax1.set_ylabel('Individual Value')
        yticks = list(ax1.set_ylim())
        yticks.append(sum(yticks) / 2)
        rounded_yticks = [round(num, 2) for num in yticks]
        ax1.set_yticks(rounded_yticks)
        ax1.set_xticks(range(1, len(self.data) + 1, round((len(self.data) + 1) / 11)))
        ax1.annotate(("UCL = " + str(round(ucl, 5))), xy=(len(self.data), ucl), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate(("X = " + str(round(mean(self.data), 5))), xy=(len(self.data), mean(self.data)), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate(("LCL = " + str(round(lcl, 5))), xy=(len(self.data), lcl), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate("_", xy=(len(self.data), mean(self.data)), xycoords='data',
                    xytext=(15,5), textcoords='offset points',
                    ha = 'left', va='bottom')

    def Capability_Histogram(self, row, col):
        spacer = (self.usl - self.lsl) / 100
        utick = self.usl + spacer
        ltick = self.lsl - spacer
        tick = self.lsl - spacer
        dataRange = utick - ltick
        dataStep = round(dataRange / 8, 3)
        tickNums = []
        tickNames = []
        for i in range(1, 9):
            tickNums.append(round(tick, 3))
            tickNames.append(str(round(tick, 3)))
            tick += dataStep
        #define lower and upper bounds for x-axis
        lower_bound = min(self.data) - (0.4 * min(self.data))
        upper_bound = max(self.data) + (0.4 * max(self.data))
        #create range of x-values from lower to upper bound in increments of .001
        x_data = np.arange(lower_bound,upper_bound, 0.001)
        #create range of y-values that correspond to normal pdf with mean1=0 and sd=1 
        y_data = stats.norm.pdf(x_data, mean(self.data), stdev(self.data))
        y1_data = stats.norm.pdf(x_data ,mean(self.data), self.within)

        # Plot histogram for data along with probability density functions and specification limits
        ax1 = self.fig.add_subplot(self.ax[row, col])
        bins, _, _ = ax1.hist(self.data, color="lightgrey", edgecolor="black", density=True)
        ax1.axvline(self.lsl, linestyle="--", color="red")
        ax1.grid()
        ax1.axvline(self.usl, linestyle="--", color="red")
        ax1.plot(x_data, y_data, color='red')
        ax1.plot(x_data, y1_data, color='black', linestyle="--")
        ax1.set_xlim(ltick,utick)
        ax1.set_title('Capability Histogram')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_xticks(tickNums)
        ax1.set_xticklabels(tickNames)
        yticks = [0, max(bins)]
        yticks.append(sum(yticks) / 2)
        ax1.set_yticks(yticks)
        ax1.set_yticklabels([])
        ax1.annotate('LSL', xy=(self.lsl, ax1.set_ylim()[1]), xycoords='data', 
                    xytext=(0, 1.5), textcoords='offset points', 
                    ha='center', color='red')
        ax1.annotate('USL', xy=(self.usl, ax1.set_ylim()[1]), xycoords='data', 
                    xytext=(0, 1.5), textcoords='offset points', 
                    ha='center', color='red')
        ax1.annotate('', xy=(1.01, 0.85), xycoords='axes fraction',
                    xytext=(40,0), textcoords='offset points',
                    ha = 'left', va='center',
                    arrowprops=dict(arrowstyle="-", color='red'))
        ax1.annotate('', xy=(1.075, 0.75), xycoords='axes fraction',
                    xytext=(18,0), textcoords='offset points',
                    ha = 'left', va='center',
                    arrowprops=dict(arrowstyle="-", color='black'))
        ax1.annotate('', xy=(1.01, 0.75), xycoords='axes fraction',
                    xytext=(18,0), textcoords='offset points',
                    ha = 'left', va='center',
                    arrowprops=dict(arrowstyle="-", color='black'))
        ax1.annotate('Specifications', xy=(1.255, 0.45), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'right', va='center')
        ax1.annotate('LSL', xy=(1.05, 0.35), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate('USL', xy=(1.05, 0.25), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate(str(self.lsl), xy=(1.255, 0.35), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'right', va='center')
        ax1.annotate(str(self.usl), xy=(1.255, 0.25), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'right', va='center')
        ax1.annotate('Overall', xy=(1.255, 0.85), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'right', va='center')
        ax1.annotate('Within', xy=(1.255, 0.75), xycoords='axes fraction',
                    xytext=(0,0), textcoords='offset points',
                    ha = 'right', va='center')

    def Moving_Range(self, row, col):
        ucl = 3.267 * mean(self.mR_data)
        lcl = 0
        hlist = []
        plist = []
        c = 1
        for i in self.mR_data:
            if lcl <= i <= ucl:
                c += 1
            else:
                hlist.append(i)
                plist.append(c)
                c += 1

        #Plots the Data From Above
        ax1 = self.fig.add_subplot(self.ax[row, col])
        ax1.plot(range(1, len(self.mR_data) + 1), self.mR_data, linestyle='-', marker='o', color='blue')
        ax1.plot(plist, hlist, 'rs')
        ax1.axhline(mean(self.mR_data), color='green', xmin=1 / (len(self.mR_data) + 2), xmax = 1 / (len(self.mR_data) + 2) * (len(self.mR_data) + 1))
        ax1.axhline(ucl, color='red', xmin=1 / (len(self.mR_data) + 2), xmax = 1 / (len(self.mR_data) + 2) * (len(self.mR_data) + 1))
        ax1.axhline(lcl, color='red', xmin=1 / (len(self.mR_data) + 2), xmax = 1 / (len(self.mR_data) + 2) * (len(self.mR_data) + 1))
        ax1.set_title('Moving Range Chart')
        ax1.set_ylabel('Moving Range')
        ax1.set_xlim(0, len(self.mR_data) + 1)
        yticks = list(ax1.set_ylim())
        ytickStep = max(yticks) / 3
        ax1.set_yticks([round(0, 2), round(ytickStep, 2), round(2 * ytickStep, 2)])
        ax1.set_xticks(range(1, len(self.data) + 1, round((len(self.data) + 1) / 11)))
        #LEGEND
        ax1.annotate(("UCL = " + str(round(ucl, 5))), xy=(len(self.data), ucl), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate(("MR = " + str(round(mean(self.mR_data), 5))), xy=(len(self.data), mean(self.mR_data)), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate(("LCL = " + str(round(lcl, 5))), xy=(len(self.data), lcl), xycoords='data',
                    xytext=(15,0), textcoords='offset points',
                    ha = 'left', va='center')
        ax1.annotate("__", xy=(len(self.data), mean(self.mR_data)), xycoords='data',
                    xytext=(15,5), textcoords='offset points',
                    ha = 'left', va='bottom')

    def Normal_Probability_Plot(self, row, col):
        n = len(self.data)
        AD = round(stats.anderson(self.data)[0], 3)
        AD1 = AD * (1 + (0.75/n) + (2.25/(n**2)))
        if AD1 >= 0.6:
            p = exp(1.2937 - (5.709 * AD1) + (0.0186 * AD1**2))
        elif 0.34 < AD1 < 0.6:
            p = exp(0.9177 - (4.279 * AD1) - (1.38 * AD1**2))
        elif 0.2 < AD1 < .34:
            p = 1 - exp(-8.318 + (42.796 * AD1) - (59.938 * AD1**2))
        elif AD1 >= 0.2:
            p = 1 - exp(-13.536 + (101.14 * AD1) - (223.73 * AD1**2))

        if p < 0.005:
            pVal = "P: < 0.005"
        else:
            pVal = "P: " + str(round(p, 3))
        adVal = "AD: " + str(AD)
        printVal = adVal + ", " + pVal

        #Sets the confidence lines for the chart
        percentLine = np.array([0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 91, 92, 93, 94,
        95, 96, 97, 98, 99, 99.9])
        #Used for the loop to create the middle line data
        percentLineForLoop = np.array([0.001, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 
        0.70, 0.80, 0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999])

        middleLineData = []
        lowLineData = []
        upLineData = []
        for i in range(0, len(percentLineForLoop)):
            test = stats.norm.ppf(percentLineForLoop[i], loc=mean(self.data), scale=stdev(self.data))
            middleLineData.append(test)
        #THESE ARRAYS ARE THE POINTS FOR THE CONFIDENCE INTERVAL LINES
        lowPercentLine = np.array([0.1, 6, 9, 95, 96, 97, 98, 99, 99.9])
        highPercentLine = np.array([0.1, 1, 2, 5, 91, 94, 99.9])
        #ARRAYS FOR THE LOOP TO GRAB THE VALUES FROM THE MIDDLELINEDATA ARRAY
        loopPercentLinesLow = np.array([0.1, 3, 5, 90, 92, 93, 95, 97, 99.9])
        loopPercentLinesHigh = np.array([0.1, 3, 5, 10, 95, 97, 99.9])
        #CREATES THE 0.1% and 99.9% VALUES FOR THE LOWLINEDATA AND UPLINEDATA ARRAYS
        LowValInt = stats.norm.interval(alpha=0.91, loc=middleLineData[0], scale=stats.sem(middleLineData))
        HighValInt = stats.norm.interval(alpha=0.91, loc=middleLineData[len(middleLineData)-1], scale=stats.sem(middleLineData))
        lowLineData.append(LowValInt[0])
        upLineData.append(LowValInt[1])
        xx = 0
        yy = 0
        for i in range(0, len(percentLine)):
            if loopPercentLinesLow[xx] == 0.1:
                xx += 1
            elif loopPercentLinesLow[xx] == percentLine[i]:
                lowLineData.append(middleLineData[i])
                xx += 1
            elif loopPercentLinesLow[xx] == 99.9:
                break
        
        for i in range(0, len(percentLine)):
            if loopPercentLinesHigh[yy] == 0.1:
                yy += 1
            elif loopPercentLinesHigh[yy] == percentLine[i]:
                upLineData.append(middleLineData[i])
                yy += 1
            elif loopPercentLinesHigh[yy] == 99.9:
                break
        lowLineData.append(HighValInt[0])
        upLineData.append(HighValInt[1])

        #Plotting

        ax1 = self.fig.add_subplot(self.ax[row, col])
        ax1.grid()
        ax1.set_title("Normal Prob Plot", pad=15)
        ax1.annotate(printVal, xy = (0.5,1.01), xytext = (0,0), xycoords = 'axes fraction', textcoords = 'offset points', ha='center')
        probscale.probplot(self.data, probax='y', pp_kws={"postype": 'normal'})
        #xhat, yhat = mLine()
        #ax1.plot(xhat, yhat, color='red')
        #ax1.set_yticks([0.1, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 99.9])
        ax1.set_yticks([0.1, 1, 10, 50, 90, 99, 99.9])
        ax1.set_yticklabels([])
        #ax1.set_xlim(min(data) * 0.9998, max(data) * 1.0006)
        ax1.plot(middleLineData, percentLine, color='red', alpha=0.7)
        ax1.plot(lowLineData, lowPercentLine, color='red', alpha=0.7)
        ax1.plot(upLineData, highPercentLine, color='red', alpha=0.7)

    def Last_Observations(self, row, col):
        last_data = self.data[-25:]
        x_data = list(range((len(self.data) - 24), len(self.data) + 1))

        #PLOTTING
        ax1 = self.fig.add_subplot(self.ax[row, col])
        ax1.scatter(x_data, last_data)
        yticks = list(ax1.set_ylim())
        yticks.append(sum(yticks) / 2)
        rounded_yticks = [round(num, 3) for num in yticks]
        ax1.set_title("Last 25 Observations")
        ax1.axhline(mean(self.data), linestyle="--", color="lightgrey")
        ax1.set_ylabel("Value")
        ax1.set_xlabel("Observation")
        ax1.set_yticks(rounded_yticks)
        ax1.set_xticks(range(len(self.data) - 20, len(self.data) + 1, 5))
        
    def Capability_Plot(self, row, col):
        stdev3plusO = mean(self.data) + (3 * stdev(self.data))
        stdev3minusO = mean(self.data) - (3 * stdev(self.data))
        overall_p1 = [stdev3minusO, 0.5]
        overall_p2 = [stdev3plusO, 0.5]
        overall_x = [overall_p1[0], overall_p2[0]]
        overall_y = [overall_p1[1], overall_p2[1]]
        stdev3plusW = mean(self.data) + (3 * self.within)
        stdev3minusW = mean(self.data) - (3 * self.within)
        within_p1 = [stdev3minusW, 0.5]
        within_p2 = [stdev3plusW, 0.5]
        within_x = [within_p1[0], within_p2[0]]
        within_y = [within_p1[1], within_p2[1]]

        #PLOTTING
        #Creates Rectangles for the data to be placed in
        ax1 = self.fig.add_subplot(self.ax[row, col])
        def __rectangles():
            ax1.add_patch(Rectangle((0,0), 500, 690, fc="white", ec="black"))
            ax1.add_patch(Rectangle((0,0), 500, 630, fc="white", ec="black"))
            ax1.add_patch(Rectangle((0,0), 500, 480, fc="white", ec="black"))
            ax1.add_patch(Rectangle((0,0), 500, 420, fc="white", ec="black"))
            ax1.add_patch(Rectangle((0,0), 500, 280, fc="white", ec="black"))
            ax1.add_patch(Rectangle((0,0), 500, 220, fc="white", ec="black"))
            # ax1.add_patch(Rectangle((-420, 340), 400, 350, fc="white", ec="black"))
            # ax1.add_patch(Rectangle((520, 300), 400, 390, fc="white", ec="black"))
        __rectangles()
        #Formats the plot
        def __formating():
            ax1.set_title('Capability Plot')
            ax1.text(250, 650, 'Overall', fontsize=6, horizontalalignment='center', verticalalignment='center')
            ax1.text(250, 440, 'Within', fontsize=6, horizontalalignment='center', verticalalignment='center')
            ax1.text(250, 240, 'Specs', fontsize=6, horizontalalignment='center', verticalalignment='center')
            ax1.axis('scaled')
        __formating()
        #Sets the Within Specs Outside the graph
        def __withinLabel():
            ax1.text(-220, 635, 'Within', fontsize=9, horizontalalignment='center')
            ax1.text(-390, 565, 'StDev', fontsize=7)
            ax1.text(-220, 565, str(round(self.within, 6)), fontsize=7)
            ax1.text(-390, 510, 'Cp', fontsize=7)
            ax1.text(-220, 510, str(round(self.cp, 2)), fontsize=7)
            ax1.text(-390, 450, 'Cpk', fontsize=7)
            ax1.text(-220, 450, str(round(self.cpk, 2)), fontsize=7)
            ax1.text(-390, 390, 'PPM', fontsize=7)
            ax1.text(-220, 390, '0.00', fontsize=7)
        __withinLabel()
        #Sets the Overall Specs Outside the graph
        def __overallLabel():
            ax1.text(710, 635, 'Overall', fontsize=9, horizontalalignment='center')
            ax1.text(540, 565, 'StDev', fontsize=7)
            ax1.text(680, 565, str(round(stdev(self.data), 6)), fontsize=7)
            ax1.text(540, 510, 'Pp', fontsize=7)
            ax1.text(680, 510, str(round(self.pp, 2)), fontsize=7)
            ax1.text(540, 450, 'Ppk', fontsize=7)
            ax1.text(680, 450, str(round(self.ppk, 2)), fontsize=7)
            ax1.text(540, 390, 'Cpm', fontsize=7)
            ax1.text(680, 390, '*', fontsize=7)
            ax1.text(540, 330, 'PPM', fontsize=7)
            ax1.text(680, 330, '0.00', fontsize=7)
        __overallLabel()
        #Creates the new plot and overall capability line
        def __overallLine():
            overallAxis = ax1.inset_axes([90, 530, 350, 80], transform = ax1.transData)
            overallAxis.set_xlim([self.lsl, self.usl])
            overallAxis.plot(overall_x, overall_y, color="red", markersize=7, linewidth=1)
            overallAxis.plot(stdev3minusO, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            overallAxis.plot(mean(self.data), 0.5, color="red", marker="+", markersize=7, linewidth=5)
            overallAxis.plot(stdev3plusO, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            overallAxis.axis('off')
        __overallLine()
        #Creates the new plot and within capability line
        def __withinLine():
            withinAxis = ax1.inset_axes([90, 320, 350, 80], transform = ax1.transData)
            withinAxis.set_xlim([self.lsl, self.usl])
            withinAxis.plot(within_x, within_y, color="red", markersize=7, linewidth=1)
            withinAxis.plot(stdev3minusW, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            withinAxis.plot(mean(self.data), 0.5, color="red", marker="+", markersize=7, linewidth=5)
            withinAxis.plot(stdev3plusW, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            withinAxis.axis('off')
        __withinLine()
        #Creates the new plot and spec capability line
        def __specLine():
            point5 = [self.lsl, 0.5]
            point6 = [self.usl, 0.5]
            x_values3 = [point5[0], point6[0]]
            y_values3 = [point5[1], point6[1]]
            specAxis = ax1.inset_axes([30, 70, 440, 80], transform = ax1.transData)
            specAxis.set_xlim([(self.lsl - (2 * stdev(self.data))),(self.usl + (2 * stdev(self.data)))])
            specAxis.plot(x_values3, y_values3, color="blue", markersize=7, linewidth=1)
            specAxis.plot(self.lsl, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            specAxis.plot(self.usl, 0.5, color="red", marker="+", markersize=7, linewidth=5)
            specAxis.axis('off')
        __specLine()
        #Makes all of the axes invisible
        ax1.axis('off')

    def add_plot(self, plotType):
        self.plotList.append(plotType)

    def update_gridspec(self):
        numPlots = self.numPlots
        if numPlots == 1:
            self.ax = self.fig.add_gridspec(nrows=1,ncols=1)
        elif numPlots == 2:
            self.ax = self.fig.add_gridspec(nrows=1, ncols=2)
        elif numPlots == 3:
            self.ax = self.fig.add_gridspec(nrows=2, ncols=2)
        elif numPlots == 4:
            self.ax = self.fig.add_gridspec(nrows=2, ncols=2)
        elif numPlots == 5:
            self.ax = self.fig.add_gridspec(nrows=3, ncols=2)
        elif numPlots == 6:
            self.ax = self.fig.add_gridspec(nrows=3, ncols=2)
        else:
            return False

    def create_plot(self):
        row = 0
        col = 0
        for p in self.plotList:
            if col > 1:
                col = 0
                row += 1
            if p == 'I_Chart':
                self.I_Chart(row, col)
            elif p == 'Capability Histogram':
                self.Capability_Histogram(row, col)
            elif p == 'Moving Range Chart':
                self.Moving_Range(row, col)
            elif p == 'Normal Probability Plot':
                self.Normal_Probability_Plot(row, col)
            elif p == 'Last 25 Observations':
                self.Last_Observations(row, col)
            elif p == 'Capability Plot':
                self.Capability_Plot(row, col)
            col += 1

    def show(self):
        self.numPlots = len(self.plotList)
        if self.numPlots <= 0:
            return 'You Must Select At Least One Plot!'
        else:
            self.update_gridspec()
            self.create_plot()
            plt.show()
