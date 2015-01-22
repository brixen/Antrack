//
//  ApproximateKernel.h
//  Robust_tracking_by_detection
//
//  Created by Ivan Bogun on 12/18/14.
//
//

#ifndef __Robust_tracking_by_detection__ApproximateKernel__
#define __Robust_tracking_by_detection__ApproximateKernel__

#include <stdio.h>
#include "Kernel.h"
#include "AdditiveKernel.h"
#include "IntersectionKernel_fast.h"
#include "IntersectionKernel.h"
#include "armadillo"
#include "Spline.h"
class ApproximateKernel: public Kernel{
    
    IntersectionKernel* intKernelFast=new IntersectionKernel;
    int nPts;
    
    std::vector<Spline> splines;
    
public:
    ApproximateKernel(int nPts_){ nPts=nPts_;};
    
    void preprocess(std::vector<supportData*>& S, int K);
    void preprocessMatrices(arma::mat& X, arma::colvec& beta);

    double calculate(arma::mat& x,int r1,arma::mat& x2,int r2){
        return intKernelFast->calculate(x, r1, x2, r2);
    };
    
    
    
    
    double predictOne(arma::rowvec& x);
    arma::rowvec predictAll(arma::mat& newX,std::vector<supportData*>& S, int K);
    
};

#endif /* defined(__Robust_tracking_by_detection__ApproximateKernel__) */