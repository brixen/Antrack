

#include "SuperPixels.h"



SuperPixels::SuperPixels() {


}

UINT* SuperPixels::calculateSegmentation(cv::Mat& img_, int nSuperPixels) {
   

    IplImage* img=new IplImage(img_);
	
	int NR_SUPERPIXELS=nSuperPixels;
    if ((!img))
      {
        printf("Error while opening file\n");
        
      }

    int width = img->width;
    int height = img->height;
    int sz = height*width;


    UINT* ubuff = new UINT[sz];
    //UINT* ubuff2 = new UINT[sz];
    //UINT* dbuff = new UINT[sz];
    UINT pValue;
    //UINT pdValue;
    char c;
    UINT r,g,b,d;
    int idx = 0;
    for(int j=0;j<img->height;j++)
      for(int i=0;i<img->width;i++)
        {
          if(img->nChannels == 3)
            {
              // image is assumed to have data in BGR order
              b = ((uchar*)(img->imageData + img->widthStep*(j)))[(i)*img->nChannels];
              g = ((uchar*)(img->imageData + img->widthStep*(j)))[(i)*img->nChannels+1];
              r = ((uchar*)(img->imageData + img->widthStep*(j)))[(i)*img->nChannels+2];
  			if (d < 128) d = 0;
              pValue = b | (g << 8) | (r << 16);
            }
          else if(img->nChannels == 1)
            {
              c = ((uchar*)(img->imageData + img->widthStep*(j)))[(i)*img->nChannels];
              pValue = c | (c << 8) | (c << 16);
            }
          else
            {
              printf("Unknown number of channels %d\n", img->nChannels);
          
            }
          ubuff[idx] = pValue;
          //ubuff2[idx] = pValue;
          idx++;
        }




  /*******************************************
   * SEEDS SUPERPIXELS                       *
   *******************************************/
  int NR_BINS = 5; // Number of bins in each histogram channel

  //printf("Generating SEEDS with %d superpixels\n", NR_SUPERPIXELS);
  SEEDS seeds(width, height, 3, NR_BINS);

  // SEEDS INITIALIZE
  int nr_superpixels = NR_SUPERPIXELS;

  // NOTE: the following values are defined for images from the BSD300 or BSD500 data set.
  // If the input image size differs from 480x320, the following values might no longer be
  // accurate.
  // For more info on how to select the superpixel sizes, please refer to README.TXT.
  int seed_width = 3; int seed_height = 4; int nr_levels = 4;
  if (width >= height)
  {
  	if (nr_superpixels == 600) {seed_width = 2; seed_height = 2; nr_levels = 4;}
  	if (nr_superpixels == 400) {seed_width = 3; seed_height = 2; nr_levels = 4;}
  	if (nr_superpixels == 266) {seed_width = 3; seed_height = 3; nr_levels = 4;}
  	if (nr_superpixels == 200) {seed_width = 3; seed_height = 4; nr_levels = 4;}
  	if (nr_superpixels == 150) {seed_width = 2; seed_height = 2; nr_levels = 5;}
  	if (nr_superpixels == 100) {seed_width = 3; seed_height = 2; nr_levels = 5;}
  	if (nr_superpixels == 50)  {seed_width = 3; seed_height = 4; nr_levels = 5;}
  	if (nr_superpixels == 25)  {seed_width = 3; seed_height = 2; nr_levels = 6;}
  	if (nr_superpixels == 17)  {seed_width = 3; seed_height = 3; nr_levels = 6;}
  	if (nr_superpixels == 12)  {seed_width = 3; seed_height = 4; nr_levels = 6;}
  	if (nr_superpixels == 9)  {seed_width = 2; seed_height = 2; nr_levels = 7;}
  	if (nr_superpixels == 6)  {seed_width = 3; seed_height = 2; nr_levels = 7;}
  }
  else
  {
  	if (nr_superpixels == 600) {seed_width = 2; seed_height = 2; nr_levels = 4;}
  	if (nr_superpixels == 400) {seed_width = 2; seed_height = 3; nr_levels = 4;}
  	if (nr_superpixels == 266) {seed_width = 3; seed_height = 3; nr_levels = 4;}
  	if (nr_superpixels == 200) {seed_width = 4; seed_height = 3; nr_levels = 4;}
  	if (nr_superpixels == 150) {seed_width = 2; seed_height = 2; nr_levels = 5;}
  	if (nr_superpixels == 100) {seed_width = 2; seed_height = 3; nr_levels = 5;}
  	if (nr_superpixels == 50)  {seed_width = 4; seed_height = 3; nr_levels = 5;}
  	if (nr_superpixels == 25)  {seed_width = 2; seed_height = 3; nr_levels = 6;}
  	if (nr_superpixels == 17)  {seed_width = 3; seed_height = 3; nr_levels = 6;}
  	if (nr_superpixels == 12)  {seed_width = 4; seed_height = 3; nr_levels = 6;}
  	if (nr_superpixels == 9)  {seed_width = 2; seed_height = 2; nr_levels = 7;}
  	if (nr_superpixels == 6)  {seed_width = 2; seed_height = 3; nr_levels = 7;}
  }

  seeds.initialize(seed_width, seed_height, nr_levels);



  //clock_t begin = clock();

  seeds.update_image_ycbcr(ubuff);

  seeds.iterate();

  //clock_t end = clock();
  //double elapsed_secs = double(end - begin) / CLOCKS_PER_SEC;
  //printf("    elapsed time=%lf sec\n", elapsed_secs);

  //printf("SEEDS produced %d labels\n", seeds.count_superpixels());
  
  //seeds.DrawContoursAroundSegments(ubuff, seeds.labels[nr_levels-1], width, height, 0xff0000, false);//0xff0000 draws red contours


 
  //std::string imageFileName = "./test_labels.png";
  //printf("Saving image %s\n",imageFileName.c_str());
  //seeds.SaveImage(ubuff, width, height,imageFileName.c_str());

  // DRAW SEEDS OUTPUT
  return seeds.get_labels();
  	// sz = 3*width*height;
  	//
  	//     UINT* output_buff = new UINT[sz];
  	//     for (int i = 0; i<sz; i++) output_buff[i] = 0;
  	//
  	//
  	//     //printf("Draw Contours Around Segments\n");
  	//     DrawContoursAroundSegments(ubuff, seeds.labels[nr_levels-1], width, height, 0xff0000, false);//0xff0000 draws red contours
  	//     DrawContoursAroundSegments(output_buff, seeds.labels[nr_levels-1], width, height, 0xffffff, true);//0xff0000 draws white contours
  	//
  	//    	std::string imageFileName="";
  	//     imageFileName = "./test_labels.png";
  	//     //printf("Saving image %s\n",imageFileName.c_str());
  	//     SaveImage(ubuff, width, height,
  	//               imageFileName.c_str());
  	//
  	//        imageFileName = "./test_boundary.png";
  	//     //printf("Saving image %s\n",imageFileName.c_str());
  	//     SaveImage(output_buff, width, height,
  	//               imageFileName.c_str());
  	//
  	//
  	//     std::string labelFileNameTxt = "./test_.seg";
  	//     seeds.SaveLabels_Text(labelFileNameTxt);
  	//
  	//
  	//
  	//     delete[] ubuff;
  	//     delete[] output_buff;
}


