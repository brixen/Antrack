__author__ = 'Ivan'
import glob
import numpy as np
import os.path
import cPickle
import cv2

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import datetime
import os

import seaborn as sns

class Dataset(object):


    def __init__(self,path_groundTruth,datasetType):
        '''

        :param path_groundTruth:
        :param datasetType:
        :return:
        '''
        self.path_gt=path_groundTruth

        self.datasetType=datasetType

        self.loadGroundTruth()

    def loadGroundTruth(self):


        videos=[f for f in os.listdir(self.path_gt) if not f.startswith('.')]

        # list videos

        l=list()

        listDicts=list()

        for vid in videos:
            d = dict()
            vidPath= self.path_gt + "/" + vid
            boxes=self.loadOneGroundTruth(vidPath)

            images=self.loadImages(vidPath)
            l.append((vid,boxes)) # <== This should be deprecated

            d["name"]=vid;
            d["boxes"]=boxes;
            d["images"]=images;
            listDicts.append(d);

        self.data=l;
        self.dictData=listDicts;

    def loadImages(self,path):

        if self.datasetType=='vot2014':
            format='jpg'
        elif self.datasetType=='wu2013':
            format='jpg'

            path=path+"/img/";

            images=glob.glob(path+"*."+format);
        else:
            print "Dataset not recognized"

        return  images;

    def loadOneGroundTruth(self,path):


        if self.datasetType=='vot2014':

            gt=np.genfromtxt(path+"/groundtruth.txt",delimiter=',')

            print "VOT 2014 need rework"
            return gt

        elif self.datasetType=='wu2013':

            gt=np.genfromtxt(path+"/groundtruth_rect.txt",delimiter=',')

            #print gt.max()
            if np.isnan(np.min(gt)):

                gt=np.genfromtxt(path+"/groundtruth_rect.txt",)


            return gt;
        else:

            print "Dataset not recognized"

class Experiment(object):


    def __init__(self,path_current, datasetType, tracker_label):

        self.path_results=path_current
        self.trackerLabel=tracker_label

        self.datasetType=datasetType


    def loadResults(self):

        '''

        Load ground truth annotations. Note the format of the annotations:

        -   top left corner width height

        :return: saves results in a list of the form : (sequenceName, matrix)
        '''

        # list all the files
        resultFilesNames=glob.glob(self.path_results+"/*.dat")


        f=open(self.path_results+"/tracker_info.txt",'r')

        trackerInformation=f.read();

        self.trackerInformation=trackerInformation

        # get rid of absolute path and then delete extension

        l=list()

        for fileNames in resultFilesNames:

            sequenceName=os.path.splitext(os.path.basename(fileNames))[0]

            boxes=np.loadtxt(fileNames,delimiter=',')

            l.append((sequenceName,boxes))


        self.data=l;

        self.time=datetime.datetime.now()


    def __str__(self):

        s="Results on "+self.datasetType +" dataset \n"
        s=s+"Time: "+str(self.time)+"\n\n"
        s=s+"Tracker information: \n\n"
        s=s+self.trackerInformation

        return s


    def save(self,saveTo):


        cPickle.dump(self,open(saveTo,'w'))



def loadPickle(path):

    return cPickle.loads(open(path,'r').read())

def savePickle(obj,path):

    cPickle.dump(obj,open(path,'w'))


