#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

using namespace cv;

int main()
{
    Mat img = imread("/home/aahil/edhithaGCS/src/assets/DispImages/z0.jpg");
    namedWindow("image", WINDOW_AUTOSIZE);
    Rect roi;
    roi = selectROI("image", img);
    imshow("ROI", img(roi));
    waitKey(0);
    return 0;
}