arma::mat SuperPixels::calculateSegmentation_armamat(cv::Mat &image, int nSuperpixels){
    
    UINT* labels=calculateSegmentation(image,nSuperpixels);
    
    
    arma::mat Label(image.cols,image.rows,arma::fill::zeros);
    for (int x=0; x<image.cols;x++) {
        
        for (int y=0; y<image.rows; y++) {
            //std::cout<<labels[y*image.cols+x]<<std::endl;//[y * width + x]
            Label(x,y)=labels[y*image.cols+x];
        }
        
    }
    
    return Label;
}




// void SuperPixels::DrawContoursAroundSegments_mat(cv::Mat img, UINT *labels, const int &width, const int &height, const UINT &color, bool internal) {
//
//     const int dx8[8] = {-1, -1,  0,  1, 1, 1, 0, -1};
//     const int dy8[8] = { 0, -1, -1, -1, 0, 1, 1,  1};
//
//     int sz = width*height;
//
//     vector<bool> istaken(sz, false);
//
//     int mainindex(0);
//     int cind(0);
//     for( int j = 0; j < height; j++ )
//     {
//         for( int k = 0; k < width; k++ )
//         {
//             int np(0);
//             for( int i = 0; i < 8; i++ )
//             {
//                 int x = k + dx8[i];
//                 int y = j + dy8[i];
//
//                 if( (x >= 0 && x < width) && (y >= 0 && y < height) )
//                 {
//                     int index = y*width + x;
//
//                     if (internal)
//                     {
//                         {
//                             if( labels[mainindex] != labels[index] ) np++;
//                         }
//                     } else {
//                         if( false == istaken[index] )//comment this to obtain internal contours
//                         {
//                             if( labels[mainindex] != labels[index] ) np++;
//                         }
//                     }
//                 }
//             }
//             if( np > 1 )
//             {
//                 istaken[mainindex] = true;
//                 //img[mainindex] = color;
//                 img.at<uchar>(j,k)=color;
//                 cind++;
//             }
//             mainindex++;
//         }
//     }
// }
//
//
// cv::Mat SuperPixels::getBoundary() {
//     // output buff
//     cv::Mat boundary(imgWidth,imgHeight,CV_8U);
//     DrawContoursAroundSegments_mat(boundary,
//             seeds->labels[nr_levels-1], imgWidth, imgHeight,
//             0xffffff, true);
//
//     return  boundary;
//
// }
//
//
// cv::Mat SuperPixels::getLabels() {
//     cv::Mat segLabels(imgWidth,imgHeight,CV_8U);
//     DrawContoursAroundSegments_mat(segLabels,
//             seeds->labels[nr_levels-1], imgWidth, imgHeight,
//             0xff0000, false);
//
//     return  segLabels;
//
// }
//
//
// cv::Mat SuperPixels::getSegmentation() {
//     cv::Mat segmentation(imgWidth,imgHeight,CV_8U);
//
//     int i=0;
//     for( int h = 0; h < imgHeight; h++ )
//     {
//         for( int w = 0; w < imgWidth ; w++ )
//         {
//             segmentation.at<uchar>(h, w)=seeds->labels[seeds_top_level][i];
//             i++;
//         }
//     }
//
//     return segmentation;
// }