class Evaluator(object):


    def __init__(self,dataset,listOfExperiments):

        self.dataset=dataset
        self.listOfExperiments=listOfExperiments

    @staticmethod
    def createPlotData(centerDistance,maxValue=50,n=100):


        x=np.linspace(0,maxValue,num=n);

        y=np.zeros(n)

        for idx in range(0,n):

            # find percentage of centerDistance<= x[idx

            y[idx]=len(np.nonzero(centerDistance<=x[idx])[0])/(centerDistance.shape[0]*1.0)

        return (x,y)


    def createHistogramPlot(self, x_s, y_s,x_pr,y_pr,trackerNames,savefilename=''):

        precision=list()
        success  =list()

        n_groups=len(x_pr)
        names=list()
        plt.figure()
        for i in range(0,n_groups):

            p=np.trapz(y_pr[i],x=x_pr[i])/50
            s=np.trapz(y_s[i],x=x_s[i])

            precision.append(p)
            success.append(s)

            names.append(self.listOfExperiments[i].trackerLabel)

        plt.subplot(1,2,1)
        plt.subplots_adjust(bottom=0.2)
        #plt.xlim([0,1.1])
        index = np.arange(n_groups)

        idx_success= [i[0] for i in sorted(enumerate(success), key=lambda x: x[1])]

        successTrackerNames=[trackerNames[x] for x in idx_success ]
        sorted_success=[success[x] for x in idx_success]

        plt.xticks(index, successTrackerNames, rotation=45)
        plt.bar(index, sorted_success, align = "center")
        plt.ylim((0,1))
        plt.title("Success")
        plt.subplot(1,2,2)

        # NOTE: BOTH ARE SORTED ACCORDING TO SUCCESS


        precisionTrackerNames = [trackerNames[x] for x in idx_success]
        sorted_precision = [success[x] for x in idx_success]


        plt.bar(index, sorted_precision, align="center")
        plt.xticks(index, precisionTrackerNames, rotation=45)
        plt.ylim((0, 1))

        plt.title("Precision")

        if savefilename == '':
            plt.show()
        else:
            plt.savefig(savefilename)


    def createPlot(self, x_s, y_s,x_pr,y_pr,savefilename=''):

        plt.figure()
        cm = plt.get_cmap('gist_rainbow')
        NUM_COLORS=len(x_pr)

        headerFontSize=14;
        axisFontSize=12;
        lineWidth=1.8;

        legendSize=9;

        with plt.style.context('grayscale'):

            handlesLegendPrecision = list()
            handlesLegendSuccess = list()
            for i in range(0, len(x_s)):
                p = np.trapz(y_pr[i], x=x_pr[i]) / 50
                s = np.trapz(y_s[i], x=x_s[i])

                p=np.ma.round(p,2)
                s=np.ma.round(s,2)

                color = cm(1. * i / NUM_COLORS)
                red_patch = mpatches.Patch(label=self.listOfExperiments[i].trackerLabel + ' ['+str(p)+']', color=color)
                blue_path = mpatches.Patch(label=self.listOfExperiments[i].trackerLabel + ' ['+str(s)+']', color=color)
                handlesLegendPrecision.append(red_patch)
                handlesLegendSuccess.append(blue_path)
                print self.listOfExperiments[i].trackerLabel


            plt.subplot(1, 2, 1)

            for i in range(0, len(x_s)):
                plt.plot(x_s[i], y_s[i], linewidth = lineWidth, color=cm(1. * i / NUM_COLORS))
            plt.title('success', fontsize=headerFontSize)

            plt.ylim([0, 1.1])
            plt.xlim([-0.02, 1.1])
            plt.xlabel('Overlap threshold', fontsize=axisFontSize)
            plt.ylabel('Success rate', fontsize=axisFontSize)

            plt.legend(handles=handlesLegendSuccess, prop={'size': legendSize})
            plt.grid(b=False)
            plt.subplot(1, 2, 2)

            for i in range(0,len(x_pr)):
                plt.plot(x_pr[i],y_pr[i], linewidth=lineWidth,color=cm(1.*i/NUM_COLORS))
            plt.ylim([0,1.1])
            plt.xlim([-0.5,51])
            plt.title("precision", fontsize=headerFontSize)
            plt.grid(b=False)
            plt.xlabel('Location error threshold', fontsize=axisFontSize)
            plt.ylabel('Precision', fontsize=axisFontSize)



            plt.legend(handles=handlesLegendPrecision,prop={'size': legendSize}, loc=2)


        if savefilename=='':
            plt.show()
        else:
            plt.savefig(savefilename)

    @staticmethod
    def evaluateSingleVideo(video,gt,n=1000):
        '''
        Evaluate single video tracker run
        :param video:   video data
        :param gt:      ground truth data
        :param n:       number of points to sample
        :return:        (x_pr,y_pr,x_s,y_s) list
        '''

        findCenter = lambda x: np.array([x[0] + x[2] / 2.0, x[1] + x[3] / 2.0])

        distCenter = lambda x, y: np.linalg.norm(findCenter(x) - findCenter(y))

        get4D = lambda x: np.array([x[0], x[1], x[0] + x[2], x[1] + x[3]])
        intersection = lambda x, y: max(min(x[2], y[2]) - max(x[0], y[0]), 0) * max(min(x[3], y[3]) - max(x[1], y[1]),
                                                                                    0)

        area = lambda x: (x[3] - x[1]) * (x[2] - x[0])

        distJaccard = lambda x, y: (intersection(x, y) / (area(x) + area(y) - intersection(x, y)))

        distJarrardFull = lambda x, y: distJaccard(get4D(x), get4D(y))

        boxes = video[1]

        boxes_gt = gt[1]

        nFrames = min(boxes.shape[0], boxes_gt.shape[0]);

        centerDistance = np.zeros((nFrames, 1))
        overlap_over_union = np.zeros((nFrames, 1))

        for idx in range(0, nFrames):
            # calculate different statistics: overlap over union and euclidean distance of centers

            overlap_over_union[idx] = distJarrardFull(boxes[idx], boxes_gt[idx])
            centerDistance[idx] = distCenter((boxes[idx]), (boxes_gt[idx]))

        (x_pr, y_pr) = Evaluator.createPlotData(centerDistance, maxValue=50, n=n)
        (x_s, y_s) = Evaluator.createPlotData(overlap_over_union, maxValue=1, n=n)

        # complement success plot curve
        y_s = 1 - y_s;

        return (x_pr,y_pr,x_s,y_s)

    def evaluateSingleTracker(self, listRun,n=1000):

        listGT = self.dataset.data


        runs = listRun.data

        precision_x = np.zeros(n)
        precision_y = np.zeros(n)

        success_x = np.zeros(n)
        success_y = np.zeros(n)

        for video, gt in zip(runs, listGT):
            (x_pr, y_pr, x_s, y_s)= Evaluator.evaluateSingleVideo(video, gt, n=n)

            precision_x = precision_x + x_pr
            precision_y = precision_y + y_pr

            success_x = success_x + x_s
            success_y = success_y + y_s


        precision_x = precision_x / len(runs)
        precision_y = precision_y / len(runs)

        success_x = success_x / len(runs)
        success_y = success_y / len(runs)

        return (precision_x,precision_y,success_x,success_y)

    def evaluate(self,n=1000,successAndPrecisionPlotName='',histogramPlot=''):

        '''

        Evaluate the dataset

        :return: accuracy and precision
        '''

        listGT=self.dataset.data


        pr_x_list=list()
        pr_y_list=list()

        sc_x_list=list()
        sc_y_list=list();

        experimentNames=list()

        for listRun in self.listOfExperiments:

            runs=listRun.data
            experimentNames.append(listRun.trackerLabel)

            (precision_x, precision_y, success_x, success_y)= self.evaluateSingleTracker(listRun,n)


            pr_x_list.append(precision_x)
            pr_y_list.append(precision_y)

            sc_x_list.append(success_x)
            sc_y_list.append(success_y)


        # REWRITE THIS FUNCTION: SUCCESS plots are not generated properly


        self.createPlot(sc_x_list, sc_y_list,pr_x_list,pr_y_list,savefilename=successAndPrecisionPlotName)


        # get some real data and finish this plot
        self.createHistogramPlot(sc_x_list, sc_y_list,pr_x_list,pr_y_list,trackerNames=experimentNames,savefilename=histogramPlot)







