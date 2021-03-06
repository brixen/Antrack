
__author__ = 'Ivan'
import glob
import numpy as np
import os.path
import cPickle
import cv2
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import datetime
import os
import re

from DatasetEvaluation import Dataset,loadPickle,AllExperiments,Evaluator,savePickle


class EvaluatorAllExperiments(object):
    def __init__(self, dataset, listOfExperiments,names):

        self.dataset = dataset
        self.listOfExperiments = listOfExperiments

        r=re.compile("(.*\/)(.+)(.p)")

        namesProcessed=list()

        for n in names:

            print n
            m=r.match(n)


            namesProcessed.append(m.group(2))

        self.experimentNames= namesProcessed;

    @staticmethod
    def createPlotData(centerDistance, maxValue=50, n=100):


        x = np.linspace(0, maxValue, num=n);

        y = np.zeros(n)

        for idx in range(0, n):
            # find percentage of centerDistance<= x[idx

            y[idx] = len(np.nonzero(centerDistance <= x[idx])[0]) / (centerDistance.shape[0] * 1.0)

        return (x, y)





    def createHistogramPlot(self, plotMetricsDict, completeMetricDict, savefilename=''):

        # x_pr_input, y_pr_input, x_s_input, y_s_input

        precision = list()
        success = list()
        cm = plt.get_cmap('gist_rainbow')

        titleFontSize = 16;
        headerFontSize = 13;
        axisFontSize = 12;
        lineWidth = 1.8;

        legendSize = 9;
        names = list()
        plt.figure(figsize=(13, 9))

        evaluationTypes = ['default', 'SRE', 'TRE']

        trackerNames = self.experimentNames
        labelsFontSize = 11
        idx = 1

        import seaborn as sn

        for expName, index in zip(evaluationTypes, range(0, len(evaluationTypes))):

            x_pr = list()
            y_pr = list()

            x_s = list()
            y_s = list()

            p = list()
            s = list()
            for name in self.experimentNames:
                d = plotMetricsDict[name];

                x_pr.append(d[expName][0])
                y_pr.append(d[expName][1])
                x_s.append(d[expName][2])
                y_s.append(d[expName][3])

                p.append(np.round(d[expName][4], 3))
                s.append(np.round(d[expName][5], 3))

            plt.subplot(3, 2, idx)
            groups = np.arange(len(x_pr))


            # sort by a combination of the two metrics
            idx_success = [i[0] for i in sorted(enumerate([sum(x) for x in zip(p, s)]), key=lambda x: x[1])]

            successTrackerNames = [trackerNames[x] for x in idx_success]
            sorted_success = [s[x] for x in idx_success]

            rects = plt.barh(groups, sorted_success, align="center")
            # plt.yticks(groups, successTrackerNames)
            frame1 = plt.gca()
            frame1.axes.get_yaxis().set_ticks([])
            plt.xlim((0, 1))
            plt.grid(b=False)
            if idx == 1:
                plt.title("Success", fontsize=headerFontSize)

            for rect, name, pr in zip(rects, successTrackerNames, sorted_success):
                # Rectangle widths are already integer-valued but are floating
                # type, so it helps to remove the trailing decimal point and 0 by
                # converting width to int type
                width = int(rect.get_width())

                rankStr = name
                xloc = width  #
                clr = 'black'  # Black against white background
                align = 'left'

                valueStr = ' [' + str(pr) + ']'


                # Center the text vertically in the bar
                yloc = rect.get_y() + rect.get_height() / 2.0
                plt.text(xloc, yloc, rankStr, horizontalalignment=align,
                         verticalalignment='center', color=clr, fontsize=labelsFontSize)

                plt.text(xloc + rect.get_width(), yloc, valueStr, horizontalalignment=align,
                         verticalalignment='center', color=clr, fontsize=labelsFontSize + 2, weight='bold')

            idx = idx + 1

            plt.subplot(3, 2, idx)
            precisionTrackerNames = [trackerNames[x] for x in idx_success]
            sorted_precision = [p[x] for x in idx_success]

            rects = plt.barh(groups, sorted_precision, align="center")
            frame1 = plt.gca()
            frame1.axes.get_yaxis().set_ticks([])
            plt.xlim((0, 1))
            plt.grid(b=False)
            if idx == 2:
                plt.title("Precision", fontsize=headerFontSize)

            for rect, name, pr in zip(rects, precisionTrackerNames, sorted_precision):
                # Rectangle widths are already integer-valued but are floating
                # type, so it helps to remove the trailing decimal point and 0 by
                width = int(rect.get_width())

                rankStr = name
                xloc = width  #
                clr = 'black'  # Black against white background
                align = 'left'

                valueStr = ' [' + str(pr) + ']'


                # Center the text vertically in the bar
                yloc = rect.get_y() + rect.get_height() / 2.0
                plt.text(xloc, yloc, rankStr, horizontalalignment=align,
                         verticalalignment='center', color=clr, fontsize=labelsFontSize)

                plt.text(xloc + rect.get_width(), yloc, valueStr, horizontalalignment=align,
                         verticalalignment='center', color=clr, fontsize=labelsFontSize + 2, weight='bold')

            ax2 = plt.twinx()
            ax2.set_ylabel(evaluationTypes[index], color='black')
            frame1 = plt.gca()
            frame1.axes.get_yaxis().set_ticks([])
            plt.grid(b=False)
            idx = idx + 1
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        if savefilename == '':
            plt.show()
        else:
            plt.savefig(savefilename, dpi=1000)



    def evaluate(self, n=1000, successAndPrecisionPlotName='', histogramPlot=''):

        '''

        Evaluate the dataset

        :return: accuracy and precision
        '''

        listGT = self.dataset.data

        pr_x_list = list()
        pr_y_list = list()

        sc_x_list = list()
        sc_y_list = list();

        experimentNames = list()


        defaultExpList=list()
        sreExpList=list()
        treExpList=list()

        for listRun,name in zip(self.listOfExperiments,self.experimentNames):
            runs = listRun.data
            experimentNames.append(name)


            defaultExpList.append(runs['default'])
            sreExpList.append(runs['SRE'])
            treExpList.append(runs['TRE'])


        allExpList=list()
        allExpList.append(defaultExpList)
        allExpList.append(sreExpList)
        allExpList.append(treExpList)


        pr_x_all_list=list()
        pr_y_all_list=list()

        sc_x_all_list = list()
        sc_y_all_list = list()

        for exp in allExpList:    # experiment type
            # exp
            e=Evaluator(self.dataset,exp)

            pr_x_list = list()
            pr_y_list = list()

            sc_x_list = list()
            sc_y_list = list()


            measures_specific_list=list()
            for listRun in exp:   # different tracker runs
                (precision_x, precision_y, success_x, success_y) = e.evaluateSingleTracker(listRun, n)

                pr_x_list.append(precision_x)
                pr_y_list.append(precision_y)

                sc_x_list.append(success_x)
                sc_y_list.append(success_y)

            pr_x_all_list.append(pr_x_list)
            pr_y_all_list.append(pr_y_list)

            sc_x_all_list.append(sc_x_list)
            sc_y_all_list.append(sc_y_list)


        # REWRITE THIS FUNCTION: SUCCESS plots are not generated pro

        #self.createPlot(pr_x_all_list, pr_y_all_list, sc_x_all_list, sc_y_all_list, savefilename=successAndPrecisionPlotName)


        # get some real data and finish this plot
        #self.createHistogramPlot(pr_x_all_list, pr_y_all_list, sc_x_all_list, sc_y_all_list,self.experimentNames, savefilename=histogramPlot)


    def createPlot(self, plotMetricsDict, completeMetricDict, savefilename=''):

        cm = plt.get_cmap('gist_rainbow')
        NUM_COLORS = len(plotMetricsDict)

        titleFontSize = 16;
        headerFontSize = 14;
        axisFontSize = 13;
        lineWidth = 1.8;

        legendSize = 9;

        plt.figure(figsize=(13, 9))

        evaluationTypes = ['default', 'SRE', 'TRE']

        with plt.style.context('grayscale'):
            i = 2

            idx = 1




            for expName, index in zip(evaluationTypes, range(0, len(evaluationTypes))):

                x_pr = list()
                y_pr = list()

                x_s = list()
                y_s = list()

                p=list()
                s=list()
                for name in self.experimentNames:
                    d = plotMetricsDict[name];



                    x_pr.append(d[expName][0])
                    y_pr.append(d[expName][1])
                    x_s.append(d[expName][2])
                    y_s.append(d[expName][3])

                    p.append(np.round(d[expName][4],3))
                    s.append(np.round(d[expName][5],3))
                # x_pr = [z[expName][0] for z in plotMetricsDict.values()]
                # y_pr = [z[expName][1] for z in plotMetricsDict.values()]
                #
                # x_s = [z[expName][2] for z in plotMetricsDict.values()]
                # y_s = [z[expName][3] for z in plotMetricsDict.values()]

                handlesLegendPrecision = list()
                handlesLegendSuccess = list()

                # p = np.ma.round([z[expName][4] for z in plotMetricsDict.values()], 2)
                # s = np.ma.round([z[expName][5] for z in plotMetricsDict.values()], 2)

                for ii in range(0, len(self.experimentNames)):
                    color = cm(1. * ii / NUM_COLORS)
                    if idx == 1:
                        red_patch = mpatches.Patch(label=' [' + str(p[ii]) + '] ' + self.experimentNames[ii],
                                                   color=color)
                        # self.run.trackerLabel
                    else:
                        red_patch = mpatches.Patch(label=' [' + str(p[ii]) + ']',
                                                   color=color)
                    blue_path = mpatches.Patch(label=' [' + str(s[ii]) + ']',
                                               color=color)
                    handlesLegendPrecision.append(red_patch)
                    handlesLegendSuccess.append(blue_path)

                # plt.suptitle(expName, fontsize=titleFontSize)
                ax = plt.subplot(3, 2, idx)

                for i in range(0, len(self.experimentNames)):
                    ax.plot(x_s[i], y_s[i], linewidth=lineWidth, color=cm(1. * i / NUM_COLORS))

                # if idx == 1:
                #     plt.title('success', fontsize=headerFontSize)

                ax.set_ylim([0, 1])
                ax.set_xlim([0, 1])

                if idx == 5:
                    ax.set_xlabel('Overlap threshold', fontsize=axisFontSize)

                ax.set_ylabel('Success rate', fontsize=axisFontSize)

                idx = idx + 1
                ax.legend(handles=handlesLegendSuccess, prop={'size': legendSize})
                plt.grid(b=False)
                ax = plt.subplot(3, 2, idx)

                for i in range(0, len(self.experimentNames)):
                    ax.plot(x_pr[i], y_pr[i], linewidth=lineWidth, color=cm(1. * i / NUM_COLORS))
                # plt.plot(x_pr, y_pr, linewidth=lineWidth, color=cm(1. * i / NUM_COLORS))
                ax.set_ylim([0, 1])
                ax.set_xlim([-0.5, 51])

                if idx == 2:
                    plt.title("precision", fontsize=headerFontSize)
                plt.grid(b=False)

                if idx == 6:
                    plt.xlabel('Location error threshold', fontsize=axisFontSize)

                ax.set_ylabel('Precision', fontsize=axisFontSize)

                ax2 = plt.twinx()
                ax2.set_ylabel(evaluationTypes[index], color='black')
                ax2.grid(b=False)
                idx = idx + 1
                ax.legend(handles=handlesLegendPrecision, prop={'size': legendSize}, loc=2)

            #plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
            #plt.set_tight_layout(True)
        if savefilename == '':
            plt.show()
        else:
            plt.savefig(savefilename)



    def calculateMetricsAndSave(self,savePath,n=1000):
        completeMetricDict = dict()

        plotMetricsDict = dict()

        for run, experimentName in zip(self.listOfExperiments, self.experimentNames):

            fullP = 0
            fullS = 0

            ll = 0

            experimentDict = dict()

            for expName, experiment in run.data.iteritems():


                x_p_var = np.zeros(n)
                y_p_var = np.zeros(n)

                x_s_var = np.zeros(n)
                y_s_var = np.zeros(n)

                averageP = 0
                averageS = 0

                l = 0

                for videoData in experiment.data:

                    gt = [x for x in self.dataset.data if x[0] == videoData[0]][0]

                    for expRunIndex in range(0, len(videoData[1])):
                        (x_pr, y_pr, x_s, y_s) = Evaluator.evaluateSingleVideo(videoData, gt,
                                                                               experimentNumber=expRunIndex,
                                                                               n=n)

                        x_p_var =np.add(x_p_var, x_pr)
                        y_p_var = np.add(y_p_var,y_pr)

                        x_s_var = np.add(x_s_var,x_s)
                        y_s_var = np.add(y_s_var,y_s)

                        l = l + 1

                        (p1, s1) = Evaluator.getIntegralValues(x_pr, y_pr, x_s, y_s)

                        averageP = averageP + p1
                        averageS = averageS + s1

                        if expName != 'default':
                            fullP = fullP + p1
                            fullS = fullS + s1;
                            ll = ll + 1

                x_p_var = x_p_var / (float(l))
                y_p_var = y_p_var / (float(l))
                x_s_var = x_s_var / (float(l))
                y_s_var = y_s_var / (float(l))

                averageP = averageP / (float(l))
                averageS = averageS / (float(l))

                experimentDict[expName] = (x_p_var, y_p_var, x_s_var, y_s_var, averageP, averageS)

            fullP = fullP / (float(ll))
            fullS = fullS / (float(ll))

            completeMetricDict[experimentName] = (fullP, fullS)

            plotMetricsDict[experimentName] = experimentDict

            print experimentName
            print "===================="
            print "Precision: ", fullP
            print "Success: ", fullS

            for key, value in experimentDict.iteritems():
                print key
                print value[4], value[5]

            print "===================="

            e=Evaluated(plotMetricsDict[experimentName],completeMetricDict[experimentName],experimentName)

            e.save(savePath+"/"+experimentName+".p")

    def evaluate(self, n=1000, successAndPrecisionPlotName='', histogramPlot=''):

        '''

        Evaluate the dataset

        :return: accuracy and precision
        '''



        completeMetricDict=dict()

        plotMetricsDict=dict()

        for run,experimentName in zip(self.listOfExperiments,self.experimentNames):

            fullP=0
            fullS=0

            ll=0

            experimentDict=dict()

            for expName, experiment in run.data.iteritems():


                x_p_var=np.zeros((n,1))
                y_p_var= np.zeros((n, 1))

                x_s_var= np.zeros((n, 1))
                y_s_var= np.zeros((n, 1))


                averageP=0
                averageS=0


                l=0

                for videoData in experiment.data:

                    gt = [x for x in self.dataset.data if x[0] == videoData[0]][0]



                    for expRunIndex in range(0, len(videoData[1])):
                        (x_pr, y_pr, x_s, y_s) = Evaluator.evaluateSingleVideo(videoData, gt, experimentNumber=expRunIndex,
                                                                               n=n)

                        x_p_var= x_p_var+x_pr
                        y_p_var= y_p_var+y_pr

                        x_s_var=x_s_var+x_s
                        y_s_var=y_s_var+y_s


                        l=l+1

                        (p1,s1)=Evaluator.getIntegralValues(x_pr,y_pr,x_s,y_s)

                        averageP=averageP+p1
                        averageS=averageS+s1


                        if expName!='default':
                            fullP= fullP+p1
                            fullS=fullS+s1;
                            ll=ll+1


                x_p_var=x_p_var/(float(l))
                y_p_var = y_p_var / (float(l))
                x_s_var = x_s_var / (float(l))
                y_s_var = y_s_var / (float(l))

                averageP= averageP/(float(l))
                averageS=averageS/(float(l))

                experimentDict[expName]=(x_p_var,y_p_var,x_s_var,y_s_var,averageP,averageS)

            fullP= fullP/(float(ll))
            fullS = fullS / (float(ll))

            completeMetricDict[experimentName]=(fullP,fullS)

            plotMetricsDict[experimentName]=experimentDict


            print experimentName
            print "===================="
            print "Precision: ",fullP
            print "Success: ",fullS

            for key,value in experimentDict.iteritems():
                print key
                print value[4],value[5]

            print "===================="






        # runEvaluation is

        self.createPlot(plotMetricsDict,completeMetricDict,savefilename=successAndPrecisionPlotName)
        self.createHistogramPlot(plotMetricsDict, completeMetricDict, savefilename=histogramPlot)



    def evaluateFromSave(self,runs, successAndPrecisionPlotName='', histogramPlot=''):
        plotMetricsDict=dict()
        completeMetricDict=dict()

        for r in runs:
            plotMetricsDict[r.name]=r.plotMetricsDictEntry
            completeMetricDict[r.name]=r.completeMetricDictEntry

        self.createPlot(plotMetricsDict, completeMetricDict, savefilename=successAndPrecisionPlotName)

        print "Generating histogram plot..."
        self.createHistogramPlot(plotMetricsDict, completeMetricDict, savefilename=histogramPlot)

