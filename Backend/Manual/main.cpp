#include <pistache/endpoint.h>
#include <pistache/http.h>
#include <pistache/router.h>
#include <iostream>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <nlohmann/json.hpp>
#include <filesystem>

using namespace Pistache;
using json = nlohmann::json;

const std::string image_dir = "/home/aahil/edhithaGCS/src/assets/DispImages"; // Replace with your image directory

class ImageHandler
{
public:
    ImageHandler(Address addr)
        : httpEndpoint(std::make_shared<Http::Endpoint>(addr)) {}

    void init(size_t threads = 1)
    {
        auto opts = Http::Endpoint::options()
                        .threads(static_cast<int>(threads));
        httpEndpoint->init(opts);
        setupRoutes();
    }

    void start()
    {
        httpEndpoint->setHandler(router.handler());
        httpEndpoint->serve();
    }

    void shutdown()
    {
        httpEndpoint->shutdown();
    }

private:
    void setupRoutes()
    {
        using namespace Rest;
        Routes::Get(router, "/all-images", Routes::bind(&ImageHandler::listAllImages, this));
        Routes::Get(router, "/images/:filename", Routes::bind(&ImageHandler::serveImage, this));
        Routes::Post(router, "/crop-image", Routes::bind(&ImageHandler::cropImage, this));
    }

    void listAllImages(const Rest::Request &request, Http::ResponseWriter response)
    {
        std::vector<std::string> imageUrls;
        for (const auto &entry : std::filesystem::directory_iterator(image_dir))
        {
            if (entry.is_regular_file())
            {
                imageUrls.push_back(entry.path().filename().string());
            }
        }
        json responseJson = {{"imageUrls", imageUrls}};
        response.headers().add<Http::Header::ContentType>("application/json");
        response.send(Http::Code::Ok, responseJson.dump());
    }

    void serveImage(const Rest::Request &request, Http::ResponseWriter response)
    {
        auto filename = request.param(":filename").as<std::string>();
        std::string image_path = image_dir + "/" + filename;

        if (!std::filesystem::exists(image_path))
        {
            response.send(Http::Code::Not_Found, "Image not found");
            return;
        }

        std::ifstream image_file(image_path, std::ios::binary);
        if (!image_file.is_open())
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to open image");
            return;
        }

        image_file.seekg(0, std::ios::end);
        size_t image_size = image_file.tellg();
        image_file.seekg(0, std::ios::beg);

        std::string content_type = "image/";
        if (filename.find(".jpg") != std::string::npos)
        {
            content_type += "jpeg";
        }
        else if (filename.find(".png") != std::string::npos)
        {
            content_type += "png";
        }
        else
        {
            response.send(Http::Code::Bad_Request, "Unsupported image format");
            return;
        }

        response.headers().add<Http::Header::ContentType>(content_type);
        response.headers().add<Http::Header::ContentLength>(image_size);
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*"); // Add CORS header
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET");

        std::stringstream buffer;
        buffer << image_file.rdbuf();
        response.send(Http::Code::Ok, buffer.str());
    }

    void cropImage(const Rest::Request &request, Http::ResponseWriter response)
    {
        auto data = json::parse(request.body());
        std::string imageUrl = data["imageUrl"];
        int clickX = data["clickX"];
        int clickY = data["clickY"];

        std::string imagePath = image_dir + "/" + imageUrl;

        cv::Mat image = cv::imread(imagePath, cv::IMREAD_UNCHANGED);
        if (image.empty())
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to open image");
            return;
        }

        int cropWidth = 200;
        int cropHeight = 200;
        int startX = std::max(0, clickX - cropWidth / 2);
        int startY = std::max(0, clickY - cropHeight / 2);
        int endX = std::min(image.cols, startX + cropWidth);
        int endY = std::min(image.rows, startY + cropHeight);

        cv::Rect cropRegion(startX, startY, endX - startX, endY - startY);
        cv::Mat croppedImage = image(cropRegion);

        std::string croppedImagePath = "/home/aahil/edhithaGCS/src/assets/CroppedImages" + imageUrl.substr(0, imageUrl.find_last_of(".")) + "_cropped.png";
        if (!cv::imwrite(croppedImagePath, croppedImage))
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to save cropped image");
            return;
        }

        response.send(Http::Code::Ok, "Cropped image saved successfully");
    }

    std::shared_ptr<Http::Endpoint> httpEndpoint;
    Rest::Router router;
};

int main()
{
    Address addr(Ipv4::any(), Port(9080));
    ImageHandler imageHandler(addr);

    imageHandler.init();
    imageHandler.start();
    imageHandler.shutdown();

    return 0;
}