if __name__ == "__main__":
    wu2013results="/Users/Ivan/Files/Results/Tracking/wu2013"
    wu2013GroundTruth="/Users/Ivan/Files/Data/Tracking_benchmark"

    vot2014Results="/Users/Ivan/Files/Results/Tracking/vot2014"
    vot2014GrounTruth="/Users/Ivan/Files/Data/vot2014"

    datasetType='wu2013'
    # Note: in wu2013 i

    # trackerLabel="STR+f_hog"

    #
    # run=Experiment(wu2013results,datasetType,trackerLabel)
    # run.loadResults()


    # picklePath='./Runs/'+trackerLabel+'.p'
    # #
    # # savePickle(a,picklePath)
    # #
    # run=loadPickle(picklePath)
    #
    #
    dataset=Dataset(wu2013GroundTruth,datasetType)


    runsNames=glob.glob('./Runs/*.p')

    runs=list()

    for runName in runsNames:
        run=loadPickle(runName)

        runs.append(run)

    evaluator=Evaluator(dataset,runs)

    saveFigureToFolder='/Users/Ivan/Code/personal-website/Projects/Object_aware_tracking/images/fixedScale/'
    saveFormat=['png','pdf']

    successAndPrecision='SuccessAndPrecision_wu2013'
    histograms='histogram_wu2013'

    # for i in saveFormat:
    #     evaluator.evaluate(successAndPrecisionPlotName=saveFigureToFolder+successAndPrecision+'.'+
    #                                                    i,histogramPlot=saveFigureToFolder+histograms+'.'+
    #                                                                                i)

    evaluator.evaluate()
