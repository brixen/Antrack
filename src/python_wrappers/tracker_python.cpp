
#include "../../src/Tracker/Struck.h"
#include <iostream>
#include <opencv2/opencv.hpp>
#include "armadillo"
#include <vector>
#include <boost/python.hpp>

#include "../../src/Tracker/OLaRank_old.h"
#include "../../src/Tracker/LocationSampler.h"
#include "../../src/Features/Histogram.h"
#include "../../src/Filter/KalmanFilterGenerator.h"
#include "../../src/Kernels/IntersectionKernel_fast.h"

class Antrack {

public:
    Struck* tracker;


  boost::python::list track(std::string filename){

      boost::python::list output;
      cv::Rect r = this->tracker->track(filename);

      output.append(r.x);
      output.append(r.y);
      output.append(r.width);
      output.append(r.height);
        return output;
  }

  void initialize(std::string filename, int x, int y, int width, int height){

      this->tracker->initialize(filename,x,y,width,height);
  }

  void initializeTracker(){
      // Parameters
      // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      params p;
      p.C = 100;
      p.n_O = 10;
      p.n_R = 10;
      int nRadial = 5;
      int nAngular = 16;
      int B = 100;

      int nRadial_search = 12;
      int nAngular_search = 30;

      // RawFeatures* features=new RawFeatures(16);


      Feature *features;
      Kernel *kernel;
      std::string featureSTR = "hist";
      std::string kernelSTR = "int";
      features = new HistogramFeatures(4, 16);

      kernel = new IntersectionKernel_fast;

      //    MultiFeature* features=new MultiFeature(fs);

      int verbose = 0;
      int display = 0;
      int m = features->calculateFeatureDimension();

      OLaRank_old *olarank = new OLaRank_old(kernel);
      olarank->setParameters(p, B, m, verbose);

      int r_search = 45;
      int r_update = 60;

      bool useObjectness = false;


      // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

      LocationSampler *samplerForUpdate =
              new LocationSampler(r_update, nRadial, nAngular);
      LocationSampler *samplerForSearch =
              new LocationSampler(r_search, nRadial_search, nAngular_search);

      this->tracker = new Struck(olarank, features, samplerForSearch, samplerForUpdate,
                     false, false, true, false, false);


      int measurementSize = 6;
      arma::colvec x_k(measurementSize, fill::zeros);
      x_k(0) = 0;
      x_k(1) = 0;
      x_k(2) = 0;
      x_k(3) = 0;

      int robustConstant_b = 10;

      int R_cov = 5;
      int Q_cov = 5;
      int P = 3;

      KalmanFilter_my filter =
              KalmanFilterGenerator::generateConstantVelocityFilter(
                      x_k, 0, 0, R_cov, Q_cov, P, robustConstant_b);

      this->tracker->setFilter(filter);

      this->tracker->setNote("");
  }

  void initializeTrackerWithParameters(std::string featureSTR,
                                       std::string kernelSTR,
                                       int C,
                                       int n_O,
                                       int n_R,
                                       int nRadial,
                                       int nAngular,
                                       int B,
                                       int nRadial_search,
                                       int nAngular_search,
                                       int L,
                                       int bins,
                                       int r_search,
                                       int r_update,
                                       bool useObjectness,
                                       int robustConstant_b,
                                       int R_cov,
                                       int Q_cov,
                                       int P,
                                       int display) {

    // Parameters
      // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      params p;
      p.C = C;
      p.n_O = n_O;
      p.n_R = n_R;

      Feature *features;
      Kernel *kernel;

      features = new HistogramFeatures(L, bins);

      kernel = new IntersectionKernel_fast;

      int verbose = 0;

      int m = features->calculateFeatureDimension();

      OLaRank_old *olarank = new OLaRank_old(kernel);
      olarank->setParameters(p, B, m, verbose);

      // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

      LocationSampler *samplerForUpdate =
              new LocationSampler(r_update, nRadial, nAngular);
      LocationSampler *samplerForSearch =
              new LocationSampler(r_search, nRadial_search, nAngular_search);

      this->tracker = new Struck(olarank, features, samplerForSearch, samplerForUpdate,
                     false, false, true, false, false);


      int measurementSize = 6;
      arma::colvec x_k(measurementSize, fill::zeros);
      x_k(0) = 0;
      x_k(1) = 0;
      x_k(2) = 0;
      x_k(3) = 0;


      KalmanFilter_my filter =
              KalmanFilterGenerator::generateConstantVelocityFilter(
                      x_k, 0, 0, R_cov, Q_cov, P, robustConstant_b);

      this->tracker->setFilter(filter);

      this->tracker->setNote("");

  }

~Antrack(){
    delete tracker;
}

};


using namespace boost::python;

BOOST_PYTHON_MODULE(struck_tracker)

{
  class_<Antrack>("Antrack")
      .def("initialize",&Antrack::initialize)
    .def("initializetrackerwithparameters",
         &Antrack::initializeTrackerWithParameters)
      .def("track", &Antrack::track)
    .def("initializeTracker",&Antrack::initializeTracker)
      ;
}
// find how to write functions which return some values in c++/python boost
// framework