class Evaluated(object):
    """"""

    def __init__(self, plotMetricsDictEntry, completeMetricDictEntry,name):
        """Constructor for Evaluated"""

        self.plotMetricsDictEntry= plotMetricsDictEntry
        self.completeMetricDictEntry= completeMetricDictEntry
        self.name=name
    def save(self,savePath):

        savePickle(self,savePath)




def createSavedEvaluations(wildcard):
    wu2013results = "/Users/Ivan/Files/Results/Tracking/wu2013"
    wu2013GroundTruth = "/Users/Ivan/Files/Data/Tracking_benchmark"

    vot2014Results = "/Users/Ivan/Files/Results/Tracking/vot2014"
    vot2014GrounTruth = "/Users/Ivan/Files/Data/vot2014"

    datasetType = 'wu2013'


    dataset = Dataset(wu2013GroundTruth, datasetType)

    runsNames = glob.glob('./Runs/' + wildcard + '*.p')

    runs = list()
    #
    names = list()
    for runName in runsNames:
        run = loadPickle(runName)
        names.append(runName)
        print runName
        runs.append(run)


    evaluator = EvaluatorAllExperiments(dataset, runs, names)


    strSave = './Results/'

    evaluator.calculateMetricsAndSave(strSave)

if __name__ == "__main__":


    # if you want to evaluate and save evaluations ( do this first)


    wildcard = "p"
    createSavedEvaluations(wildcard);


    wu2013results = "/Users/Ivan/Files/Results/Tracking/wu2013"
    wu2013GroundTruth = "/Users/Ivan/Files/Data/Tracking_benchmark"

    vot2014Results = "/Users/Ivan/Files/Results/Tracking/vot2014"
    vot2014GrounTruth = "/Users/Ivan/Files/Data/vot2014"

    datasetType = 'wu2013'
    # Note: in wu2013 i

    # trackerLabel="STR+f_hog"

    # wildcard = sys.argv[1]

    dataset = Dataset(wu2013GroundTruth, datasetType)

    runsNames = glob.glob('./Results/' + wildcard + '*.p')

    #runsNames = ['SAMF', 'Kernelized_filter', 'fk_hist_int_f0', 'fk_hist_int_f1','TLD']
    runs = list()
    #
    names=list()
    for runName in runsNames:

        #runName= './Results/' + runName + '.p'
        run = loadPickle(runName)
        names.append(runName)
        print runName
        #run = run.data[experimentType]
        runs.append(run)

    # run=loadPickle('./Runs/TLD.p')
    # runs.append(run)
    # names.append('./Runs/TLD.p')


    evaluator = EvaluatorAllExperiments(dataset, list(), names)

    saveFigureToFolder = '/Users/Ivan/Code/personal-website/Projects/Object_aware_tracking/images/multiScale/'
    #saveFormat = ['png', 'pdf']
    saveFormat=['pdf']
    successAndPrecision = 'SuccessAndPrecision_wu2013'
    histograms = 'histogram_wu2013'



    # for i in saveFormat:
    #     evaluator.evaluateFromSave(runs,successAndPrecisionPlotName=saveFigureToFolder+successAndPrecision+'.'+
    #                                                    i,histogramPlot=saveFigureToFolder+histograms+'.'+
    #                                                                                i)

    evaluator.evaluateFromSave(runs)
